def build_fallback_user_prompt(query, fallback_context):

    return f"""
Prefer the provided sources heavily, but you may use general debugging knowledge if needed.
When external sources mention a concrete package installation, prefer exact package names over inferred dependency chains.
If the error is ModuleNotFoundError, prioritize solutions that explicitly install the missing module package.

<fallback_context>
{fallback_context}
</fallback_context>

<user_problem>
{query}
</user_problem>
"""
