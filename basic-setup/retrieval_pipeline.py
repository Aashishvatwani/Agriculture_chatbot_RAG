import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
import re
import json
import csv
from pathlib import Path
import difflib
try:
    from rank_bm25 import BM25Okapi
except Exception:
    BM25Okapi = None

load_dotenv()

class AgriRAGSystem:
    def __init__(self, persist_directory="chroma_db"):
        """Initialize the Agriculture RAG system with Ollama"""
        self.persist_directory = persist_directory
        
        # Initialize embeddings with free local model
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Load vector store
        self.db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_model,
            collection_metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize Ollama model
        self.llm = ChatOllama(
            model="llama3.1",
            temperature=0.3
        )
        
        # Create retriever
        self.retriever = self.db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )

        # Simple in-memory cache to avoid repeated LLM calls for same queries
        self._cache = {}
        # Maximum characters to include from each context document when building prompt
        self._max_ctx_chars = 1000

        # Build BM25 index over local CSV questions for misspell correction / fuzzy retrieval
        self.bm25 = None
        self.bm25_qtexts = []
        self.bm25_rows = []
        if BM25Okapi is not None:
            try:
                self.build_bm25_index()
            except Exception as e:
                print(f"BM25 index build failed: {e}")
    
    def is_agriculture_related(self, query: str) -> bool:
        """Check if query is agriculture/crop related"""
        agri_keywords = [
            # general agriculture terms
            'agri', 'agriculture', 'agricultural', 'farm', 'farmer', 'farming', 'cultivation',
            'cropping', 'crop', 'harvest', 'yield', 'produce', 'produce market', 'agribusiness',
            # crops (common)
            'wheat', 'rice', 'paddy', 'maize', 'corn', 'millet', 'sorghum', 'barley', 'oats',
            'sugarcane', 'cotton', 'soybean', 'groundnut', 'peanut', 'pulses', 'lentil', 'chickpea',
            'mustard', 'rapeseed', 'canola', 'potato', 'tomato', 'onion', 'garlic', 'banana',
            'mango', 'citrus', 'tea', 'coffee', 'cocoa', 'pepper',
            # soil and nutrients
            'soil', 'soil test', 'ph', 'ec', 'electrical conductivity', 'organic matter',
            'nitrogen', 'phosphorus', 'potassium', 'npk', 'micronutrient', 'calcium', 'magnesium',
            'soil type', 'clay', 'sandy', 'loam', 'peat', 'silt', 'moisture',
            # fertilizers & amendments
            'fertilizer', 'manure', 'compost', 'biofertilizer', 'lime', 'gypsum', 'urea', 'dap',
            # pesticides & pest management
            'pesticide', 'herbicide', 'insecticide', 'fungicide', 'rodenticide',
            'pest', 'pests', 'aphid', 'borer', 'weevil', 'locust', 'whitefly', 'thrips', 'mealybug',
            'nematode', 'armyworm', 'leaf miner',
            # diseases
            'disease', 'blight', 'rust', 'blast', 'wilt', 'mosaic', 'scab', 'smut', 'root rot',
            # irrigation & water
            'irrigation', 'drip', 'drip irrigation', 'sprinkler', 'flood irrigation', 'canal',
            'water management', 'water table', 'groundwater', 'rainfall', 'drought', 'moisture stress',
            # weather & climate
            'weather', 'climate', 'temperature', 'forecast', 'monsoon', 'frost', 'hail', 'humidity',
            'wind', 'season', 'growing season',
            # practices & techniques
            'sowing', 'seeding', 'planting', 'transplanting', 'pruning', 'grafting', 'mulching',
            'crop rotation', 'intercropping', 'agroforestry', 'greenhouse', 'polyhouse', 'hydroponics',
            'aquaponics', 'organic farming', 'precision farming', 'conservation agriculture',
            # machinery & tools
            'tractor', 'plough', 'plow', 'tiller', 'harvester', 'combine', 'seed drill', 'sprayer',
            # labor, economics & finance
            'labor', 'labour', 'wage', 'wages', 'salary', 'employment', 'migrant worker',
            'credit', 'loan', 'finance', 'subsidy', 'microcredit', 'insurance', 'crop insurance',
            'market', 'mandi', 'minimum support price', 'msp', 'price', 'exports', 'imports',
            # measurement units & scales
            'hectare', 'acre', 'kg', 'kilogram', 'tonne', 'ton', 'quintal', 'acreage', 'yield per hectare',
            # institutions & extension
            'extension', 'agriculture extension', 'cooperative', 'farmer producer organization', 'fpo',
            'research station', 'krishi', 'kisan', 'agri department', 'agri ministry',
            # resources & sustainability
            'soil health', 'soil testing', 'sustainable', 'organic', 'biodiversity', 'carbon sequestration',
            'fertility', 'nutrient management',
            # common phrases and misc
            'seed', 'variety', 'hybrid', 'indigenous', 'germination', 'seedling', 'nursery',
            'postharvest', 'storage', 'grading', 'sorting', 'processing', 'supply chain',
            'export', 'import', 'market access'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in agri_keywords)
    
    def classify_query_type(self, query: str) -> str:
        """Classify the type of agricultural query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['disease', 'pest', 'infection', 'damage']):
            return 'disease'
        elif any(word in query_lower for word in ['soil', 'nutrient', 'ph', 'fertilizer']):
            return 'soil'
        elif any(word in query_lower for word in ['weather', 'rain', 'temperature', 'climate']):
            return 'weather'
        elif any(word in query_lower for word in ['wage', 'labor', 'worker', 'salary']):
            return 'wages'
        elif any(word in query_lower for word in ['credit', 'loan', 'finance', 'subsidy']):
            return 'credit'
        elif any(word in query_lower for word in ['fertilizer', 'npk', 'nutrient']):
            return 'fertilizer'
        else:
            return 'general'
    
    def retrieve_context(self, query: str):
        """Retrieve relevant documents from vector store"""
        try:
            # Prefer the lightweight document retrieval method if available
            if hasattr(self.retriever, 'get_relevant_documents'):
                return self.retriever.get_relevant_documents(query)

            # Fallback to any generic invoke call
            if hasattr(self.retriever, 'invoke'):
                return self.retriever.invoke(query)

            return []
        except Exception as e:
            print(f"Retrieval error: {e}")
            return []

    def find_direct_answer(self, query: str, k: int = 3):
        """Try to find a direct answer from the vector DB via similarity search.

        Returns a tuple (answer_text, sources) or (None, None) if no confident
        match is found.
        """
        try:
            # Use Chroma's similarity search with score if available
            if hasattr(self.db, 'similarity_search_with_score'):
                results = self.db.similarity_search_with_score(query, k=k)
                if not results:
                    return None, None

                # results is a list of (Document, score)
                best_doc, best_score = results[0]

                # Heuristic: detect whether score is cosine similarity (in -1..1)
                # or a distance (lower is better). We support both:
                if isinstance(best_score, float):
                    # If score looks like cosine similarity (<=1.0)
                    if -1.0 <= best_score <= 1.0:
                        is_confident = best_score >= 0.65
                    else:
                        # treat as distance; lower is better
                        is_confident = best_score <= 0.5
                else:
                    is_confident = False

                # If top match is confident and carries an 'answer' in metadata,
                # return it directly.
                if is_confident and best_doc and isinstance(best_doc.metadata, dict):
                    answer = best_doc.metadata.get('answer') or best_doc.metadata.get('Answer')
                    if answer:
                        sources = [{
                            'source': best_doc.metadata.get('source', 'Unknown'),
                            'excerpt': best_doc.page_content[:200] + ('...' if len(best_doc.page_content) > 200 else '')
                        }]
                        return answer, sources
                    # If metadata does not contain the answer, try to read the source
                    # CSV (if available) and find a matching question row with an answer.
                    src = best_doc.metadata.get('source') if isinstance(best_doc.metadata, dict) else None
                    if src and isinstance(src, str) and os.path.exists(src) and src.lower().endswith('.csv'):
                        try:
                            with open(src, newline='', encoding='utf-8') as f:
                                reader = csv.DictReader(f)
                                for row in reader:
                                    # match by question text (best-effort)
                                    qtext = (row.get('question') or row.get('Question') or row.get('Question Text') or '').strip()
                                    if not qtext:
                                        continue
                                    if qtext.lower() == best_doc.page_content.strip().lower() or qtext.lower() == query.strip().lower():
                                        ans = row.get('answer') or row.get('Answer') or row.get('answer_text') or row.get('response')
                                        if ans:
                                            sources = [{
                                                'source': src,
                                                'excerpt': best_doc.page_content[:200] + ('...' if len(best_doc.page_content) > 200 else '')
                                            }]
                                            return ans, sources
                        except Exception as e:
                            # ignore file read errors and continue
                            print(f"Error reading source CSV for answer lookup: {e}")

            # Fallback: use the retriever to get documents and inspect metadata
            docs = self.retriever.get_relevant_documents(query) if hasattr(self.retriever, 'get_relevant_documents') else None
            if docs:
                for doc in docs[:k]:
                    ans = doc.metadata.get('answer') if isinstance(doc.metadata, dict) else None
                    if ans:
                        # no score available here; use fuzzy ratio between query and doc text
                        try:
                            ratio = difflib.SequenceMatcher(None, query.lower(), doc.page_content.lower()).ratio()
                        except Exception:
                            ratio = 0.0
                        # threshold 0.65 is a conservative fuzzy match for short QA
                        if ratio >= 0.65:
                            sources = [{
                                'source': doc.metadata.get('source', 'Unknown'),
                                'excerpt': doc.page_content[:200] + ('...' if len(doc.page_content) > 200 else '')
                            }]
                            return ans, sources

        except Exception as e:
            print(f"Direct-answer search error: {e}")

        return None, None

    def csv_lookup_answer(self, query: str):
        """Scan local CSV files under `files/` for an exact question match and return its answer.

        Returns (answer, sources) or (None, None).
        """
        try:
            base = Path(__file__).resolve().parent / 'files'
            if not base.exists():
                return None, None

            qnorm = query.strip().lower()
            # Try BM25 first (good for misspellings and term variants)
            if self.bm25 is not None:
                try:
                    bm_ans = self.bm25_lookup(query)
                    if bm_ans:
                        return bm_ans
                except Exception:
                    pass
            best_match = None
            best_ratio = 0.0
            best_source = None
            FUZZY_THRESHOLD = 0.72
            for fp in base.rglob('*.csv'):
                try:
                    with open(fp, newline='', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            qtext = (row.get('question') or row.get('Question') or row.get('Question Text') or '').strip()
                            if not qtext:
                                continue
                            if qtext.lower() == qnorm:
                                ans = row.get('answer') or row.get('Answer') or row.get('answer_text') or row.get('response')
                                if ans and str(ans).strip():
                                    sources = [{
                                        'source': str(fp),
                                        'excerpt': qtext[:200] + ('...' if len(qtext) > 200 else '')
                                    }]
                                    return ans, sources
                            # track fuzzy best candidate
                            try:
                                ratio = difflib.SequenceMatcher(None, qnorm, qtext.lower()).ratio()
                                if ratio > best_ratio:
                                    best_ratio = ratio
                                    best_match = (row, qtext)
                                    best_source = fp
                            except Exception:
                                pass
                except Exception:
                    # ignore malformed CSVs and continue
                    continue
            # If no exact match, consider the best fuzzy candidate
            if best_match and best_ratio >= FUZZY_THRESHOLD:
                row, qtext = best_match
                ans = row.get('answer') or row.get('Answer') or row.get('answer_text') or row.get('response')
                if ans and str(ans).strip():
                    sources = [{
                        'source': str(best_source),
                        'excerpt': qtext[:200] + ('...' if len(qtext) > 200 else '')
                    }]
                    return ans, sources
        except Exception as e:
            print(f"CSV lookup error: {e}")

        return None, None
    
    def format_rich_content(self, response: str, query_type: str, context_docs: list):
        """Format response with rich content based on query type"""
        rich_content = None
        
        if query_type == 'wages' and context_docs:
            # Try to extract wage data
            try:
                # Parse wage information from context
                rich_content = {
                    'type': 'wages-card',
                    'data': {
                        'category': 'Agricultural Wages',
                        'info': 'Data from census and wage surveys',
                        'sources': len(context_docs)
                    }
                }
            except:
                pass
        
        elif query_type == 'credit' and context_docs:
            rich_content = {
                'type': 'credit-card',
                'data': {
                    'category': 'Agriculture Credit Flow',
                    'info': 'Financial assistance data',
                    'sources': len(context_docs)
                }
            }
        
        elif query_type == 'soil':
            rich_content = {
                'type': 'soil-card',
                'data': {
                    'pH': 'Varies by region',
                    'nitrogen': 'Consult local data',
                    'phosphorus': 'Consult local data',
                    'potassium': 'Consult local data',
                    'recommendation': 'Soil testing recommended'
                }
            }
        
        elif query_type == 'weather':
            rich_content = {
                'type': 'weather-card',
                'data': {
                    'temperature': 'Check local forecast',
                    'humidity': 'Variable',
                    'rainfall': 'Seasonal',
                    'recommendation': 'Monitor weather patterns'
                }
            }
        
        return rich_content
    
    def process_query(self, query: str) -> dict:
        """
        Main query processing pipeline:
        1. Retrieve relevant CSV data from vector store
        2. Use Ollama to augment/refine response if needed
        3. Format response with rich content
        """
        
        # Check cache first
        if query in self._cache:
            return self._cache[query]

        # Classify query
        query_type = self.classify_query_type(query)

        # First, try to find a direct answer from our QA vectors (fast path)
        direct_answer, direct_sources = self.find_direct_answer(query, k=3)
        if direct_answer:
            return {
                "response": direct_answer,
                "richContent": None,
                "sources": direct_sources
            }

        # If no vector-based direct answer was found, do a CSV-wide exact lookup
        # across the local `files/` folder for an exact question match (case-insensitive).
        csv_answer, csv_sources = self.csv_lookup_answer(query)
        if csv_answer:
            return {
                "response": csv_answer,
                "richContent": None,
                "sources": csv_sources
            }

        # Retrieve context from vector store for generative fallback
        context_docs = self.retrieve_context(query) or []
        
        # Build prompt based on available context
        if context_docs and len(context_docs) > 0:
            # Use CSV data as primary source
            # Limit number of docs and truncate their content to keep prompt small
            docs_to_use = context_docs[:3]
            context_text = "\n\n".join([
                f"Source: {doc.metadata.get('source', 'Unknown')}\n{doc.page_content[:self._max_ctx_chars]}"
                for doc in docs_to_use
            ])
            
            prompt = f"""You are AgriSearch Bot, an AI assistant specializing in agriculture and forestry intelligence.

