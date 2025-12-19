# # src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-2.0-flash")
    try:
        MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    except ValueError:
        MAX_SEARCH_RESULTS = 5
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")

cfg = Config()

