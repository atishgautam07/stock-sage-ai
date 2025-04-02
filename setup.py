# setup.py

import os
from dotenv import load_dotenv
import streamlit as st
from langchain_openai import ChatOpenAI
from tavily import TavilyClient
import yfinance as yf

def verify_environment():
    """Verify that the environment is correctly set up."""
    # Load environment variables
    load_dotenv()
    
    issues = []
    
    # Check OpenAI API key
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        issues.append("OpenAI API key not found in .env file")
    else:
        try:
            # Test OpenAI API
            llm = ChatOpenAI(temperature=0)
            llm.invoke("Hello")
            print("✅ OpenAI API connection successful")
        except Exception as e:
            issues.append(f"OpenAI API error: {str(e)}")
    
    # Check Tavily API key
    tavily_key = os.getenv("TAVILY_API_KEY")
    if not tavily_key:
        issues.append("Tavily API key not found in .env file")
    else:
        try:
            # Test Tavily API
            client = TavilyClient(api_key=tavily_key)
            client.search(query="test", search_depth="basic")
            print("✅ Tavily API connection successful")
        except Exception as e:
            issues.append(f"Tavily API error: {str(e)}")
    
    # Test Yahoo Finance data retrieval
    try:
        data = yf.download("AAPL", period="1d")
        if len(data) > 0:
            print("✅ Yahoo Finance data retrieval successful")
        else:
            issues.append("Yahoo Finance returned empty data")
    except Exception as e:
        issues.append(f"Yahoo Finance error: {str(e)}")
    
    return issues

if __name__ == "__main__":
    print("Verifying environment setup...")
    issues = verify_environment()
    
    if issues:
        print("\n❌ Environment setup issues found:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nPlease fix these issues before proceeding.")
    else:
        print("\n✅ All environment checks passed! Your setup is ready.")
        print("Run 'streamlit run app.py' to start the application.")