User Query: {query}

Available Data from Agricultural Records:
{context_text}

Instructions:
1. Answer the question primarily using the data provided above
2. If the data contains relevant information, cite it specifically
3. If the data is insufficient, you may supplement with general agricultural knowledge, but clearly indicate what comes from the data vs. general knowledge
4. Keep responses concise, helpful, and farmer-friendly
5. Use specific numbers, locations, and facts from the data when available

Please provide a clear, helpful answer:"""
        else:
            # No relevant CSV data found - use Ollama's knowledge
            if not self.is_agriculture_related(query):
                return {
                    "response": "I'm specifically designed to help with agriculture and forestry-related queries. Could you please ask a question related to crops, farming, soil, weather, forestry, or agricultural practices?",
                    "richContent": None,
                    "sources": []
                }
            
            prompt = f"""You are AgriSearch Bot, an AI assistant specializing in agriculture and forestry intelligence.

User Query: {query}

Note: No specific data found in local records for this query.

Instructions:
1. Provide helpful agricultural/forestry information based on your knowledge
2. Keep responses practical and farmer-friendly
3. Focus on actionable advice
4. Mention that this is general guidance and local conditions may vary

Please provide a clear, helpful answer:"""
        
        # Get response from Ollama
        try:
            result = self.llm.invoke(prompt)
            # Ollama client may return a dict-like or object; attempt to grab text safely
            response_text = getattr(result, 'content', None) or result.get('content') if isinstance(result, dict) else str(result)
        except Exception as e:
            response_text = f"I apologize, but I encountered an error processing your query: {str(e)}"
        
        # Format rich content
        rich_content = self.format_rich_content(response_text, query_type, context_docs)
        
        # Extract sources
        sources = [
            {
                "source": doc.metadata.get('source', 'Unknown'),
                "excerpt": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            }
            for doc in context_docs[:3]  # Limit to top 3 sources
        ]
        
        out = {
            "response": response_text,
            "richContent": rich_content,
            "sources": sources
        }

        # Cache the result (simple in-memory cache)
        try:
            self._cache[query] = out
        except Exception:
            pass

        return out

    def process_query_stream(self, query: str, on_chunk, k: int = 3):
        """
        Stream the response for `query` by calling `on_chunk(chunk)` for each partial piece.

        `on_chunk` will be invoked with a dict containing at least:
          - 'text': partial text (may be a line or fragment)
          - 'done': bool (True for final chunk)
        Final chunk will also include 'richContent' and 'sources'.

        If the LLM client provides a streaming API, it will be used. Otherwise the full
        response is generated and then split into lines and streamed.
        """
        # Return cached result immediately if available
        if hasattr(self, '_cache') and query in self._cache:
            cached = self._cache[query]
            on_chunk({
                'text': cached['response'],
                'richContent': cached.get('richContent'),
                'sources': cached.get('sources', []),
                'done': True
            })
            return

        # Fast-path direct/csv answers
        direct_answer, direct_sources = self.find_direct_answer(query, k=k)
        if direct_answer:
            out = {"response": direct_answer, "richContent": None, "sources": direct_sources}
            try:
                self._cache[query] = out
            except Exception:
                pass
            on_chunk({'text': direct_answer, 'richContent': None, 'sources': direct_sources, 'done': True})
            return

        csv_answer, csv_sources = self.csv_lookup_answer(query)
        if csv_answer:
            out = {"response": csv_answer, "richContent": None, "sources": csv_sources}
            try:
                self._cache[query] = out
            except Exception:
                pass
            on_chunk({'text': csv_answer, 'richContent': None, 'sources': csv_sources, 'done': True})
            return

        # Retrieve context and build prompt (same logic as process_query)
        context_docs = self.retrieve_context(query) or []
        if context_docs and len(context_docs) > 0:
            docs_to_use = context_docs[:3]
            context_text = "\n\n".join([
                f"Source: {doc.metadata.get('source', 'Unknown')}\n{doc.page_content[:self._max_ctx_chars]}"
                for doc in docs_to_use
            ])
            prompt = f"""You are AgriSearch Bot, an AI assistant specializing in agriculture and forestry intelligence.

