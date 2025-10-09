"""
OpenRouter LLM integration for Checko.
Adapter for OpenRouter API.
"""
import requests
import json
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import settings
import structlog

logger = structlog.get_logger()


class OpenRouterLLM:
    """OpenRouter LLM client."""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def call(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call OpenRouter API.
        
        Args:
            system_prompt: System message
            user_prompt: User message
            
        Returns:
            LLM response as string
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.WEBAPP_URL,
            "X-Title": "Checko"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }
        
        logger.info("Calling OpenRouter API", model=self.model)
        
        response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]


# Global instance
llm = OpenRouterLLM()
