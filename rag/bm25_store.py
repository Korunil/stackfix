import re
from rank_bm25 import BM25Okapi


class BM25Retriever:
    def __init__(self, docs):
        self.docs = docs
        # Use regex to extract alphanumeric tokens, separating punctuation from code
        self.tokens = [self._tokenize(d.page_content) for d in docs]
        self.bm25 = BM25Okapi(self.tokens)
        
    def _tokenize(self, text):
        return re.findall(r'\w+', text.lower())

    def retrieve(self, query, k=5):
        query_tokens = self._tokenize(query)
        scores = self.bm25.get_scores(query_tokens)

        ranked = sorted(
            zip(self.docs, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return [d for d, _ in ranked[:k]]