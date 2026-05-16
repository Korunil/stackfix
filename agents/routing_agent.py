import re

from config import MODERN_KEYWORDS

class RoutingAgent:

    def __init__(
        self,
        threshold=0.80,
        boost=0.02
    ):

        self.threshold = threshold
        self.boost = boost

    def route(self, confidence, refined_query, refined_signals, docs):
        
        # MODERN ECOSYSTEM DETECTION
        rq = refined_query.lower()

        if any(
            re.search(rf"\b{re.escape(keyword)}\b", rq)
            for keyword in MODERN_KEYWORDS
        ):
            print("\n=== ROUTING DEBUG ===")
            print("\nROUTING AGENT: ⚠️ MODERN KEYWORD DETECTED -> FALLBACK")
            return "fallback"
            

        adjusted_confidence = confidence

        query_errors = set(refined_signals.get("errors", []))
        query_languages = set(refined_signals.get("language", []))
        query_frameworks = set(refined_signals.get("framework", []))
        query_versions = set(refined_signals.get("versions", []))

        titles = []
        tags = []

        for d in docs[:2]:

            title = d.metadata.get("title", "")
            titles.append(title.lower())

            doc_tags = d.metadata.get("tags", [])

            if isinstance(doc_tags, list):
                tags.extend([t.lower() for t in doc_tags])

        title_blob = " ".join(titles)
        tag_blob = " ".join(tags)

        # ERROR MATCHES -> TITLE
        if any(err.lower() in title_blob for err in query_errors):
            adjusted_confidence += 2 * self.boost

        # LANGUAGE MATCHES -> TAGS
        if any(lang.lower() in tag_blob for lang in query_languages):
            adjusted_confidence += self.boost

        # FRAMEWORK MATCHES -> TAGS
        if any(fw.lower() in tag_blob for fw in query_frameworks):
            adjusted_confidence += self.boost

        # VERSION MATCHES -> TITLE
        if any(ver.lower() in title_blob for ver in query_versions):
            adjusted_confidence += 0.5 * self.boost

        adjusted_confidence = min(adjusted_confidence, 1.0)

        print("\n=== ROUTING DEBUG ===")
        print("Base Confidence:", confidence)
        print("Adjusted Confidence:", adjusted_confidence)
        print("Threshold:", self.threshold)

        if adjusted_confidence < self.threshold:
            return "fallback"

        return "local"