from agents.refinement_agent import QueryRefinementAgent
from agents.confidence_agent import ConfidenceAgent
from agents.routing_agent import RoutingAgent

from prompts.system_prompt import SYSTEM_PROMPT
from prompts.debug_prompt import build_debug_user_prompt
from prompts.fallback_prompt import build_fallback_user_prompt

from core.citation_builder import build_context, build_fallback_context
from core.query_fallback import build_web_query
from core.github_search import github_fallback
from core.web_search import web_fallback

from memory.memory import ChatMemory

from config import GENERATION_CONFIGS

from urllib.parse import urlparse

def normalize(url):
    try:
        return urlparse(url).netloc + urlparse(url).path
    except:
        return url

def infer_source_type(url):

    if not url:
        return "web"

    url = url.lower()

    if "github.com" in url:
        return "github"

    if "stackoverflow.com" in url:
        return "stackoverflow"

    if "docs.python.org" in url:
        return "docs"

    if "huggingface.co" in url:
        return "huggingface"

    return "web"

class DebugPipeline:

    def __init__(self, retriever, llm):

        self.retriever = retriever
        self.llm = llm

        self.refinement_agent = QueryRefinementAgent()        
        self.confidence_agent = ConfidenceAgent()        
        self.routing_agent = RoutingAgent()
        
        self.memory = ChatMemory()

    def prepare(self, query):

        # REFINE QUERY
        refined = self.refinement_agent.refine(query)

        refined_query = refined["query"]
        refined_signals = refined["signals"]

        # RETRIEVE & RERANK
        reranked_docs, rerank_scores = self.retriever.retrieve(
            refined_query, 
            return_scores=True
        )

        # CONFIDENCE & ROUTING
        confidence = self.confidence_agent.compute(rerank_scores)
        route = self.routing_agent.route(confidence, refined_query, refined_signals, reranked_docs[:2])
       
        # Get chat history
        chat_history = self.memory.format()
        memory_block = f"PREVIOUS CHAT HISTORY:\n{chat_history}\n\n" if chat_history else ""
        
        # Prepend memory to the query
        full_query = memory_block + query
        citations = []
        
        if route == "local":
            
            # Set the config
            active_config = GENERATION_CONFIGS["debug"]
            
            # Using citation builder
            local_context = build_context(reranked_docs[:2])
            
            user_prompt = build_debug_user_prompt(full_query, local_context)
            
            for d in reranked_docs[:2]:
                citations.append({
                    "title": d.metadata.get("title", "StackOverflow Post"),
                    "score": d.metadata.get("rerank_score", 0.0),
                    "is_external": False
                })

        else: # "fallback"
            
            # Set the config
            active_config = GENERATION_CONFIGS["fallback"]
            web_query = build_web_query(query, refined_signals)
            github_results = github_fallback(web_query)
            web_results = web_fallback(web_query, refined_signals)
            
            # treat only meaningful GitHub results as valid
            valid_github = [
                g for g in github_results
                if g.get("url") and g.get("title")
            ]
            
            # THE SAFETY NET: If GitHub failed
            if github_results: 
                github_urls = {normalize(g.get("url", "")) for g in valid_github}
                web_results = [
                    w for w in web_results
                    if normalize(w.get("url", "")) not in github_urls
                ][:2] 
            else:
                web_results = web_results[:5]
            
            if not github_results and not web_results:
                print("ALL SOURCES FAILED → injecting fallback citation")
                web_results = [{
                    "title": "No external sources found",
                    "url": "",
                    "body": "Fallback generated response"
                }]
            
            fallback_context = build_fallback_context(github_results, web_results)           
            user_prompt = build_fallback_user_prompt(full_query, fallback_context)

            for ext in (github_results):
                citations.append({
                    "title": ext.get("title", "GitHub Results"),
                    "url": ext.get("url", "#"),
                    "score": ext.get("score", 1.0),
                    "is_external": True,
                    "source_type": "github_api"
                })
                
            for ext in (web_results):
                citations.append({
                    "title": ext.get("title", "Web Results"),
                    "url": ext.get("url", "#"),
                    "score": ext.get("score", 1.0),
                    "is_external": True,
                    "source_type": infer_source_type(ext.get("url", "#"))
                })

        print("\n========PIPELINE DEBUG==============")
        print("QUERY:", query)
        print("QUERY + CHAT:", full_query)
        print("REFINED:", refined_query)
        print("CONFIDENCE:", confidence)
        print("ROUTE:", route)
        print("RAW GITHUB:", github_results)
        print("RAW WEB:", web_results)
        print("FINAL CITATIONS:")
        for c in citations:
            print(c)

        return {
            "system_prompt": SYSTEM_PROMPT, 
            "user_prompt": user_prompt,
            "route": route,
            "confidence": confidence,
            "citations": citations,
            "config": active_config
        }
