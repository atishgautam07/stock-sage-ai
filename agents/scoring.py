# agents/scoring.py
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from typing import Dict
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LLM_MODEL

class StockScore(BaseModel):
    financial_health_score: int = Field(description="Score from 1-10 assessing financial health based on metrics")
    growth_potential_score: int = Field(description="Score from 1-10 assessing growth potential")
    analyst_sentiment_score: int = Field(description="Score from 1-10 based on analyst opinions")
    momentum_score: int = Field(description="Score from 1-10 assessing price and trading momentum")
    risk_score: int = Field(description="Score from 1-10 assessing risk level (1=highest risk, 10=lowest risk)")
    overall_score: int = Field(description="Overall investment score from 1-100")
    reasoning: Dict[str, str] = Field(description="Brief reasoning for each score component")
    investment_recommendation: str = Field(description="Investment recommendation: Buy, Hold, or Sell")
    confidence_level: str = Field(description="Confidence level: High, Medium, or Low")

class ScoringMechanism:
    def __init__(self):
        """
        Initialize the Scoring Mechanism with necessary components.
        """
        # Initialize LLM
        self.llm = ChatOpenAI(temperature=0, model=LLM_MODEL)
        
        # Create parser
        self.parser = PydanticOutputParser(pydantic_object=StockScore)
        
        # Create scoring prompt
        scoring_template = """
        You are a financial analyst specializing in short-term stock evaluation.
        
        Based on the following insights about {ticker} ({company_name}), evaluate its investment potential 
        for a short-term horizon (last 3 months).
        
        Company: {company_name} ({ticker})
        
        INSIGHTS:
        {insights}
        
        Analyze these insights and provide an investment score using the following format:
        
        {format_instructions}
        """
        
        self.scoring_prompt = PromptTemplate(
            input_variables=["ticker", "company_name", "insights"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
            template=scoring_template
        )
        
        # self.scoring_chain = LLMChain(
        #     llm=self.llm,
        #     prompt=self.scoring_prompt,
        #     output_parser=self.parser
        # )
        self.scoring_chain = self.scoring_prompt | self.llm | self.parser
    
    def score(self, extraction_results):
        """
        Score a stock based on extracted insights.
        
        Args:
            extraction_results (dict): Results from ExtractionAgent
            
        Returns:
            dict: Scored results including StockScore
        """
        ticker = extraction_results["ticker"]
        company_name = extraction_results["company_name"]
        extracted_insights = extraction_results["extracted_insights"]
        
        # Format insights for the prompt
        insights_text = ""
        
        for i, article_insights in enumerate(extracted_insights, 1):
            insights_text += f"ARTICLE {i}:\n"
            insights_text += f"URL: {article_insights['url']}\n"
            insights_text += f"SUMMARY: {article_insights['summary']}\n"
            
            structured = article_insights['structured_insights']
            if structured:
                if 'financial_metrics' in structured and structured['financial_metrics']:
                    insights_text += "FINANCIAL METRICS:\n"
                    for metric in structured['financial_metrics']:
                        insights_text += f"- {metric.get('metric_name', 'N/A')}: {metric.get('value', 'N/A')} ({metric.get('sentiment', 'N/A')})\n"
                
                if 'analyst_opinions' in structured and structured['analyst_opinions']:
                    insights_text += "ANALYST OPINIONS:\n"
                    for opinion in structured['analyst_opinions']:
                        insights_text += f"- {opinion.get('analyst_or_firm', 'N/A')}: Rating: {opinion.get('rating', 'N/A')}, Target: {opinion.get('target_price', 'N/A')}\n"
                
                if 'business_developments' in structured and structured['business_developments']:
                    insights_text += "BUSINESS DEVELOPMENTS:\n"
                    for dev in structured['business_developments']:
                        insights_text += f"- {dev.get('event_type', 'N/A')}: {dev.get('description', 'N/A')}\n"
                
                if 'market_sentiment' in structured and structured['market_sentiment']:
                    sentiment = structured['market_sentiment']
                    insights_text += f"MARKET SENTIMENT: {sentiment.get('overall_sentiment', 'N/A')}\n"
                
                if 'risk_factors' in structured and structured['risk_factors']:
                    insights_text += "RISK FACTORS:\n"
                    for risk in structured['risk_factors']:
                        insights_text += f"- {risk.get('risk_type', 'N/A')} ({risk.get('severity', 'N/A')}): {risk.get('description', 'N/A')}\n"
            
            insights_text += "\n---\n\n"
        
        # Get score
        result = self.scoring_chain.invoke({
            "ticker": ticker,
            "company_name": company_name,
            "insights": insights_text
        })
        
        return {
            "ticker": ticker,
            "company_name": company_name,
            "score": result,
            "extracted_insights": extracted_insights
        }

# # Test the scoring mechanism
# if __name__ == "__main__":
#     from research import ResearchAgent
#     from filtering import FilteringSystem
#     from extraction import ExtractionAgent
    
#     research_agent = ResearchAgent()
#     filtering_system = FilteringSystem()
#     extraction_agent = ExtractionAgent()
#     scoring_mechanism = ScoringMechanism()
    
#     research_results = research_agent.research("AAPL", "Apple Inc.")
#     filtered_results = filtering_system.filter(research_results, "AAPL", "Apple Inc.")
#     extraction_results = extraction_agent.process(filtered_results)
#     scoring_results = scoring_mechanism.score(extraction_results)
    
#     print(f"Overall Score: {scoring_results['score'].overall_score}/100")
#     print(f"Recommendation: {scoring_results['score'].investment_recommendation}")
#     print(f"Confidence: {scoring_results['score'].confidence_level}")
#     print("Score Components:")
#     print(f"- Financial Health: {scoring_results['score'].financial_health_score}/10")
#     print(f"- Growth Potential: {scoring_results['score'].growth_potential_score}/10")
#     print(f"- Analyst Sentiment: {scoring_results['score'].analyst_sentiment_score}/10")
#     print(f"- Momentum: {scoring_results['score'].momentum_score}/10")
#     print(f"- Risk: {scoring_results['score'].risk_score}/10")

