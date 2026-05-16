def build_search_query(query, signals):

    parts = [query]

    if signals["errors"]:
        parts.extend(signals["errors"])

    if signals["framework"]:
        parts.extend(signals["framework"])

    if signals["language"]:
        parts.extend(signals["language"])

    if signals.get("imports"):
        parts.extend(signals["imports"])
        
    if signals["modern_packages"]:
        parts.extend(signals["modern_packages"])
    
    # Add semantic debugging intent boosters
    parts.extend([
        "fix",
        "solution",
        "github issue",
        "stackoverflow",
        "documentation"
    ])

    return " ".join(parts)