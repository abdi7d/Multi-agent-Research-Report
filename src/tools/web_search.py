import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from src.config import cfg

SERPAPI_KEY = cfg.SERPAPI_API_KEY

def _serpapi_search(query: str, num: int = 5) -> List[Dict]:
    from serpapi import GoogleSearch
    params = {"q": query, "engine": "google", "num": num, "api_key": SERPAPI_KEY}
    search = GoogleSearch(params)
    results = search.get_dict()
    items = results.get("organic_results", [])[:num]
    return [{"title": it.get("title"), "link": it.get("link"), "snippet": it.get("snippet") or ""} for it in items]

def _duckduckgo_search(query: str, num: int = 5) -> List[Dict]:
    url = "https://duckduckgo.com/html"
    resp = requests.post(url, data={"q": query})
    soup = BeautifulSoup(resp.text, "lxml")
    results = []
    for a in soup.select("a.result__a")[:num]:
        results.append({"title": a.get_text(), "link": a.get("href"), "snippet": ""})
    return results

def search(query: str, num: int = 5) -> List[Dict]:
    if SERPAPI_KEY:
        try:
            return _serpapi_search(query, num)
        except Exception:
            pass
    return _duckduckgo_search(query, num)
