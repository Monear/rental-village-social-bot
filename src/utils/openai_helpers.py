import os
import openai
from typing import Optional
from dotenv import load_dotenv
import logging

# Load environment variables from .env if present
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

logger = logging.getLogger(__name__)

class OpenAIRateLimitError(Exception):
    """Custom exception for OpenAI API rate limiting."""
    pass

def call_openai_api(prompt: str, model: str = "gpt-3.5-turbo", max_tokens: int = 512, temperature: float = 0.7) -> Optional[str]:
    """
    Calls the OpenAI Chat API with the given prompt and returns the response text.
    Raises OpenAIRateLimitError on rate limit.
    Logs all errors for debugging.
    Compatible with openai>=1.0.0 and httpx==0.27.2.
    """
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY must be set in the environment or .env file.")
        raise ValueError("OPENAI_API_KEY must be set in the environment or .env file.")
    
    try:
        from openai import OpenAI
        # Simple client creation - httpx version is pinned to avoid proxy issues
        client = OpenAI(
            api_key=OPENAI_API_KEY,
            timeout=60.0
        )
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        # Handle OpenAI rate limit error by message string (for openai v1+)
        if 'rate limit' in str(e).lower() or '429' in str(e):
            logger.error(f"OpenAI Rate Limit Error: {e}")
            raise OpenAIRateLimitError(str(e))
        logger.error(f"OpenAI API Error: {e}")
        return None
