from config import ERROR_SYNONYMS, PACKAGE_HINTS

def expand_query(query, parsed):

    expanded = [query]

    error = parsed.get("error")

    if error in ERROR_SYNONYMS:
        expanded.extend(ERROR_SYNONYMS[error])

    if error in PACKAGE_HINTS:
        expansions.extend(PACKAGE_HINTS[error])
    
    return " ".join(expanded)