from config import PACKAGE_HINTS

def build_web_query(query, signals):

    tokens = []

    # 1. Error names
    tokens.extend(signals.get("errors", []))

    # 2. Modern packages/imports
    tokens.extend(signals.get("modern_packages", []))
    tokens.extend(signals.get("imports", []))

    # 3. Frameworks
    tokens.extend(signals.get("framework", []))

    # 4. Add useful package hints
    for pkg in signals.get("modern_packages", []):
        if pkg in PACKAGE_HINTS:
            tokens.extend(PACKAGE_HINTS[pkg][:2])

    # 5. Remove duplicates while preserving order
    seen = set()
    cleaned = []

    for t in tokens:
        if t and t not in seen:
            cleaned.append(t)
            seen.add(t)

    return " ".join(cleaned[:8])