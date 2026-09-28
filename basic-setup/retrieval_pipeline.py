import os
import re
import json
import csv
from pathlib import Path
from collections import OrderedDict
from typing import Optional, Tuple, List, Dict, Any

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    BM25Okapi = None

load_dotenv()


class AgriRAGSystem:
    """
    Optimized Agriculture RAG System:
    - In-memory O(1) QA index & BM25 sparse index (instant response for thousands of common questions)
    - Single-pass dense vector search with Chroma (eliminates redundant embeddings)
    - Fixed cosine distance confidence metric (properly identifies exact & high-similarity matches)
    - Hybrid retrieval: BM25 keyword matching + Dense vector search
    - LRU query cache with normalized keys (avoids re-running identical or near-identical queries)
    - Clean source citation formatting
    - Graceful error handling for OpenRouter API rate limits
    """

    def __init__(self, persist_directory: str = "chroma_db"):
        self.persist_directory = persist_directory

        # 1. Initialize local embeddings
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        # 2. Load vector store
        self.db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_model,
            collection_metadata={"hnsw:space": "cosine"},
        )

        # 3. Initialize OpenRouter configuration with multi-model failover
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.primary_model = os.getenv("OPENROUTER_MODEL", "qwen/qwen3.8-27b:free")
        fallback_str = os.getenv(
            "OPENROUTER_FALLBACK_MODELS",
            "nvidia/nemotron-3-super-120b-a12b:free,nvidia/nemotron-3.5-lightning:free",
        )
        fallbacks = [m.strip() for m in fallback_str.split(",") if m.strip()]
        self.models_pool = list(dict.fromkeys([self.primary_model] + fallbacks))

        if not self.openrouter_api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not found in environment variables. "
                "Please set it in your .env file."
            )

        print(f"OpenRouter Model Pool: {self.models_pool}")

        # 4. In-memory LRU cache (capped at 500 entries)
        self._cache = OrderedDict()
        self._max_cache_size = 500
        self._max_ctx_chars = 1000

        # 5. Build in-memory QA map and BM25 index from files/
        self._exact_qa: Dict[str, Dict[str, str]] = {}
        self.bm25: Optional[BM25Okapi] = None
        self.bm25_records: List[Dict[str, str]] = []
        self._build_in_memory_indexes()

    @staticmethod
    def _normalize_key(text: str) -> str:
        """Strip punctuation and lowercase for normalized cache/lookup keys."""
        return re.sub(r"[^\w\s]", "", text.strip().lower())

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Simple, fast tokenizer for BM25 keyword matching."""
        return [w for w in re.findall(r"\b\w+\b", text.lower()) if len(w) > 1]

    def _build_in_memory_indexes(self):
        """
        Loads all CSV QA pairs into memory ONCE at startup:
        - self._exact_qa: normalized_question -> {question, answer, source} for O(1) lookup
        - self.bm25: BM25Okapi index for sub-millisecond typo-tolerant keyword search
        This completely eliminates opening/scanning CSV files on disk during queries.
        """
        base = Path(__file__).resolve().parent / "files"
        if not base.exists():
            return

        corpus = []
        count = 0

        for fp in base.rglob("*.csv"):
            try:
                with open(fp, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Support multiple CSV column conventions
                        q = (
                            row.get("question")
                            or row.get("Question")
                            or row.get("Question Text")
                            or row.get("Term")
                            or ""
                        ).strip()
                        a = (
                            row.get("answer")
                            or row.get("Answer")
                            or row.get("answer_text")
                            or row.get("response")
                            or row.get("Definition")
                            or ""
                        ).strip()

                        if q and a:
                            clean_source = fp.name
                            record = {
                                "question": q,
                                "answer": a,
                                "source": clean_source,
                            }
                            # Store exact normalized question
                            norm_q = self._normalize_key(q)
                            self._exact_qa[norm_q] = record

                            # Also add alias for definition terms (e.g. "what is soil" -> Soil)
                            if row.get("Term") and not norm_q.startswith("what is"):
                                self._exact_qa[f"what is {norm_q}"] = record

                            tokens = self._tokenize(q)
                            if tokens:
                                corpus.append(tokens)
                                self.bm25_records.append(record)
                                count += 1
            except Exception as e:
                print(f"Warning: could not index {fp.name}: {e}")

        if BM25Okapi is not None and corpus:
            try:
                self.bm25 = BM25Okapi(corpus)
                print(f"Indexed {count} agricultural QA records into memory with BM25.")
            except Exception as e:
                print(f"BM25 build error: {e}")

    def is_agriculture_related(self, query: str) -> bool:
        """Check if query is agriculture/crop related."""
        agri_keywords = [
            "agri", "agriculture", "agricultural", "farm", "farmer", "farming", "cultivation",
            "cropping", "crop", "harvest", "yield", "produce", "produce market", "agribusiness",
            "wheat", "rice", "paddy", "maize", "corn", "millet", "sorghum", "barley", "oats",
            "sugarcane", "cotton", "soybean", "groundnut", "peanut", "pulses", "lentil", "chickpea",
            "mustard", "rapeseed", "canola", "potato", "tomato", "onion", "garlic", "banana",
            "mango", "citrus", "tea", "coffee", "cocoa", "pepper",
            "soil", "soil test", "ph", "ec", "electrical conductivity", "organic matter",
            "nitrogen", "phosphorus", "potassium", "npk", "micronutrient", "calcium", "magnesium",
            "soil type", "clay", "sandy", "loam", "peat", "silt", "moisture",
            "fertilizer", "manure", "compost", "biofertilizer", "lime", "gypsum", "urea", "dap",
            "pesticide", "herbicide", "insecticide", "fungicide", "rodenticide",
            "pest", "pests", "aphid", "borer", "weevil", "locust", "whitefly", "thrips", "mealybug",
            "nematode", "armyworm", "leaf miner",
            "disease", "blight", "rust", "blast", "wilt", "mosaic", "scab", "smut", "root rot",
            "irrigation", "drip", "drip irrigation", "sprinkler", "flood irrigation", "canal",
            "water management", "water table", "groundwater", "rainfall", "drought", "moisture stress",
            "weather", "climate", "temperature", "forecast", "monsoon", "frost", "hail", "humidity",
            "wind", "season", "growing season",
            "sowing", "seeding", "planting", "transplanting", "pruning", "grafting", "mulching",
            "crop rotation", "intercropping", "agroforestry", "greenhouse", "polyhouse", "hydroponics",
            "aquaponics", "organic farming", "precision farming", "conservation agriculture",
            "tractor", "plough", "plow", "tiller", "harvester", "combine", "seed drill", "sprayer",
            "labor", "labour", "wage", "wages", "salary", "employment", "migrant worker",
            "credit", "loan", "finance", "subsidy", "microcredit", "insurance", "crop insurance",
            "market", "mandi", "minimum support price", "msp", "price", "exports", "imports",
            "hectare", "acre", "kg", "kilogram", "tonne", "ton", "quintal", "acreage", "yield per hectare",
            "extension", "agriculture extension", "cooperative", "fpo", "krishi", "kisan",
            "soil health", "soil testing", "sustainable", "organic", "biodiversity",
            "seed", "variety", "hybrid", "germination", "seedling", "nursery",
            "postharvest", "storage", "grading", "sorting", "processing", "supply chain",
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in agri_keywords)

    def classify_query_type(self, query: str) -> str:
        """Classify the type of agricultural query."""
        query_lower = query.lower()
        if any(w in query_lower for w in ["disease", "pest", "infection", "damage", "blight", "rust"]):
            return "disease"
        elif any(w in query_lower for w in ["soil", "ph", "nutrient", "clay", "sandy", "loam"]):
            return "soil"
        elif any(w in query_lower for w in ["fertilizer", "npk", "urea", "dap", "manure", "compost"]):
            return "fertilizer"
        elif any(w in query_lower for w in ["weather", "rain", "temperature", "climate", "monsoon"]):
            return "weather"
        elif any(w in query_lower for w in ["wage", "labor", "worker", "salary"]):
            return "wages"
        elif any(w in query_lower for w in ["credit", "loan", "finance", "subsidy", "msp", "insurance"]):
            return "credit"
        else:
            return "general"

    def fast_lookup(self, query: str) -> Tuple[Optional[str], Optional[List[Dict[str, str]]]]:
        """
        Fast in-memory lookup (< 1ms):
        1. Exact match in pre-indexed dictionary
        2. High-confidence BM25 keyword match for typo-tolerant matching
        Returns (answer, sources) or (None, None).
        """
        norm_q = self._normalize_key(query)

        # 1. Exact match
        if norm_q in self._exact_qa:
            match = self._exact_qa[norm_q]
            sources = [{
                "source": match["source"],
                "excerpt": f"Q: {match['question'][:180]}"
            }]
            return match["answer"], sources

        # 2. BM25 keyword matching
        if self.bm25 is not None and len(self.bm25_records) > 0:
            tokens = self._tokenize(query)
            if len(tokens) >= 2:
                scores = self.bm25.get_scores(tokens)
                best_idx = int(scores.argmax())
                best_score = scores[best_idx]
                # A score >= 7.0 indicates a strong keyword alignment
                if best_score >= 7.0:
                    best_match = self.bm25_records[best_idx]
                    sources = [{
                        "source": best_match["source"],
                        "excerpt": f"Q: {best_match['question'][:180]}"
                    }]
                    return best_match["answer"], sources

        return None, None

    def vector_search(self, query: str, k: int = 3) -> List[Tuple[Any, float]]:
        """
        Single-pass similarity search returning list of (Document, cosine_distance).
        Cosine distance: 0.0 = identical, 1.0 = orthogonal.
        """
        try:
            return self.db.similarity_search_with_score(query, k=k)
        except Exception as e:
            print(f"Vector search error: {e}")
            return []

    def check_direct_answer(
        self, search_results: List[Tuple[Any, float]], threshold_dist: float = 0.35
    ) -> Tuple[Optional[str], Optional[List[Dict[str, str]]]]:
        """
        Extract direct answer if the top vector match is highly confident.
        Fixed bug: Cosine distance <= 0.35 indicates high confidence (>= 0.65 similarity).
        """
        if not search_results:
            return None, None

        best_doc, best_dist = search_results[0]

        # In cosine distance: 0.0 is perfect, <= 0.35 is confident
        is_confident = (best_dist <= threshold_dist)

        if is_confident and isinstance(best_doc.metadata, dict):
            answer = (
                best_doc.metadata.get("answer")
                or best_doc.metadata.get("Answer")
                or best_doc.metadata.get("Definition")
            )
            if answer:
                clean_src = Path(best_doc.metadata.get("source", "Unknown")).name
                sources = [{
                    "source": clean_src,
                    "excerpt": best_doc.page_content[:200] + ("..." if len(best_doc.page_content) > 200 else "")
                }]
                return answer, sources

        return None, None

    def format_rich_content(self, response: str, query_type: str, context_docs: list) -> Optional[dict]:
        """Format response with rich content cards based on query type."""
        if query_type == "wages" and context_docs:
            return {
                "type": "wages-card",
                "data": {
                    "category": "Agricultural Wages & Labor",
                    "info": "Data from census and wage surveys",
                    "sources": len(context_docs),
                },
            }
        elif query_type == "credit" and context_docs:
            return {
                "type": "credit-card",
                "data": {
                    "category": "Agriculture Credit & Schemes",
                    "info": "Government assistance and financial data",
                    "sources": len(context_docs),
                },
            }
        elif query_type == "soil":
            return {
                "type": "soil-card",
                "data": {
                    "pH": "Ideal: 6.0 - 7.5 (crop dependent)",
                    "nitrogen": "Check soil test report",
                    "phosphorus": "Balanced application recommended",
                    "potassium": "Essential for disease resistance",
                    "recommendation": "Soil testing every 2-3 years is recommended",
                },
            }
        elif query_type == "weather":
            return {
                "type": "weather-card",
                "data": {
                    "temperature": "Check local forecast",
                    "humidity": "Variable by season",
                    "rainfall": "Seasonal monitoring advised",
                    "recommendation": "Adjust irrigation schedule based on precipitation",
                },
            }
        return None

    def generate_with_fallback(self, prompt: str) -> str:
        """
        Attempts to generate response with the primary model.
        If rate-limited (429) or busy, seamlessly falls over to backup free models in the pool.
        """
        for model_name in self.models_pool:
            try:
                llm = ChatOpenAI(
                    model=model_name,
                    openai_api_key=self.openrouter_api_key,
                    openai_api_base="https://openrouter.ai/api/v1",
                    temperature=0.3,
                    max_tokens=1024,
                    default_headers={
                        "HTTP-Referer": "http://localhost:8000",
                        "X-Title": "AgriSearch Bot",
                    },
                )
                res = llm.invoke(prompt)
                text = getattr(res, "content", None) or str(res)
                if text and text.strip():
                    return text.strip()
            except Exception as e:
                err_str = str(e).lower()
                if "429" in err_str or "rate" in err_str or "temporarily" in err_str:
                    print(f"Model {model_name} is rate-limited (429). Falling over to next model...")
                    continue
                else:
                    print(f"Model {model_name} error: {e}. Trying fallback...")
                    continue

        return (
            "The AI service is currently experiencing extremely high demand across all free providers. "
            "Please wait a few seconds and try asking your question again."
        )

    def stream_with_fallback(self, prompt: str, on_chunk) -> str:
        """
        Streams response with automatic failover if the primary model returns a 429 rate limit.
        """
        for model_name in self.models_pool:
            assembled = []
            try:
                llm = ChatOpenAI(
                    model=model_name,
                    openai_api_key=self.openrouter_api_key,
                    openai_api_base="https://openrouter.ai/api/v1",
                    temperature=0.3,
                    max_tokens=1024,
                    default_headers={
                        "HTTP-Referer": "http://localhost:8000",
                        "X-Title": "AgriSearch Bot",
                    },
                )
                stream_fn = getattr(llm, "stream", None)
                if stream_fn:
                    for chunk in stream_fn(prompt):
                        text = getattr(chunk, "content", None) or (chunk.get("content") if isinstance(chunk, dict) else str(chunk))
                        if text:
                            assembled.append(text)
                            on_chunk({"text": text, "done": False})
                    res = "".join(assembled).strip()
                    if res:
                        return res
                else:
                    res_obj = llm.invoke(prompt)
                    res_text = getattr(res_obj, "content", None) or str(res_obj)
                    if res_text:
                        on_chunk({"text": res_text, "done": False})
                        return res_text.strip()
            except Exception as e:
                err_str = str(e).lower()
                if "429" in err_str or "rate" in err_str or "temporarily" in err_str:
                    print(f"Streaming: Model {model_name} rate-limited (429). Failing over...")
                    continue
                else:
                    print(f"Streaming error on {model_name}: {e}. Trying fallback...")
                    continue

        fallback_msg = "The AI service is temporarily busy. Please retry in a few seconds."
        on_chunk({"text": fallback_msg, "richContent": None, "sources": [], "done": True})
        return fallback_msg

    def _get_from_cache(self, query: str) -> Optional[dict]:
        norm_key = self._normalize_key(query)
        if norm_key in self._cache:
            # Move to end for LRU order
            self._cache.move_to_end(norm_key)
            return self._cache[norm_key]
        return None

    def _save_to_cache(self, query: str, result: dict):
        norm_key = self._normalize_key(query)
        if len(self._cache) >= self._max_cache_size:
            self._cache.popitem(last=False)  # Evict oldest
        self._cache[norm_key] = result

    def process_query(self, query: str) -> dict:
        """
        Main query processing pipeline:
        1. Fast LRU Cache check (instant)
        2. Fast In-Memory QA & BM25 check (instant, < 1ms)
        3. Single-pass Chroma Vector Search (retrieves docs & distances)
        4. Confident Direct Vector Match check
        5. LLM Synthesis using already-retrieved context
        """
        # 1. Check LRU Cache
        cached = self._get_from_cache(query)
        if cached:
            return cached

        query_type = self.classify_query_type(query)

        # 2. Fast In-Memory exact & BM25 lookup
        fast_ans, fast_sources = self.fast_lookup(query)
        if fast_ans:
            result = {
                "response": fast_ans,
                "richContent": self.format_rich_content(fast_ans, query_type, []),
                "sources": fast_sources,
            }
            self._save_to_cache(query, result)
            return result

        # 3. Single-pass vector search
        search_results = self.vector_search(query, k=3)

        # 4. Direct answer from vector match (with fixed distance metric <= 0.35)
        direct_ans, direct_sources = self.check_direct_answer(search_results, threshold_dist=0.35)
        if direct_ans:
            result = {
                "response": direct_ans,
                "richContent": self.format_rich_content(direct_ans, query_type, []),
                "sources": direct_sources,
            }
            self._save_to_cache(query, result)
            return result

        # Extract documents from search results
        context_docs = [doc for doc, _ in search_results]

        # 5. Generative fallback via OpenRouter LLM
        if context_docs:
            context_blocks = []
            for doc in context_docs[:3]:
                clean_src = Path(doc.metadata.get("source", "Unknown")).name
                context_blocks.append(f"Source: {clean_src}\n{doc.page_content[:self._max_ctx_chars]}")
            context_text = "\n\n".join(context_blocks)

            prompt = f"""You are AgriSearch Bot, an expert AI assistant specializing in agriculture and forestry intelligence.

