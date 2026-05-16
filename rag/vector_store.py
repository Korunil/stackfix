from langchain_community.vectorstores import FAISS
from tqdm import tqdm
from config import K, FETCH_K

class VectorRetriever:
    def __init__(self, embeddings, documents=None, load_path=None):
        
        self.embeddings = embeddings
        
        if load_path:
            # Load from disk
            self.vectorstore = FAISS.load_local(
                load_path,
                self.embeddings,
                allow_dangerous_deserialization = True
            )
        
        elif documents:
            # Build from scratch with progress bar to track
            batch_size = 25000
            print(f"Initiailizing FAISS with first batch of {batch_size}...")
            
            # FAISS requires the first batch to create the index structure
            self.vectorstore = FAISS.from_documents(documents[:batch_size], self.embeddings)
            
            # Add remaining batches with a progress bar
            if len(documents) > batch_size:
                for i in tqdm(range(batch_size, len(documents), batch_size), desc="Indexing FAISS"):
                    batch = documents[i : i + batch_size]
                    self.vectorstore.add_documents(batch)
            
        else:
            raise ValueError("You must provide either 'documents' to build or 'load_path' to load.")

    def retrieve(self, query, k=K, fetch_k=FETCH_K, use_mmr=True):
        if use_mmr:
            return self.vectorstore.max_marginal_relevance_search(
                query, k=k, fetch_k=fetch_k
            )
        return self.vectorstore.similarity_search(query, k=k)