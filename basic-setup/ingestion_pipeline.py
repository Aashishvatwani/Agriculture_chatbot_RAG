import os
import csv
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
try:
    from langchain.schema import Document
except Exception:
    # Fallback for older langchain versions
    try:
        from langchain.docstore.document import Document
    except Exception:
        # Define a minimal Document fallback (only used if imports fail)
        class Document:
            def __init__(self, page_content, metadata=None):
                self.page_content = page_content
                self.metadata = metadata or {}
from dotenv import load_dotenv

load_dotenv()

def load_document(docs_path="files"):
    # Load documents from the specified directory
    print("Load Document Function Called")
    if not os.path.exists(docs_path):
        raise FileNotFoundError(f"The specified path {docs_path} does not exist.")
    documents = []

    # Walk the directory and parse CSV files explicitly. For CSVs that contain a
    # `question` column we'll create one Document per row where page_content is
    # the question text and metadata includes other fields (answer, source, etc.).
    p = Path(docs_path)
    for fp in p.rglob('*.csv'):
        try:
            with fp.open(newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                if 'question' in (h.lower() for h in reader.fieldnames or []):
                    for row in reader:
                        # normalize keys to lowercase
                        row_lc = {k.lower(): v for k, v in (row.items() if row else [])}
                        q = row_lc.get('question') or ''
                        if not q:
                            continue
                        metadata = {k: v for k, v in row_lc.items() if k != 'question'}
                        metadata['source'] = str(fp)
                        doc = Document(page_content=q, metadata=metadata)
                        documents.append(doc)
                else:
                    # Fallback: if no `question` column, load entire CSV as text
                    # using CSVLoader for backwards compatibility
                    loader = CSVLoader(fp)
                    docs = loader.load()
                    documents.extend(docs)
        except Exception as e:
            print(f"Warning: failed to process {fp}: {e}")

    if len(documents) == 0:
        raise ValueError(f"No documents found in the specified path {docs_path}.")

    for i, doc in enumerate(documents[:10]):
        # print a short preview for the first few docs
        print(f"Document {i+1}: {doc.metadata.get('source')}, {len(doc.page_content)} characters")
        preview = doc.page_content[:200].replace('\n', ' ')
        print(f" Preview: {preview}...")

    print(f"Total documents loaded: {len(documents)}")
    return documents

def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    split_docs = text_splitter.split_documents(documents)
    
    if split_docs:
        print(f"\nTotal chunks created: {len(split_docs)}")
        for i, doc in enumerate(split_docs[:5]):  # Show first 5 chunks
            print(f"Chunk {i+1}: {doc.metadata['source']}, {len(doc.page_content)} characters")
            print(f" Source: {doc.metadata['source']}")
    
    return split_docs

def create_vector_store(chunks, persist_directory="chroma_db"):
    # Use free local embedding model (same as retrieval)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    print("Creating vector store...")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory,
        collection_metadata={"hnsw:space": "cosine"}
    )
    
    # No need to call persist() - it auto-persists with persist_directory
    print(f"✅ Vector store created and persisted at {persist_directory}")
    print(f"✅ Total vectors stored: {len(chunks)}")
    
    return vector_store

def main():
    print("Main Function Called")
    
    # Load documents
    documents = load_document(docs_path="files")
    
    # Split into chunks
    chunks = split_documents(documents=documents, chunk_size=1000, chunk_overlap=200)
    
    # Create and persist vector store
    create_vector_store(chunks=chunks, persist_directory="chroma_db")
    
    print("\n✅ Ingestion pipeline completed successfully!")

if __name__ == "__main__":
    main()