User Query: {query}

Available Agricultural Records:
{context_text}

Instructions:
1. Answer the query clearly using the data above.
2. If data is relevant, cite specific numbers, crops, and facts.
3. If data is insufficient, supplement with general agricultural knowledge while keeping advice practical and actionable.
4. Keep answers concise, helpful, and farmer-friendly.

Answer:"""
        else:
            if not self.is_agriculture_related(query):
                return {
                    "response": (
                        "I am specifically designed to assist with agriculture, crops, soil, "
                        "weather, pest management, and forestry. Could you please ask a question "
                        "related to farming or agriculture?"
                    ),
                    "richContent": None,
                    "sources": [],
                }

            prompt = f"""You are AgriSearch Bot, an expert AI assistant specializing in agriculture and forestry intelligence.

User Query: {query}

Instructions:
1. Provide accurate, practical agricultural guidance.
2. Keep responses actionable and farmer-friendly.
3. Mention that local conditions may vary.

Answer:"""

        response_text = self.generate_with_fallback(prompt)

        # Deduplicate sources and clean source paths
        seen_sources = set()
        sources = []
        for doc in context_docs[:3]:
            raw_src = doc.metadata.get("source", "Unknown")
            clean_src = Path(raw_src).name
            if clean_src not in seen_sources:
                seen_sources.add(clean_src)
                excerpt = doc.page_content[:180] + ("..." if len(doc.page_content) > 180 else "")
                sources.append({"source": clean_src, "excerpt": excerpt})

        rich_content = self.format_rich_content(response_text, query_type, context_docs)

        out = {
            "response": response_text,
            "richContent": rich_content,
            "sources": sources,
        }
        self._save_to_cache(query, out)
        return out

    def process_query_stream(self, query: str, on_chunk, k: int = 3):
        """
        Streaming response generator:
        Calls on_chunk({'text': ..., 'done': bool, 'richContent': ..., 'sources': ...})
        """
        # 1. Fast Cache check
        cached = self._get_from_cache(query)
        if cached:
            on_chunk({
                "text": cached["response"],
                "richContent": cached.get("richContent"),
                "sources": cached.get("sources", []),
                "done": True,
            })
            return

        query_type = self.classify_query_type(query)

        # 2. Fast In-Memory lookup
        fast_ans, fast_sources = self.fast_lookup(query)
        if fast_ans:
            rich_content = self.format_rich_content(fast_ans, query_type, [])
            out = {"response": fast_ans, "richContent": rich_content, "sources": fast_sources}
            self._save_to_cache(query, out)
            on_chunk({"text": fast_ans, "richContent": rich_content, "sources": fast_sources, "done": True})
            return

        # 3. Vector search
        search_results = self.vector_search(query, k=k)

        # 4. Confident vector match
        direct_ans, direct_sources = self.check_direct_answer(search_results, threshold_dist=0.35)
        if direct_ans:
            rich_content = self.format_rich_content(direct_ans, query_type, [])
            out = {"response": direct_ans, "richContent": rich_content, "sources": direct_sources}
            self._save_to_cache(query, out)
            on_chunk({"text": direct_ans, "richContent": rich_content, "sources": direct_sources, "done": True})
            return

        context_docs = [doc for doc, _ in search_results]

        # 5. Build prompt
        if context_docs:
            context_blocks = [
                f"Source: {Path(doc.metadata.get('source', 'Unknown')).name}\n{doc.page_content[:self._max_ctx_chars]}"
                for doc in context_docs[:3]
            ]
            prompt = f"""You are AgriSearch Bot, an expert AI assistant specializing in agriculture and forestry intelligence.

