import re

def clean_context(text):

    if not text:
        return ""

    # Remove non-ascii garbage
    text = re.sub(r"[^\x00-\x7F]+", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove excessive separators
    text = re.sub(r"-{3,}", "---", text)

    # Remove repeated words like: foo foo foo foo
    text = re.sub(r"\b(\w+)( \1\b){2,}", r"\1", text, flags=re.IGNORECASE)

    return text.strip()

def format_code(code_list, label):
    
    if not code_list:
        return ""
    
    if isinstance(code_list, list):
        content = "\n".join(code_list)
    else:
        content = str(code_list)

    content = content.strip()

    # Avoid gigantic code dumps
    content = content[:1200]
    
    return (
        f"\n--- {label} ---\n"
        f"```\n{content}\n```\n"
    )

def build_context(docs):
    """
    Constructs a structured context block for the LLM, 
    ensuring code snippets are explicitly highlighted.
    """

    blocks = []

    for i, doc in enumerate(docs, start=1):

        metadata = doc.metadata
        title = clean_context(metadata.get("title", "Unknown"))[:300]
        
        tags = metadata.get("tags", [])
        if isinstance(tags, list):
            tags_text = ", ".join(tags[:10])  
        else:
            tags_text = str(tags)
        
        score = metadata.get("rerank_score", 0)
        
        # Extract code snippets from metadata
        q_code = metadata.get("question_code", [])
        a_code = metadata.get("answer_code", [])
        
        # Format code blocks for the prompt       
        code_blocks = []
        if q_code and len(str(q_code)) < 1200:
            code_blocks.append(format_code(q_code, 'QUESTION CODE'))
        
        if a_code and len(str(a_code)) <1200:
            code_blocks.append(format_code(a_code, 'ANSWER CODE'))
        
        code_section = "\n".join(code_blocks)

        # Format text
        text = clean_context(doc.page_content[:700])

        block = f"""
[{i}] SOURCE: {title}

RELEVANCE:
{score:.4f}

TAGS:
{tags_text}

DEBUG DISCUSSION:
{text}

{code_section}
"""

        blocks.append(block.strip())

    return "\n\n" + "="*30 + "\n" + "\n\n".join(blocks)
    
def build_fallback_context(github_results, web_results):
    """
    Formats external search results, clearly separating and labeling 
    GitHub issues from general Web results.
    """
    blocks = []

    # 1. Inject GitHub Data with specific labeling
    if github_results:
        blocks.append("=== GITHUB ISSUES (High Priority for Code Bugs) ===")
        for i, res in enumerate(github_results, start=1):
            title = clean_context(res.get("title", "Unknown Title"))[:300]
            url = res.get("url", "No URL")
            body = clean_context(res.get("body", ""))[:2000]
            
            block = f"""
[GITHUB-{i}] 
TITLE: {title}

URL: {url}

CONTENT:
{body}

{'-'*40}
"""
            blocks.append(block.strip())

    # 2. Inject Web Data with specific labeling
    if web_results:
        blocks.append("\n=== WEB SEARCH RESULTS (General Documentation) ===")
        for i, res in enumerate(web_results, start=1):
            title = clean_context(res.get("title", "Unknown Title"))[:300]
            url = res.get("url", "No URL")
            body = clean_context(res.get("body", ""))[:2000]
            
            block = f"""
[WEB-{i}] 
TITLE: {title}

URL: {url}

CONTENT:
{body}

"{'-'*30}"""           
            blocks.append(block.strip())
            

    return "\n\n".join(blocks)