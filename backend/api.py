from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from graph.workflow import analyze_stock
import uvicorn
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Stock Analyzer Agent")

class StockRequest(BaseModel):
    ticker: str
    company_name: str

@app.post("/analyze")
async def analyze(request: StockRequest):
    """Endpoint to analyze a stock based on ticker and company name"""
    logger.info(f"Received analysis request for {request.ticker} ({request.company_name})")
    try:
        result = analyze_stock(request.ticker, request.company_name)
        return result
    except Exception as e:
        logger.error(f"Error analyzing stock {request.ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)