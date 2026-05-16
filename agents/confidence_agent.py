import numpy as np

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

class ConfidenceAgent:

    # Add is_logit=True so it defaults to squashing the CrossEncoder outputs
    def compute(self, rerank_scores, is_logit=True):
        if not rerank_scores:
            return 0.0
        
        # Grab the top 3 scores 
        top_scores = rerank_scores[:3]
        
        # If CrossEncoder outputs logits, squash them to 0-1
        # Adding a quick check (any s < 0 or s > 1) so we don't double-squash
        if is_logit and any(s < 0 or s > 1 for s in top_scores):
            top_scores = [sigmoid(s) for s in top_scores]

        return sum(top_scores) / min(3, len(top_scores))