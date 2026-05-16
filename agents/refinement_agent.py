from core.query_parser import extract_signals
from core.query_builder import build_search_query
from core.query_expander import expand_query


class QueryRefinementAgent:

    def refine(self, query):

        # PARSE QUERY
        signals = extract_signals(query) or {"errors": [], "language": [], "framework": [], "versions": [], "imports": [], "modern_packages": []}

        # BUILD SEARCH QUERY
        refined_query = build_search_query(
            query,
            signals
        )
        
        error_context = signals.get("errors")[0] if signals.get("errors") else None

        # EXPAND QUERY
        expanded_query = expand_query(
            refined_query,
            {"error": error_context}
        )

        return {
            "query": expanded_query,
            "signals": signals
        }