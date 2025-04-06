# tests/test_workflow.py
import unittest
from graph.workflow import analyze_stock

class TestWorkflow(unittest.TestCase):
    def test_full_workflow(self):
        result = analyze_stock("AAPL", "Apple Inc.")
        
        # Check for errors
        self.assertNotIn("error", result)
        
        # Check result structure
        self.assertIn("recommendation_results", result)
        
        # Check recommendation
        recommendation = result["recommendation_results"]
        self.assertIn("ticker", recommendation)
        self.assertIn("recommendation", recommendation)
        self.assertIn("score", recommendation)
        
        # Check score
        score = recommendation["score"]
        self.assertTrue(0 <= score.overall_score <= 100)
        self.assertIn(score.investment_recommendation, ["Buy", "Hold", "Sell"])

if __name__ == "__main__":
    unittest.main()