# agents/filtering.py
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LLM_MODEL, MAX_FILTERED_ARTICLES, ARTICLE_RECENCY_DAYS

class FilteringSystem:
    def __init__(self):
        """
        Initialize the Filtering System with necessary components.
        """
        # Initialize LLM
        self.llm = ChatOpenAI(temperature=0, model=LLM_MODEL)
        
        # Create relevance checker prompt
        relevance_template = """
        You are a financial analyst assistant. Evaluate if the following article 
        or snippet is relevant for short-term stock investment analysis for {ticker} ({company_name}).
        
        An article is relevant if it contains information about:
        1. Earnings reports or financial results
        2. Analyst recommendations or price targets
        3. Major business developments (new products, partnerships, etc.)
        4. Market sentiment or stock performance trends
        5. Competitive landscape changes
        
        Article or snippet:
        {article}
        
        Respond with:
        - "RELEVANT" if the article contains useful information for short-term investment decisions
        - "NOT_RELEVANT" if the article lacks substantial financial insights
        - Briefly explain your decision in 1-2 sentences.
        """
        
        self.relevance_prompt = PromptTemplate(
            input_variables=["article", "ticker", "company_name"],
            template=relevance_template
        )
        
        # self.relevance_chain = LLMChain(
        #     llm=self.llm,
        #     prompt=self.relevance_prompt
        # )
    
    def fetch_article_content(self, url):
        """
        Fetch and extract text content from a URL.
        
        Args:
            url (str): Article URL
            
        Returns:
            str: Extracted text content
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to get the article date
            date_str = None
            date_tags = soup.find_all(['time', 'meta'], attrs={'datetime': True})
            if date_tags:
                date_str = date_tags[0].get('datetime')
            
            # Check if the article is recent enough
            if date_str:
                try:
                    article_date = datetime.fromisoformat(date_str.split('T')[0])
                    cutoff_date = datetime.now() - timedelta(days=ARTICLE_RECENCY_DAYS)
                    if article_date < cutoff_date:
                        return None, "Article too old"
                except (ValueError, IndexError):
                    pass  # If date parsing fails, continue with content extraction
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            # Get text
            text = soup.get_text()
            
            # Clean text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text, None
        except Exception as e:
            return None, f"Error fetching {url}: {str(e)}"
    
    def check_relevance(self, article, ticker, company_name):
        """
        Check if an article is relevant for stock analysis.
        
        Args:
            article (str): Article text or snippet
            ticker (str): Stock ticker
            company_name (str): Company name
            
        Returns:
            bool: True if relevant, False otherwise
            str: Explanation
        """
        # Create input dictionary
        input_variables = {
            "article": article[:1500],  # Limit to first 1500 chars
            "ticker": ticker,
            "company_name": company_name
        }
        
        # Use the invoke method directly on the chained objects
        result = (self.relevance_prompt | self.llm).invoke(input_variables)
        
        # Extract the content from the AIMessage object
        content = result.content
        
        # Process the content
        is_relevant = "RELEVANT" in content
        explanation = content.replace("RELEVANT", "").replace("NOT_RELEVANT", "").strip()
        
        return is_relevant, explanation
    
    def filter(self, research_results, ticker, company_name):
        """
        Filter search results based on relevance.
        
        Args:
            research_results (dict): Results from ResearchAgent
            ticker (str): Stock ticker
            company_name (str): Company name
            
        Returns:
            list: Filtered articles with full content
        """
        filtered_results = []
        errors = []
        
        # Extract URLs from search results
        search_text = research_results["search_results"]
        
        if isinstance(search_text, str):
            # Extract URLs using regex
            urls = re.findall(r'https?://[^\s]+', search_text)
        else:
            # Assume structured results with URLs
            urls = [item.get('url') for item in search_text if 'url' in item]
        
        for url in urls[:20]:  # Limit to first 20 URLs for efficiency
            # Fetch article content
            content, error = self.fetch_article_content(url)
            
            if error:
                errors.append(error)
                continue
                
            if not content:
                continue
            
            # Check relevance using first part of the article
            is_relevant, explanation = self.check_relevance(content, ticker, company_name)
            
            if is_relevant:
                filtered_results.append({
                    'url': url,
                    'content': content,
                    'explanation': explanation
                })
            
            if len(filtered_results) >= MAX_FILTERED_ARTICLES:
                break
        
        return {
            "ticker": ticker,
            "company_name": company_name,
            "filtered_articles": filtered_results,
            "errors": errors
        }

# # Test the filtering system
# if __name__ == "__main__":
#     from research import ResearchAgent
    
#     research_agent = ResearchAgent()
#     filtering_system = FilteringSystem()
    
#     research_results = research_agent.research("AAPL", "Apple Inc.")
#     filtered_results = filtering_system.filter(research_results, "AAPL", "Apple Inc.")
    
#     print(f"Found {len(filtered_results['filtered_articles'])} relevant articles")
#     for i, article in enumerate(filtered_results['filtered_articles']):
#         print(f"Article {i+1}: {article['url']}")
#         print(f"Explanation: {article['explanation']}")
#         print("---")
