async def get_llm_response(message: str) -> str:
    """
    Mock LLM response function. In a real implementation, this would call OpenAI or Anthropic.
    """
    return f"Mock response to: {message}" 