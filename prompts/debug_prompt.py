def build_debug_user_prompt(query, context):

    return f"""
    
The first retrieved source is the most relevant.
Prioritize it heavily.

Use later sources only if they directly support or clarify the same issue.

Ignore unrelated or weakly related examples.

<context>
{context}
</context>

<user_problem>
{query}
</user_problem>
"""