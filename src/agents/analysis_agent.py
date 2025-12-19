"""Analysis agent: synthesize research hits into a structured report.

Uses the summarizer and LLM wrapper to produce a JSON report structure. Falls back to
an internal heuristic if a robust LLM isn't available.
"""
import json
from typing import Dict, List

from src.tools.summarizer import extract_key_points
from src.utils.llm_client import get_default_client


def analyze_research(research_output: dict) -> dict:
    excerpts: List[str] = research_output.get("excerpts", [])
    title = research_output.get("query", "Research Report")
    summary = research_output.get("summary", "")

    # First get concise bullets
    try:
        key_points_text = extract_key_points(excerpts)
    except Exception:
        key_points_text = "\n".join([f"- {e}" for e in excerpts[:8]])

    # Prompt an LLM to convert bullets into structured JSON
    prompt = (
        f"{title}\n"
        f"Summary: {summary}\n\n"
        f"Bulleted points:\n{key_points_text}\n\n"
        "Task: Create a structured report JSON object with keys: 'title', 'summary', 'sections'. "
        "The 'sections' key should be a list of objects, each having 'heading' and 'content' keys. "
        "Content can be a string or a list of strings. "
        "IMPORTANT: Return ONLY valid JSON. Do not include markdown formatting (like ```json ... ```) or any other text."
    )

    llm = get_default_client()
    try:
        content = llm.generate_text(prompt, temperature=0.0, max_tokens=1000)
        # Attempt to clean potential markdown fences if the LLM ignores instructions
        clean_content = content.replace("```json", "").replace("```", "").strip()
        
        parsed = None
        try:
            parsed = json.loads(clean_content)
        except json.JSONDecodeError:
            # Try to find a JSON substring if direct parse fails
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1:
                try:
                    parsed = json.loads(content[start:end+1])
                except Exception:
                    parsed = None

        if isinstance(parsed, dict):
            # Validate basic structure
            if "sections" not in parsed:
                parsed["sections"] = [{"heading": "Key Points", "content": key_points_text}]
            return parsed

    except Exception:
        parsed = None

    # Final fallback: construct a simple structured report
    sections = []
    if key_points_text:
        sections.append({"heading": "Key Points", "content": key_points_text})
    else:
        sections.append(
            {"heading": "Findings", "content": "No key points extracted."})

    return {
        "title": title,
        "summary": summary or (excerpts[0] if excerpts else ""),
        "sections": sections,
    }


# -------------------------
# Debug test
# -------------------------
if __name__ == "__main__":
    dummy_research = {
        "query": "Climate change impacts on Ethiopian Agriculture",
        "summary": "Short summary here",
        "excerpts": [
            "Ethiopian agriculture is highly sensitive to rainfall changes.",
            "Climate change affects crop yields and food security."
        ]
    }
    report = analyze_research(dummy_research)
    print("\n[DEBUG] Structured Report Output:")
    print(json.dumps(report, indent=4))
