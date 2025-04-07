# agents/extraction.py
from langchain_openai import ChatOpenAI
from langchain.chains import create_extraction_chain
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LLM_MODEL

class ExtractionAgent:
    def __init__(self):
        """
        Initialize the Extraction Agent with necessary components.
        """
        # Initialize LLM
        self.llm = ChatOpenAI(temperature=0, model=LLM_MODEL)
        
        # Define extraction schema
        self.extraction_schema = {
            "title": "StockInsights",
            "description": "Extracted insights about a stock from financial news and reports",
            "type": "object",
            "properties": {
                "financial_metrics": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "metric_name": {"type": "string"},
                            "value": {"type": "string"},
                            "comparison": {"type": "string"},
                            "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]}
                        }
                    }
                },
                "analyst_opinions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "analyst_or_firm": {"type": "string"},
                            "rating": {"type": "string"},
                            "target_price": {"type": "string"},
                            "previous_rating": {"type": "string"},
                            "previous_target": {"type": "string"}
                        }
                    }
                },
                "business_developments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "event_type": {"type": "string"},
                            "description": {"type": "string"},
                            "expected_impact": {"type": "string"},
                            "timeline": {"type": "string"}
                        }
                    }
                },
                "market_sentiment": {
                    "type": "object",
                    "properties": {
                        "overall_sentiment": {"type": "string", "enum": ["bullish", "bearish", "neutral"]},
                        "trading_volume": {"type": "string"},
                        "price_movement": {"type": "string"},
                        "volatility": {"type": "string"}
                    }
                },
                "risk_factors": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "risk_type": {"type": "string"},
                            "description": {"type": "string"},
                            "severity": {"type": "string", "enum": ["high", "medium", "low"]}
                        }
                    }
                }
            }
        }
        
        # Create extraction chain
        # extraction_function = format_tool_to_openai_function({
        #     "name": "extract_stock_insights",
        #     "description": "Extract structured insights from financial text about a stock",
        #     "parameters": self.extraction_schema
        # })
        extraction_function = convert_to_openai_function({
            "name": "extract_stock_insights",
            "description": "Extract structured insights from financial text about a stock",
            "parameters": self.extraction_schema
        })
        
        self.extraction_llm = self.llm.bind(
            functions=[extraction_function],
            function_call={"name": "extract_stock_insights"}
        )
        
        self.parser = JsonOutputFunctionsParser()
        
        # Create summary chain
        summary_template = """
        You are a financial analyst specializing in extracting key insights for stock investors.
        
        Analyze the following article about {ticker} ({company_name}) and extract the most important 
        information for a short-term investor (last 3 month horizon).
        
        Focus on:
        1. Recent financial results
        2. Analyst ratings and price targets
        3. Business developments and news
        4. Market sentiment and trading patterns
        5. Key risk factors
        
        Article:
        {text}
        
        Provide a concise summary of the key investment insights:
        """
        
        self.summary_prompt = PromptTemplate(
            input_variables=["ticker", "company_name", "text"],
            template=summary_template
        )
        
        self.summary_chain = PromptTemplate.from_template(summary_template) | self.llm | StrOutputParser()
    
    def extract(self, article, ticker, company_name):
        """
        Extract structured insights from an article.
        
        Args:
            article (dict): Article content and metadata
            ticker (str): Stock ticker symbol
            company_name (str): Company name
            
        Returns:
            dict: Structured insights
        """
        # Use the first 4000 chars of the article to avoid token limits
        content = article['content'][:4000]
        
        # Extract structured data
        chain = self.extraction_llm | self.parser
        
        try:
            structured_insights = chain.invoke(
                f"Extract insights about {ticker} ({company_name}) from this article: {content}"
            )
        except Exception as e:
            print(f"Error in extraction: {str(e)}")
            structured_insights = {}
        
        # Generate summary
        summary = self.summary_chain.invoke({
            "ticker": ticker,
            "company_name": company_name,
            "text": content
        })
        
        return {
            "url": article['url'],
            "structured_insights": structured_insights,
            "summary": summary
        }
    
    def process(self, filtered_results):
        """
        Extract insights from multiple articles.
        
        Args:
            filtered_results (dict): Results from FilteringSystem
            
        Returns:
            dict: Extracted insights for each article
        """
        ticker = filtered_results["ticker"]
        company_name = filtered_results["company_name"]
        filtered_articles = filtered_results["filtered_articles"]
        
        extracted_insights = []
        for article in filtered_articles:
            insights = self.extract(article, ticker, company_name)
            extracted_insights.append(insights)
        
        return {
            "ticker": ticker,
            "company_name": company_name,
            "extracted_insights": extracted_insights
        }

# # Test the extraction agent
# if __name__ == "__main__":
#     from research import ResearchAgent
#     from filtering import FilteringSystem
    
#     research_agent = ResearchAgent()
#     filtering_system = FilteringSystem()
#     extraction_agent = ExtractionAgent()
    
#     research_results = research_agent.research("AAPL", "Apple Inc.")
#     filtered_results = filtering_system.filter(research_results, "AAPL", "Apple Inc.")
#     extraction_results = extraction_agent.process(filtered_results)
    
#     print(f"Extracted insights from {len(extraction_results['extracted_insights'])} articles")
#     for i, insight in enumerate(extraction_results['extracted_insights']):
#         print(f"Article {i+1}: {insight['url']}")
#         print(f"Summary: {insight['summary']}")
#         print("---")

