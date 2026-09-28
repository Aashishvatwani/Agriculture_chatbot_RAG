import os
import requests
from dotenv import load_dotenv

load_dotenv()


class OpenRouterKeyManager:
    """Simple manager for OpenRouter API key and model configuration."""

    def __init__(self, api_key: str = None):
        """
        Initialize the key manager.

        Args:
            api_key: OpenRouter API key. If not provided, reads from
                     OPENROUTER_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No OpenRouter API key provided. Set OPENROUTER_API_KEY in "
                "your .env file or pass it directly."
            )
        self.api_base = "https://openrouter.ai/api/v1"
        print(f"OpenRouter key configured (ending ...{self.api_key[-4:]})")

    def get_headers(self, referer: str = "http://localhost:8000", title: str = "AgriSearch Bot") -> dict:
        """Return standard headers for OpenRouter API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": referer,
            "X-Title": title,
        }

    def chat_completion(self, messages: list, model: str = None, **kwargs) -> dict:
        """
        Send a chat completion request to OpenRouter.

        Args:
            messages: List of message dicts (role/content).
            model: Model identifier. Defaults to OPENROUTER_MODEL env var or
                   qwen/qwen3.8-27b:free.
            **kwargs: Extra body parameters (temperature, max_tokens, etc.)

        Returns:
            The JSON response from OpenRouter.
        """
        model = model or os.getenv("OPENROUTER_MODEL", "qwen/qwen3.8-27b:free")

        payload = {
            "model": model,
            "messages": messages,
            **kwargs,
        }

        response = requests.post(
            f"{self.api_base}/chat/completions",
            headers=self.get_headers(),
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def execute_with_retry(self, func, *args, max_retries: int = 3, **kwargs):
        """
        Execute a function with simple retry logic for transient errors.

        Args:
            func: Callable to execute.
            max_retries: Number of retries on transient failures.

        Returns:
            The result of func(*args, **kwargs).
        """
        last_error = None
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                # Retry on rate-limit or server errors
                if "429" in error_str or "500" in error_str or "502" in error_str or "503" in error_str:
                    print(f"Transient error (attempt {attempt + 1}/{max_retries}): {e}")
                    continue
                else:
                    raise
        raise RuntimeError(f"All {max_retries} retry attempts failed. Last error: {last_error}")
