"""LLM provider factory for SqlAgent"""

from vanna.integrations.ollama import OllamaLlmService
from vanna.integrations.google import GeminiLlmService
from config import Config


def create_llm(config=Config):
    """Create and return the LLM service based on configuration.

    Args:
        config: Configuration class (defaults to Config)

    Returns:
        LLM service instance (OllamaLlmService or GeminiLlmService)
    """
    if config.LLM_PROVIDER == 'gemini':
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required when LLM_PROVIDER=gemini")
        return GeminiLlmService(
            model=config.GEMINI_MODEL,
            api_key=config.GEMINI_API_KEY
        )
    else:
        return OllamaLlmService(
            model=config.OLLAMA_MODEL,
            host=config.OLLAMA_HOST
        )
