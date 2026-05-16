import os, time
import pickle
from langchain_community.vectorstores import FAISS

from rag.ingestion import load_stackoverflow_dataset
from rag.embedding import get_embeddings
from rag.vector_store import VectorRetriever
from rag.bm25_store import BM25Retriever
from rag.hybrid_retriever import HybridRetriever

from config import *

GLOBAL_RETRIEVER = None

# Define paths for saved indexes
FAISS_INDEX_PATH = "./model_cache/faiss_index"
BM25_INDEX_PATH = "./model_cache/bm25_index.pkl"

def preload_retriever():
    global GLOBAL_RETRIEVER
    start_time = time.time()

    print("Initializing Embedding Model...")

    # Check if we already built the indexes
    if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(BM25_INDEX_PATH):
        print("Step 1/4: Detected saved indexes. Loading from disk...")
        
        # Uses normal CPU config
        embeddings = get_embeddings(EMBEDDING_MAP, "balanced")
        
        vector_retriever = VectorRetriever(embeddings=embeddings, load_path=FAISS_INDEX_PATH)

        # Load BM25
        with open(BM25_INDEX_PATH, "rb") as f:
            bm25_retriever = pickle.load(f)

    else:
        print("\n" + "="*50)
        print("⚠️ No index found. Starting first-time build...")
        
        user_choice = input("[?] Do you want to use CUDA for faster indexing? (Recommended for 1M+ docs) [y/n]: ")
        build_device = "cuda" if user_choice.strip().lower() == 'y' else "cpu"
        
        print(f"\nStep 1/4: Initializing Embedding Model on {build_device.upper()}...")
        embeddings = get_embeddings(EMBEDDING_MAP, "balanced", device_override=build_device)
        
        print("Step 2/4: Loading dataset into memory...") 
        docs_list = list(load_stackoverflow_dataset(JSON_PATH)) 
        print(f"Loaded {len(docs_list)} documents.")

        print(f"Step 3/4: Generating Embeddings on {build_device.upper()}... (Grab a coffee ☕)")
        vector_retriever = VectorRetriever(embeddings=embeddings, documents=docs_list)
        
        print("Saving FAISS index to disk...")
        vector_retriever.vectorstore.save_local(FAISS_INDEX_PATH)

        print("Step 4/4: Building BM25 Index...")
        bm25_retriever = BM25Retriever(docs_list)
        with open(BM25_INDEX_PATH, "wb") as f:
            pickle.dump(bm25_retriever, f)

        print("="*50 + "\n")

    GLOBAL_RETRIEVER = HybridRetriever(vector_retriever, bm25_retriever)
    
    total_time = (time.time() - start_time) / 60
    print(f"✅ Retriever ready! Total setup time: {total_time:.2f} minutes.")