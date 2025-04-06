from langchain_openai import ChatOpenAI
from langchain.tools import TavilySearchResults
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY, TAVILY_API_KEY, LLM_MODEL, MAX_SEARCH_RESULTS

class ResearchAgent:
    def __init__(self):
        """
        Initialize the Research Agent with API keys and tools.
        """
        # Set API keys
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
        os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
        
        # Initialize Tavily search tool
        self.search_tool = TavilySearchResults(max_results=MAX_SEARCH_RESULTS)
        
        # Initialize LLM
        self.llm = ChatOpenAI(temperature=0, model=LLM_MODEL)
        
        # Create system prompt
        system_prompt = """
        You are a financial researcher gathering information about companies for investment analysis.
        
        Focus on finding recent and relevant information about the company such as:
        1. Quarterly financial results and earnings
        2. Analyst ratings and price targets
        3. Business developments, product launches, partnerships
        4. Market trends affecting the company
        5. Competitive landscape
        
        Only consider information relevant for short-term investment decisions (last 3 months).
        Make sure to search for the most recent information available.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Research {ticker} ({company_name}) for short-term investment analysis."),
            ("ai", "{agent_scratchpad}")
        ])
        
        # Create agent
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=[self.search_tool],
            prompt=prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=[self.search_tool],
            verbose=True,
            handle_parsing_errors=True
        )
    
    def research(self, ticker, company_name):
        """
        Research a stock by ticker and company name.
        
        Args:
            ticker (str): Stock ticker symbol
            company_name (str): Company name
            
        Returns:
            dict: Search results with metadata
        """
        # Run the agent
        result = self.agent_executor.invoke({
            "ticker": ticker,
            "company_name": company_name
        })
        
        return {
            "ticker": ticker,
            "company_name": company_name,
            "search_results": result["output"],
            "raw_results": result
        }

# # Test the agent
# if __name__ == "__main__":
#     agent = ResearchAgent()
#     result = agent.research("AAPL", "Apple Inc.")
#     print(result)

