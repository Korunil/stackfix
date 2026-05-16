import re
from config import MODERN_PACKAGES, LANGUAGES, FRAMEWORKS, ERROR_PATTERNS

VERSION_PATTERN = r"\d+\.\d+(?:\.\d+)?"
IMPORT_PATTERN = r"No module named ['\"]([^'\"]+)['\"]"


def extract_signals(query):

    q = query.lower()

    signals = {
        "language": [],
        "framework": [],
        "errors": [],
        "versions": [],
        "imports": [],
        "modern_packages": [],
    }

    # languages
    for lang in LANGUAGES:
        if re.search(rf"\b{re.escape(lang)}\b", q):
            signals["language"].append(lang)

    # frameworks
    for fw in FRAMEWORKS:
        if re.search(rf"\b{re.escape(fw)}\b", q):
            signals["framework"].append(fw)

    # errors
    for pattern in ERROR_PATTERNS:
        matches = re.findall(pattern, query)

        if matches:
            signals["errors"].extend(matches)

    # versions
    versions = re.findall(
        VERSION_PATTERN,
        query
    )
    signals["versions"] = versions

    # imports
    imports = re.findall(IMPORT_PATTERN, query)
    signals["imports"] = imports
    
    # Modern packages
    for pkg in MODERN_PACKAGES:
        if pkg.lower() in q:
            signals["modern_packages"].append(pkg)
    
    return signals