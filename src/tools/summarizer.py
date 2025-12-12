
from src.utils.llm_client import get_default_client
from typing import List

llm = get_default_client()

def extract_key_points(texts: List[str], max_points: int = 8) -> str:
    prompt = "Extract top insights/facts from the following excerpts as numbered bullets:\n"
    for i, t in enumerate(texts, start=1):
        prompt += f"--- EXCERPT {i} ---\n{t}\n\n"
    prompt += f"Return max {max_points} concise bullets."
    return llm.generate_text(prompt, temperature=0.0, max_tokens=800)
