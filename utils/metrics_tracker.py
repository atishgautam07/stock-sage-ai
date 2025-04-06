# utils/metrics_tracker.py

import time
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime

class ResearchMetricsTracker:
    """
    Tracks success metrics for the Research Agent.
    """
    
    def __init__(self):
        """Initialize the metrics tracker."""
        self.metrics = {
            "requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_execution_time": 0,
            "avg_execution_time": 0,
            "stocks_researched": set(),
            "research_timestamps": [],
            "error_types": {},
            "source_domains": {},
            "data_freshness": {}
        }
    
    def start_request(self) -> float:
        """
        Start timing a new request.
        
        Returns:
            Start time in seconds
        """
        self.metrics["requests"] += 1
        return time.time()
    
    def end_request(self, start_time: float, result: Dict[str, Any], success: bool = True) -> None:
        """
        End timing a request and update metrics.
        
        Args:
            start_time: Start time from start_request
            result: Research result dictionary
            success: Whether the request was successful
        """
        execution_time = time.time() - start_time
        self.metrics["total_execution_time"] += execution_time
        
        if success:
            self.metrics["successful_requests"] += 1
            
            # Track stock symbol
            symbol = result.get("symbol")
            if symbol:
                self.metrics["stocks_researched"].add(symbol)
            
            # Track timestamp
            self.metrics["research_timestamps"].append(datetime.now())
            
            # Track source domains
            if "research_data" in result and "intermediate_steps" in result["research_data"]:
                for step in result["research_data"]["intermediate_steps"]:
                    if hasattr(step, "observation") and isinstance(step.observation, list):
                        for item in step.observation:
                            if isinstance(item, dict) and "source" in item:
                                domain = item["source"].split('/')[2] if '://' in item["source"] else item["source"]
                                self.metrics["source_domains"][domain] = self.metrics["source_domains"].get(domain, 0) + 1
            
            # Track data freshness
            if "financial_data" in result:
                fin_data = result["financial_data"]
                last_updated = fin_data.get("last_updated")
                if last_updated:
                    self.metrics["data_freshness"][symbol] = last_updated
        else:
            self.metrics["failed_requests"] += 1
            
            # Track error types
            error = result.get("error", "Unknown error")
            error_type = error.split(':')[0] if ':' in error else error
            self.metrics["error_types"][error_type] = self.metrics["error_types"].get(error_type, 0) + 1
        
        # Update average execution time
        self.metrics["avg_execution_time"] = (
            self.metrics["total_execution_time"] / 
            (self.metrics["successful_requests"] + self.metrics["failed_requests"])
        )
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all tracked metrics.
        
        Returns:
            Dictionary with metrics summary
        """
        return {
            "requests": self.metrics["requests"],
            "success_rate": (self.metrics["successful_requests"] / self.metrics["requests"]) * 100 if self.metrics["requests"] > 0 else 0,
            "avg_execution_time": self.metrics["avg_execution_time"],
            "unique_stocks_researched": len(self.metrics["stocks_researched"]),
            "top_source_domains": dict(sorted(self.metrics["source_domains"].items(), key=lambda x: x[1], reverse=True)[:5]),
            "top_error_types": dict(sorted(self.metrics["error_types"].items(), key=lambda x: x[1], reverse=True)[:3]),
            "last_research_time": max(self.metrics["research_timestamps"]) if self.metrics["research_timestamps"] else None
        }
    
    def get_detailed_report(self) -> Dict[str, Any]:
        """
        Get a detailed metrics report including all tracked data.
        
        Returns:
            Dictionary with detailed metrics
        """
        return {
            "summary": self.get_metrics_summary(),
            "raw_metrics": {
                k: list(v) if isinstance(v, set) else v 
                for k, v in self.metrics.items()
            }
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self.__init__()