User Query: {query}

Available Data from Agricultural Records:
{context_text}

Instructions:
1. Answer the question primarily using the data provided above
2. If the data contains relevant information, cite it specifically
3. If the data is insufficient, you may supplement with general agricultural knowledge, but clearly indicate what comes from the data vs. general knowledge
4. Keep responses concise, helpful, and farmer-friendly
5. Use specific numbers, locations, and facts from the data when available

Please provide a clear, helpful answer:"""
        else:
            if not self.is_agriculture_related(query):
                on_chunk({
                    'text': "I'm specifically designed to help with agriculture and forestry-related queries. Could you please ask a question related to crops, farming, soil, weather, forestry, or agricultural practices?",
                    'richContent': None,
                    'sources': [],
                    'done': True
                })
                return

            prompt = f"""You are AgriSearch Bot, an AI assistant specializing in agriculture and forestry intelligence.

User Query: {query}

Note: No specific data found in local records for this query.

Instructions:
1. Provide helpful agricultural/forestry information based on your knowledge
2. Keep responses practical and farmer-friendly
3. Focus on actionable advice
4. Mention that this is general guidance and local conditions may vary

Please provide a clear, helpful answer:"""

        # Attempt to stream from the LLM if it supports streaming
        assembled = []
        try:
            stream_fn = None
            if hasattr(self.llm, 'stream'):
                stream_fn = getattr(self.llm, 'stream')
            elif hasattr(self.llm, 'invoke_stream'):
                stream_fn = getattr(self.llm, 'invoke_stream')

            if stream_fn is not None:
                for chunk in stream_fn(prompt):
                    # Each chunk may be a dict-like or string/object
                    text = None
                    try:
                        text = getattr(chunk, 'content', None) or (chunk.get('content') if isinstance(chunk, dict) else None)
                    except Exception:
                        text = None
                    if text is None:
                        try:
                            text = str(chunk)
                        except Exception:
                            text = ''
                    if text:
                        assembled.append(text)
                        on_chunk({'text': text, 'done': False})
            else:
                # Fallback: generate full response then stream by lines
                result = self.llm.invoke(prompt)
                result_text = getattr(result, 'content', None) or (result.get('content') if isinstance(result, dict) else str(result))
                for line in result_text.splitlines():
                    assembled.append(line + "\n")
                    on_chunk({'text': line, 'done': False})

        except Exception as e:
            on_chunk({'text': f"I apologize, but I encountered an error processing your query: {str(e)}", 'done': True})
            return

        # Finalize: join assembled text and send final chunk with metadata
        final_text = ''.join(assembled).strip()
        query_type = self.classify_query_type(query)
        rich_content = self.format_rich_content(final_text, query_type, context_docs)
        sources = [
            {
                'source': doc.metadata.get('source', 'Unknown'),
                'excerpt': doc.page_content[:200] + ('...' if len(doc.page_content) > 200 else '')
            }
            for doc in (context_docs or [])[:3]
        ]

        out = {
            'response': final_text,
            'richContent': rich_content,
            'sources': sources
        }
        try:
            self._cache[query] = out
        except Exception:
            pass

        on_chunk({'text': final_text, 'richContent': rich_content, 'sources': sources, 'done': True})


# For testing
if __name__ == "__main__":
    rag = AgriRAGSystem()
    
    test_queries = [
 
        "what is soil?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print(f"{'='*80}")
        
        result = rag.process_query(query)
        
        print(f"\nResponse:\n{result['response']}")
        
        if result['richContent']:
            print(f"\nRich Content: {json.dumps(result['richContent'], indent=2)}")
        
        if result['sources']:
            print(f"\nSources ({len(result['sources'])}):")
            for i, source in enumerate(result['sources'], 1):
                print(f"{i}. {source['source']}")
        print()