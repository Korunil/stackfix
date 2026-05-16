from sentence_transformers import CrossEncoder
from config import CROSS_ENCODER, DEVICE_RERANKER, TOP_K, BATCH_SIZE

reranker = CrossEncoder(
    CROSS_ENCODER,
    device=DEVICE_RERANKER
)

def clean_text(text):
    return " ".join(str(text).split())

def rerank(query, 
    docs, 
    top_k=TOP_K, 
    return_scores=False ):

    if not docs:
        if return_scores:
            return [], []
        return []
    
    pairs = []

    for d in docs:

        metadata = d.metadata

        title = metadata.get("title", "")
        tags = metadata.get("tags", [])
        question_code = metadata.get("question_code", [])
        answer_code = metadata.get("answer_code", [])

        # Normalize
        tags_text = ", ".join(tags) if isinstance(tags, list) else str(tags)

        q_code = "\n".join(question_code) if isinstance(question_code, list) else str(question_code)

        a_code = "\n".join(answer_code) if isinstance(answer_code, list) else str(answer_code)
        
        title = title[:300]
        q_code = clean_text(q_code)
        a_code = clean_text(a_code)

        rerank_text = f"""
TITLE:
{title}

TAGS:
{tags_text}

CONTENT:
{d.page_content[:1000]}

QUESTION CODE:
{q_code[:700]}

ANSWER CODE:
{a_code[:900]}
"""

        pairs.append((query, rerank_text))

    scores = reranker.predict(
        pairs, 
        batch_size=BATCH_SIZE,
        convert_to_numpy=True
    )

    ranked = sorted(
        zip(docs, scores),
        key=lambda x: x[1],
        reverse=True
    )

    final_docs = []
    final_scores = []
    seen_titles = set()

    for doc, score in ranked:
        
        title = doc.metadata.get("title", "").strip().lower()
        if title in seen_titles:
            continue
        seen_titles.add(title)
        score = float(score)
        doc.metadata["rerank_score"] = score
        final_docs.append(doc)
        final_scores.append(score)
        
        if len(final_docs) >= top_k:
            break

    if return_scores:
        return final_docs, final_scores
    
    return final_docs