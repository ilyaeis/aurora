"""Ollama AI client with fallback support.

Abstracts AI inference so we can swap between local Ollama and cloud APIs.
"""

import json

import httpx

from app.config import settings


class AIClient:
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.fast_model = settings.ollama_fast_model
        self._http = httpx.AsyncClient(timeout=60.0)

    async def generate(
        self,
        prompt: str,
        *,
        model: str | None = None,
        json_mode: bool = True,
        max_tokens: int = 300,
    ) -> dict | str:
        """Generate text from Ollama. Returns parsed JSON if json_mode=True."""
        use_model = model or self.model

        body = {
            "model": use_model,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": max_tokens},
        }
        if json_mode:
            body["format"] = "json"

        try:
            resp = await self._http.post(f"{self.base_url}/api/generate", json=body)
            resp.raise_for_status()
            result = resp.json()
            text = result.get("response", "")

            if json_mode:
                return json.loads(text)
            return text

        except (httpx.HTTPError, json.JSONDecodeError) as e:
            # Return empty dict/string on failure — caller handles fallback
            return {} if json_mode else ""

    async def generate_fast(self, prompt: str, **kwargs) -> dict | str:
        """Use the faster/smaller model for bulk generation."""
        return await self.generate(prompt, model=self.fast_model, **kwargs)

    async def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            resp = await self._http.get(f"{self.base_url}/api/tags")
            return resp.status_code == 200
        except httpx.HTTPError:
            return False


ai_client = AIClient()
