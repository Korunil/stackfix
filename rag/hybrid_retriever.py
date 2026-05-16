import hashlib
from collections import OrderedDict

from rag.reranker import rerank
from config import TOP_K, FETCH_K

class HybridRetriever:
    
    def __init__(self, vector_retriever, bm25_retriever):
        self.vector = vector_retriever
        self.bm25 = bm25_retriever

    def retrieve(self, query, return_scores=False):
        
        vector_docs = self.vector.retrieve(
            query, 
            k=FETCH_K
        )
        
        bm25_docs = self.bm25.retrieve(
            query, 
            k=FETCH_K
        )

        merged = vector_docs + bm25_docs

        #Robust deduplication using MD5 hash of the full content
        unique = OrderedDict()

        for d in merged:
            # Hash the content to create a safe, unique key
            doc_hash = hashlib.md5(d.page_content.encode('utf-8')).hexdigest()

            if doc_hash not in unique:
                unique[doc_hash] = d

        merged_docs = list(unique.values())

        reranked = rerank(
            query,
            merged_docs,
            top_k=TOP_K,
            return_scores=return_scores
        )

        return reranked