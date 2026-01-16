# AgriSearch Bot 🌿
### AI-Powered Agriculture & Forestry Intelligence System

AgriSearch Bot is a sophisticated Retrieval-Augmented Generation (RAG) system designed to provide accurate, context-aware information about agriculture, soil health, crop diseases, weather patterns, and forestry. It combines the power of local LLMs (Llama 3.1) for text reasoning with cloud-based Vision models (Gemini 1.5 Flash) for image analysis.

---

## 🏗️ System Architecture

The system follows a modern client-server architecture with a clear separation of concerns between the React frontend and the Python/FastAPI backend.

```mermaid
graph TD
    User[User 👤] -->|Text / Voice / Image| Frontend[React Frontend ⚛️]
    Frontend -->|POST /chat| Backend[FastAPI Backend 🐍]
    
    subgraph "Backend Core"
        Backend -->|Extract Data| Controller{Has Image?}
        
        subgraph "Vision Pipeline"
            Controller -->|Yes| ImageModule[Image Analysis Module]
            ImageModule -->|Request Key| KeyMgr[Key Rotation Manager 🔑]
            KeyMgr -->|API Call| Gemini[Google Gemini 1.5 Flash 🧠]
            Gemini -->|Image Description| Augmenter[Query Augmenter]
        end
        
        Controller -->|No| Augmenter
        
        subgraph "RAG Pipeline"
            Augmenter -->|Enriched Query| Embed[HF Embeddings (all-MiniLM-L6-v2)]
            Embed -->|Vector Search| Chroma[ChromaDB 🗄️]
            Chroma -->|Relevant Docs| Context[Context Window]
            Context -->|Prompt| LLM[Ollama (Llama 3.1) 🦙]
        end
        
        LLM -->|Structured JSON| Backend
    end
    
    Backend -->|Rich Response| Frontend
```

---

## 🚀 Key Features

### 1. **Hybrid Intelligence**
- **Text Reasoning**: Uses **Llama 3.1** running locally via Ollama for privacy-focused, cost-effective inference.
- **Visual Intelligence**: Uses **Google Gemini 1.5 Flash** to analyze uploaded images (e.g., crop diseases, soil conditions) and incorporates the visual context into the chat.

### 2. **Advanced RAG Pipeline**
- **Vector Store**: **ChromaDB** stores thousands of agricultural Q&A pairs and dataset rows embedded with `sentence-transformers/all-MiniLM-L6-v2`.
- **Retrieval**: Semantic similarity search finds the most relevant documents to ground the LLM's answers, minimizing hallucinations.
- **Ingestion**: Automated pipelines ingest CSV data (census data, Q&A banks) into the vector store.

### 3. **Robust Backend Engineering**
- **Key Rotation**: A custom threaded Key Manager rotates through a pool of Google API keys to handle rate limits (429 errors) gracefully, ensuring high availability for image analysis.
- **FastAPI**: Asynchronous, high-performance API handling concurrent requests.

### 4. **Modern Frontend Experience**
- **Structured UI**: Dynamic rendering of Tables, Section Cards, and Source Citations based on the bot's structured response.
- **Multimodal Input**: Supports Voice typing and Image drag-and-drop.
- **Interactive**: Streaming-like text effects and rich content definition cards (Weather, Soil, Fertilizer).

---

## 📂 Project Structure

```bash
rag/
├── basic-setup/              # Backend Application
│   ├── main.py               # FastAPI Entry Point
│   ├── retrieval_pipeline.py # RAG Logic (LangChain + Chroma)
│   ├── image_analysis.py     # Gemini Vision Integration
│   ├── key_manager.py        # API Key Rotation Logic
│   ├── ingestion_pipeline.py # Data -> Vector DB loader
│   ├── chroma_db/            # Persisted Vector Database
│   └── files/                # Raw CSV Datasets
│
└── frontend/                 # Frontend Application
    └── frontend/             # (Vite Project Root)
        ├── src/
        │   ├── components/   # React Components (AgriSearchBot, ChatMessage)
        │   └── assets/
        └── package.json
```

---

## 🛠️ Setup & Installation

### Prerequisites
1.  **Python 3.10+**
2.  **Node.js & npm**
3.  **Ollama** installed and running (`ollama pull llama3.1`)

### 1. Backend Setup

```bash
# Navigate to backend
cd basic-setup

# Install dependencies
pip install fastapi uvicorn langchain langchain-chroma langchain-ollama langchain-huggingface pydantic python-dotenv google-generativeai pillow

# Set up Environment Variables
# Create a .env file with your Google API Keys
# GOOGLE_API_KEYS=["key1", "key2", ...]

# Run the API Server
python main.py
```
*Server will start at `http://localhost:8000`*

### 2. Frontend Setup

```bash
# Navigate to frontend
cd frontend/frontend

# Install dependencies
npm install

# Start Development Server
npm run dev
```
*UI will be available at `http://localhost:5173`*

---

## 💡 Usage Guide

1.  **Ask Questions**: "What is the best fertilizer for red soil?"
2.  **Upload Images**: Click the camera icon or drag an image of a leaf. Ask "What disease is this?"
3.  **View Sources**: The bot cites its sources (CSV rows, Database IDs) for transparency.
4.  **Voice Mode**: Use the microphone for hands-free queries.

---

## 📊 Data Sources

The system is trained on/indexed with:
- Agricultural Q&A datasets (10,000+ entries)
- Census Data (Agriculture Labourers 2011)
- State Average Agriculture Wages (2020)
- Custom defined terms and definitions.
