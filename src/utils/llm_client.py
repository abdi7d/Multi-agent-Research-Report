"""Thin LLM client wrapper with a mock fallback for local development."""
import os
import json
from typing import Optional
import logging

from src.config import cfg

logger = logging.getLogger(__name__)


class MockLLM:
    def __init__(self):
        pass

    def generate_text(self, prompt: str, temperature: float = 0.2, max_tokens: int = 1024) -> str:
        # Very small heuristic-based mock: if asked to extract bullets, return first sentences
        logger.info("Using MOCK LLM for generation.")
        if "Extract" in prompt or "top insights" in prompt or "Return max" in prompt:
            snippets = []
            # extract excerpts present after EXCERPT markers
            for part in prompt.split("--- EXCERPT"):
                if "---" in part:
                    txt = part.split("---", 1)[-1].strip()
                else:
                    txt = part.strip()
                if txt:
                    first_sentence = txt.split('.')[:1][0].strip()
                    if first_sentence:
                        snippets.append(f"- {first_sentence}.")
            if not snippets:
                # fallback: return a small generic bullet
                return "- Key point: (mocked)"
            return "\n".join(snippets[:8])

        # If asked to return JSON structure, attempt a naive parse
        if "Create structured report JSON" in prompt or "Return only a valid JSON object" in prompt:
            lines = [l.strip() for l in prompt.splitlines() if l.strip()]
            title = lines[0] if lines else "Mock Report"
            # build sections from bullets in prompt
            bullets = [l for l in prompt.splitlines()
                       if l.strip().startswith("-")]
            sections = []
            if bullets:
                sections.append(
                    {"heading": "Key Points", "content": "\n".join(bullets)})
            else:
                sections.append(
                    {"heading": "Overview", "content": "Mock summary generated."})
            return json.dumps({"title": title, "summary": "Mock summary.", "sections": sections})

        # Generic fallback: echo a trimmed prompt summary
        return (prompt[: max(200, max_tokens)])


class LLMClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or cfg.GOOGLE_API_KEY
        self.model = model or cfg.DEFAULT_MODEL
        self._client = None
        # try to initialize real client only if api_key present
        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except ImportError:
                logger.error("google-genai library not installed.")
                self._client = None
            except Exception as e:
                logger.error(f"Failed to initialize Google GenAI Client: {e}")
                self._client = None

    def generate_text(self, prompt: str, temperature: float = 0.2, max_tokens: int = 1024) -> str:
        if self._client:
            try:
                from google.genai import types
                
                # Create the config object
                config = types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
                
                response = self._client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=config
                )
                
                if response.text:
                    return response.text
                return ""
            except Exception as e:
                logger.error(f"GenAI call failed: {e}. Falling back to mock.")
                # fall through to mock behavior
                pass
        # No real client available -> use mock
        return MockLLM().generate_text(prompt, temperature=temperature, max_tokens=max_tokens)


# Singleton accessor
_default_client: Optional[LLMClient] = None


def get_default_client() -> LLMClient:
    global _default_client
    if _default_client is None:
        _default_client = LLMClient()
    return _default_client
