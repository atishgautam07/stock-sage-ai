# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Model settings
LLM_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-ada-002"

# Research settings
MAX_SEARCH_RESULTS = 5
MAX_FILTERED_ARTICLES = 3
ARTICLE_RECENCY_DAYS = 90  # Only consider articles from the last 30 days
MAX_RESEARCH_ATTEMPTS = 3  # Maximum number of research retries

# File paths
CACHE_DIR = "cache"