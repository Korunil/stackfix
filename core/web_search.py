from ddgs import DDGS

TRUSTED_DOMAINS = [
    "github.com",
    "stackoverflow.com",
    "python.langchain.com",
    "docs.python.org",
    "pytorch.org",
    "tensorflow.org",
    "fastapi.tiangolo.com",
    "react.dev",
    "nextjs.org"
]

def build_search_query(query):

    domain_filter = " OR ".join(
        [f"site:{d}" for d in TRUSTED_DOMAINS]
    )

    return f"{query} ({domain_filter})"

def web_fallback(query):

    try:
        search_query = build_search_query(query)
        
        results = []

        with DDGS() as ddgs:

            search_results = ddgs.text(
                search_query,
                max_results=5
            )

            for r in search_results:

                results.append({
                    "title": r.get("title", ""),
                    "body": r.get("body", ""),
                    "url": r.get("href", "")
                })

        return results

    except Exception as e:
        print("Web Search Error:", e)
        return []