User Query: {query}

Available Agricultural Records:
{chr(10).join(context_blocks)}

Instructions:
1. Answer the query clearly using the data above.
2. If data is relevant, cite specific numbers, crops, and facts.
3. Keep answers concise, practical, and farmer-friendly.

Answer:"""
        else:
            if not self.is_agriculture_related(query):
                on_chunk({
                    "text": (
                        "I am specifically designed to assist with agriculture, crops, soil, "
                        "weather, pest management, and forestry. Could you please ask a question "
                        "related to farming or agriculture?"
                    ),
                    "richContent": None,
                    "sources": [],
                    "done": True,
                })
                return

            prompt = f"""You are AgriSearch Bot, an expert AI assistant specializing in agriculture and forestry intelligence.

User Query: {query}

Instructions:
1. Provide accurate, practical agricultural guidance.
2. Keep responses actionable and farmer-friendly.

Answer:"""

        final_text = self.stream_with_fallback(prompt, on_chunk)
        seen_sources = set()
        sources = []
        for doc in context_docs[:3]:
            clean_src = Path(doc.metadata.get("source", "Unknown")).name
            if clean_src not in seen_sources:
                seen_sources.add(clean_src)
                sources.append({
                    "source": clean_src,
                    "excerpt": doc.page_content[:180] + ("..." if len(doc.page_content) > 180 else ""),
                })

        rich_content = self.format_rich_content(final_text, query_type, context_docs)
        out = {"response": final_text, "richContent": rich_content, "sources": sources}
        self._save_to_cache(query, out)
        on_chunk({"text": final_text, "richContent": rich_content, "sources": sources, "done": True})


if __name__ == "__main__":
    rag = AgriRAGSystem()
    test_queries = [
        "what is soil?",
        "what is irrigation?",
        "what is fertilizer?",
    ]
    for q in test_queries:
        print(f"\n{'='*60}\nQuery: {q}\n{'='*60}")
        res = rag.process_query(q)
        print(f"Response: {res['response']}")
        print(f"Sources: {res['sources']}")
        print(f"RichContent: {res['richContent']}")