from google import genai
from src.config import cfg

class LLMClient:
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or cfg.GOOGLE_API_KEY
        if not self.api_key:
            raise RuntimeError("GOOGLE_API_KEY is required in environment.")
        self.client = genai.Client(api_key=self.api_key)
        self.model = model or cfg.DEFAULT_MODEL

    def generate_text(self, prompt: str, temperature: float = 0.2, max_tokens: int = 1024):
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            temperature=temperature,
            max_output_tokens=max_tokens
        )
        # Extract output text
        output_texts = []
        for item in getattr(response, "output", []):
            if item.get("type") == "output_text":
                output_texts.append(item.get("text", ""))
        return "\n".join(output_texts)

# Singleton
_default_client = None
def get_default_client():
    global _default_client
    if _default_client is None:
        _default_client = LLMClient()
    return _default_client
