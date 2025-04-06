from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LLM_MODEL

class RecommendationAgent:
    def __init__(self):
        """
        Initialize the Recommendation Agent with necessary components.
        """
        # Initialize LLM
        self.llm = ChatOpenAI(temperature=0, model=LLM_MODEL)
        
        # Create recommendation prompt
        recommendation_template = """
        You are a financial advisor specializing in short-term stock investments.
        
        Based on the following scores and insights for {ticker} ({company_name}), 
        provide a detailed investment recommendation.
        
        SCORES:
        {scores}
        
        RECENT INSIGHTS:
        {key_insights}
        
        IMPORTANT GUIDELINES:
        1. DO NOT invent or hallucinate any information not present in the data above
        2. Price targets MUST be realistic and justified based on current price
        3. Always explain your reasoning using ONLY the provided data
        4. If the data is insufficient to make a recommendation on any aspect, explicitly state this

        Provide a comprehensive recommendation that includes:
        1. Investment thesis (2-3 paragraphs) based ONLY on provided data
        2. Key supporting factors (bullet points) from the provided insights
        3. Potential risks (bullet points) mentioned in the insights
        4. Suggested entry points or conditions (with explicit reference to current price)
        5. Suggested exit strategy or price targets (with explicit reference to current price)
        6. Timeline considerations for short-term horizon (1-3 months)

        For all price targets, include your calculation methodology showing how you arrived at the specific number from the current price.
        Keep your recommendation focused on short-term investment horizon (last 3 months).
        """
        
        self.recommendation_prompt = PromptTemplate(
            input_variables=["ticker", "company_name", "scores", "key_insights"],
            template=recommendation_template
        )
        
        # self.recommendation_chain = LLMChain(
        #     llm=self.llm,
        #     prompt=self.recommendation_prompt
        # )
        self.recommendation_chain = self.recommendation_prompt | self.llm
    
    def recommend(self, scoring_results):
        """
        Generate investment recommendation for a stock.
        
        Args:
            scoring_results (dict): Results from ScoringMechanism
            
        Returns:
            dict: Detailed recommendation
        """
        ticker = scoring_results["ticker"]
        company_name = scoring_results["company_name"]
        score = scoring_results["score"]
        extracted_insights = scoring_results["extracted_insights"]
        
        # Format scores
        scores_text = f"""
        Financial Health: {score.financial_health_score}/10 - {score.reasoning.get('financial_health_score', '')}
        Growth Potential: {score.growth_potential_score}/10 - {score.reasoning.get('growth_potential_score', '')}
        Analyst Sentiment: {score.analyst_sentiment_score}/10 - {score.reasoning.get('analyst_sentiment_score', '')}
        Momentum: {score.momentum_score}/10 - {score.reasoning.get('momentum_score', '')}
        Risk Level: {score.risk_score}/10 - {score.reasoning.get('risk_score', '')}
        
        OVERALL SCORE: {score.overall_score}/100
        RECOMMENDATION: {score.investment_recommendation}
        CONFIDENCE: {score.confidence_level}
        """
        
        # Extract key insights from each article
        key_insights = ""
        for i, insight in enumerate(extracted_insights[:3], 1):  # Use up to 3 articles
            key_insights += f"INSIGHT {i}:\n{insight['summary']}\n\n"
        
        # Generate recommendation
        result = self.recommendation_chain.invoke({
            "ticker": ticker,
            "company_name": company_name,
            "scores": scores_text,
            "key_insights": key_insights
        })
        
        return {
            "ticker": ticker,
            "company_name": company_name,
            "recommendation": result.content,
            "score": score
        }

# Test the recommendation agent
# if __name__ == "__main__":
#     from research import ResearchAgent
#     from filtering import FilteringSystem
#     from extraction import ExtractionAgent
#     from scoring import ScoringMechanism
    
#     research_agent = ResearchAgent()
#     filtering_system = FilteringSystem()
#     extraction_agent = ExtractionAgent()
#     scoring_mechanism = ScoringMechanism()
#     recommendation_agent = RecommendationAgent()
    
#     research_results = research_agent.research("AAPL", "Apple Inc.")
#     filtered_results = filtering_system.filter(research_results, "AAPL", "Apple Inc.")
#     extraction_results = extraction_agent.process(filtered_results)
#     scoring_results = scoring_mechanism.score(extraction_results)
#     recommendation_results = recommendation_agent.recommend(scoring_results)
    
#     print(f"Recommendation for {recommendation_results['ticker']}:")
#     print(recommendation_results['recommendation'])
