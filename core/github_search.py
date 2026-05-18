import requests
from config import GITHUB_API


def github_fallback(query):

    try:

        params = {
            "q": query,
            "sort": "comments",
            "order": "desc",
            "per_page": 3
        }

        response = requests.get(
            GITHUB_API,
            params=params,
            timeout=10
        )

        data = response.json()

        items = data.get("items", [])

        results = []

        for item in items:

            results.append({
                "title": item["title"],
                "body": item.get("body", "")[:1200],
                "url": item["html_url"]
            })

        return results

    except Exception:
        return []