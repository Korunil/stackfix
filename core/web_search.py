from ddgs import DDGS
from datetime import datetime
import re

from config import TRUSTED_DOMAINS

def compute_result_score(result, query, signals):

    score = 0

    title = (result.get("title") or "").lower()
    body = (result.get("body") or "").lower()
    url = (result.get("url") or "").lower()

    query_terms = set(query.lower().split())

    # DOMAIN WEIGHT

    DOMAIN_WEIGHTS = {
        "github.com": 5,
        "stackoverflow.com": 4,
        "python.langchain.com": 4,
        "docs.python.org": 4,
        "huggingface.co": 3,
        "pytorch.org": 3
    }

    for domain, weight in DOMAIN_WEIGHTS.items():
        if domain in url:
            score += weight
            break

    # KEYWORD OVERLAP

    content_terms = set(
        re.findall(r"\w+", title + " " + body)
    )

    overlap = query_terms.intersection(content_terms)

    score += len(overlap) * 0.5

    # TITLE MATCH BONUS

    for term in query_terms:
        if term in title:
            score += 1.5

    # ERROR MATCH BONUS

    errors = signals.get("errors", [])

    for err in errors:
        if err.lower() in title:
            score += 5

        if err.lower() in body:
            score += 2

    # PACKAGE MATCH BONUS

    modern_packages = signals.get("modern_packages", [])

    for pkg in modern_packages:
        if pkg.lower() in title:
            score += 4

        if pkg.lower() in body:
            score += 2

    # RECENCY BONUS (optional)

    date_str = result.get("date")

    if date_str:
        try:
            dt = datetime.fromisoformat(date_str)

            age_days = (datetime.now() - dt).days

            if age_days < 30:
                score += 2
            elif age_days < 180:
                score += 1

        except:
            pass

    return score

def web_fallback(query, signals):

    try:        
        results = []

        with DDGS() as ddgs:

            search_results = list(ddgs.text(query, max_results=5))

            for r in search_results:

                result = {
                    "title": r.get("title", ""),
                    "body": r.get("body", ""),
                    "url": r.get("href") or r.get("link") or ""
                }
                
                # Compute score per result
                result["retrieval_score"] = compute_result_score(
                    result,
                    query,
                    signals
                )
                
                results.append(result)
        
        results.sort(key=lambda r: r["retrieval_score"], reverse=True)

        return results

    except Exception as e:
        print("Web Search Error:", e)
        return []