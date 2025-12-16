# src/agents/research_agent.py
import json
import google.generativeai as palm

# Set your Google API key
# palm.configure(api_key="YOUR_GOOGLE_API_KEY")
palm.configure(api_key="AIzaSyAeIw9ace-n7-Hb1DQHSy62sv69002CzIk")

def research_topic(topic: str, max_results: int = 5) -> dict:
    """
    Generate research hits and excerpts for a given topic using Google PaLM API.
    Returns a dict with keys: query, hits, excerpts, summary.
    """
    if not topic:
        return {"query": topic, "hits": [], "excerpts": [], "summary": ""}

    prompt = (
        f"You are an expert researcher. Provide {max_results} key research findings "
        f"about the topic: '{topic}'.\n"
        "Return JSON with keys: hits (list of titles), excerpts (list of strings), summary (short summary)."
    )

    try:
        response = palm.chat(
            model="chat-bison-001",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_output_tokens=1000
        )

        content = response.last.message.content

        research = json.loads(content)

        # Ensure all keys exist
        research.setdefault("query", topic)
        research.setdefault("hits", [])
        research.setdefault("excerpts", [])
        research.setdefault("summary", "")

        return research

    except Exception as e:
        return {"query": topic, "hits": [], "excerpts": [], "summary": "", "error": str(e)}
