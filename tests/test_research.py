# tests/test_research.py
import unittest
from agents.research import ResearchAgent

class TestResearchAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ResearchAgent()
    
    def test_research(self):
        result = self.agent.research("AAPL", "Apple Inc.")
        
        # Check result structure
        self.assertIn("ticker", result)
        self.assertIn("company_name", result)
        self.assertIn("search_results", result)
        
        # Check values
        self.assertEqual(result["ticker"], "AAPL")
        self.assertEqual(result["company_name"], "Apple Inc.")
        self.assertIsNotNone(result["search_results"])

if __name__ == "__main__":
    unittest.main()