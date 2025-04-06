# utils/helpers.py
import os
import json
from datetime import datetime
import requests
from typing import Dict, Any, List, Tuple

def create_cache_dir():
    """Create cache directory if it doesn't exist."""
    cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    return cache_dir

def save_to_cache(key: str, data: Any) -> str:
    """
    Save data to cache.
    
    Args:
        key (str): Cache key
        data (Any): Data to cache
        
    Returns:
        str: Cache file path
    """
    cache_dir = create_cache_dir()
    cache_file = os.path.join(cache_dir, f"{key}_{datetime.now().strftime('%Y%m%d')}.json")
    
    with open(cache_file, "w") as f:
        json.dump(data, f)
    
    return cache_file

def load_from_cache(key: str, max_age_days: int = 1) -> Tuple[bool, Any]:
    """
    Load data from cache if it exists and is not too old.
    
    Args:
        key (str): Cache key
        max_age_days (int): Maximum age in days
        
    Returns:
        Tuple[bool, Any]: (success, data)
    """
    cache_dir = create_cache_dir()
    cache_file = os.path.join(cache_dir, f"{key}_{datetime.now().strftime('%Y%m%d')}.json")
    
    if os.path.exists(cache_file):
        # Check if file is recent enough
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        age = (datetime.now() - file_time).days
        
        if age <= max_age_days:
            with open(cache_file, "r") as f:
                return True, json.load(f)
    
    # Older cache files with the same key
    for file in os.listdir(cache_dir):
        if file.startswith(f"{key}_") and file.endswith(".json"):
            os.remove(os.path.join(cache_dir, file))
    
    return False, None

def fetch_stock_price(ticker: str) -> Dict[str, Any]:
    """
    Fetch current stock price information.
    
    Args:
        ticker (str): Stock ticker
        
    Returns:
        Dict[str, Any]: Price information
    """
    try:
        # Try the cache first
        cache_hit, cache_data = load_from_cache(f"price_{ticker}")
        if cache_hit:
            return cache_data
        
        # Alpha Vantage API (free tier, limited requests)
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}"
        
        response = requests.get(url)
        data = response.json()
        
        if "Global Quote" in data and data["Global Quote"]:
            price_data = {
                "price": float(data["Global Quote"].get("05. price", 0)),
                "change": float(data["Global Quote"].get("09. change", 0)),
                "change_percent": data["Global Quote"].get("10. change percent", "0%"),
                "volume": int(data["Global Quote"].get("06. volume", 0)),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Cache the result
            save_to_cache(f"price_{ticker}", price_data)
            
            return price_data
        else:
            return {
                "price": 0,
                "change": 0,
                "change_percent": "0%",
                "volume": 0,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": "Price data not available"
            }
    except Exception as e:
        return {
            "price": 0,
            "change": 0,
            "change_percent": "0%",
            "volume": 0,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error": str(e)
        }

def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace.
    
    Args:
        text (str): Input text
        
    Returns:
        str: Cleaned text
    """
    lines = (line.strip() for line in text.splitlines())
    return "\n".join(line for line in lines if line)