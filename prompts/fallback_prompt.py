def build_fallback_user_prompt(query, fallback_context):

    return f"""
Prefer the provided sources heavily, but you may use general debugging knowledge if needed.

<fallback_context>
{fallback_context}
</fallback_context>

<user_problem>
{query}
</user_problem>
"""