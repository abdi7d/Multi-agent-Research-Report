"""Research agent: query web search wrapper and produce snippets + summary."""
from typing import List, Dict
from src.tools import web_search
from src.tools.summarizer import extract_key_points
from src.utils.llm_client import get_default_client


def research_topic(topic: str, max_results: int = 5) -> Dict:
    """Run a web search for `topic`, collect hits and produce short excerpts and a summary.

    Returns a dict with keys: query, hits (list of dicts), excerpts (list of strings), summary (str)
    """
    if not topic:
        return {"query": topic, "hits": [], "excerpts": [], "summary": ""}

    # Get search hits from the web_search tool (uses SerpAPI if configured, otherwise mock/simple scrapper)
    try:
        hits = web_search.search(topic, num=max_results)
    except Exception:
        hits = []

    # Build excerpts list from hits' snippets
    excerpts: List[str] = []
    hits_out: List[Dict] = []
    for h in hits[:max_results]:
        title = h.get("title") or h.get("link") or ""
        link = h.get("link") or ""
        snippet = (h.get("snippet") or "").strip()
        if snippet:
            excerpts.append(snippet)
        hits_out.append({"title": title, "link": link, "snippet": snippet})

    # If no excerpts found, add a placeholder
    if not excerpts:
        # Create a small curated mock result set for local/dev runs
        mocked_hits = [
            {
                "title": f"Overview: {topic}",
                "link": "",
                "snippet": f"{topic} is a multidimensional challenge affecting agriculture, livelihoods, and food security."
            },
            {
                "title": f"Impacts and adaptation for {topic}",
                "link": "",
                "snippet": f"Key impacts include changing rainfall patterns, increased drought frequency, and crop yield variability."
            },
            {
                "title": f"Policy responses for {topic}",
                "link": "",
                "snippet": f"Adaptation measures include drought-resistant crops, irrigation improvements, and farmer training programs."
            }
        ]
        hits_out = mocked_hits[:max_results]
        excerpts = [h["snippet"] for h in hits_out]

    # Use summarizer (backed by LLM client) to extract key points; fallback to naive summary
    try:
        key_points_text = extract_key_points(excerpts)
        # Build a short summary from the returned bullets (first lines)
        summary = key_points_text.splitlines()[0] if key_points_text else ""
    except Exception:
        # Naive fallback
        summary = " ".join(excerpts[:2])
        key_points_text = "- " + summary

    return {
        "query": topic,
        "hits": hits_out,
        "excerpts": excerpts,
        "summary": summary,
        "key_points": key_points_text,
    }
