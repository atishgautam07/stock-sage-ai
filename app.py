# app.py

import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Stock Analysis Multi-Agent System",
    page_icon="📈",
    layout="wide"
)

# App title
st.title("Stock Analysis Multi-Agent System")
st.markdown("### Analyze stocks using AI agents and LangChain")

# Sidebar for inputs
with st.sidebar:
    st.header("Input Parameters")
    
    # Stock selection input
    stocks_input = st.text_area(
        "Enter stock symbols (comma separated, max 10):",
        value="AAPL, MSFT, GOOGL",
        help="Enter up to 10 stock symbols separated by commas"
    )
    
    # Analysis timeframe
    timeframe = st.selectbox(
        "Analysis timeframe:",
        options=["1 week", "1 month", "3 months", "6 months"],
        index=1
    )
    
    # Run analysis button
    run_analysis = st.button("Run Analysis", type="primary")

# Main content area
if run_analysis:
    # Parse stock symbols
    stocks = [s.strip() for s in stocks_input.split(",") if s.strip()]
    
    if len(stocks) > 10:
        st.error("Please enter at most 10 stock symbols.")
    else:
        st.info(f"Starting analysis for: {', '.join(stocks)}")
        
        # Placeholder for the analysis workflow
        with st.expander("Research Progress", expanded=True):
            research_tab, filter_tab, extract_tab, score_tab = st.tabs([
                "1. Research", "2. Filter", "3. Extract", "4. Score"
            ])
            
            with research_tab:
                st.markdown("### Research Agent")
                st.info("Gathering news and financial data...")
                # This is where we'll integrate the Research Agent
                
            with filter_tab:
                st.markdown("### Filtering Node")
                st.info("Filtering relevant content...")
                # This is where we'll integrate the Filtering Node
                
            with extract_tab:
                st.markdown("### Extraction Agent")
                st.info("Extracting key insights...")
                # This is where we'll integrate the Extraction Agent
                
            with score_tab:
                st.markdown("### Scoring Node")
                st.info("Calculating investment scores...")
                # This is where we'll integrate the Scoring Node
        
        # Results placeholder
        st.markdown("## Analysis Results")
        st.info("Results will appear here after analysis is complete.")
else:
    st.info("Enter stock symbols and click 'Run Analysis' to begin.")

# Footer
st.markdown("---")
st.markdown("Stock Analysis Multi-Agent System | Built with LangChain and Streamlit")