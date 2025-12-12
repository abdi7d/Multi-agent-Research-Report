# src/agents/analysis_agent.py
import json
import google.generativeai as palm
from src.tools.summarizer import extract_key_points

# Set API key globally
palm.configure(api_key="YOUR_GOOGLE_API_KEY")

def analyze_research(research_output: dict) -> dict:
    """
    Convert research output into a structured report using Google PaLM API.
    """
    excerpts = research_output.get("excerpts", [])
    key_points = extract_key_points(excerpts)
    title = research_output.get("query", "Research Report")
    summary = research_output.get("summary", "")

    prompt = (
        f"You are an expert researcher. Topic: {title}\n"
        f"Summary: {summary}\n"
        f"Bullets:\n{key_points}\n\n"
        "Task: Create structured report JSON with keys: title, summary, sections.\n"
        "Sections should be a list of objects with keys: heading, content (list of strings).\n"
        "Return only a valid JSON object."
    )

    try:
        # Call Google PaLM text model
        response = palm.chat(
            model="chat-bison-001",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_output_tokens=1000
        )

        # Extract the last message content
        content = response.last.message.content

        # Parse JSON safely
        structured = json.loads(content)
        return structured

    except Exception as e:
        # Fallback if Google API fails
        return {
            "title": title,
            "summary": summary,
            "sections": [{"heading": "Key Points", "content": key_points}],
            "error": str(e)
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
