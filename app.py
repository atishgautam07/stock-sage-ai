import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
import os
import time
import json

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from graph.workflow import analyze_stock

def create_streamlit_app():
    st.set_page_config(
        page_title="AI Stock Analyst",
        page_icon="📈",
        layout="wide"
    )
    
    st.title("AI Stock Analyst")
    st.subheader("Intelligent stock analysis for short-term investments")
    
    # Sidebar for inputs
    st.sidebar.header("Enter Stock Information")
    
    # Default stocks
    default_stocks = [
        {"ticker": "AAPL", "company_name": "Apple Inc."},
        {"ticker": "MSFT", "company_name": "Microsoft Corporation"},
        {"ticker": "AMZN", "company_name": "Amazon.com, Inc."},
        {"ticker": "GOOGL", "company_name": "Alphabet Inc."},
        {"ticker": "META", "company_name": "Meta Platforms, Inc."}
    ]
    
    # Initialize session state
    if "stocks" not in st.session_state:
        st.session_state.stocks = default_stocks[:1]  # Start with just Apple
    
    if "results" not in st.session_state:
        st.session_state.results = {}
    
    if "current_analysis" not in st.session_state:
        st.session_state.current_analysis = None
    
    # Function to add a stock
    def add_stock():
        st.session_state.stocks.append({"ticker": "", "company_name": ""})
    
    # Function to remove a stock
    def remove_stock(index):
        st.session_state.stocks.pop(index)
    
    # Function to analyze stocks
    def start_analysis():
        st.session_state.current_analysis = 0
        st.session_state.results = {}
    
    # Display stock inputs
    for i, stock in enumerate(st.session_state.stocks):
        col1, col2, col3 = st.sidebar.columns([2, 2, 1])
        
        with col1:
            st.session_state.stocks[i]["ticker"] = st.text_input(
                f"Ticker {i+1}",
                value=stock["ticker"],
                key=f"ticker_{i}"
            )
        
        with col2:
            st.session_state.stocks[i]["company_name"] = st.text_input(
                f"Company {i+1}",
                value=stock["company_name"],
                key=f"company_{i}"
            )
        
        with col3:
            if st.button("🗑️", key=f"remove_{i}"):
                remove_stock(i)
                st.rerun()
    
    # Add stock button
    if len(st.session_state.stocks) < 10:
        st.sidebar.button("Add Stock", on_click=add_stock)
    
    # Analyze button
    if st.sidebar.button("Analyze Stocks"):
        valid_stocks = [
            stock for stock in st.session_state.stocks
            if stock["ticker"] and stock["company_name"]
        ]
        
        if not valid_stocks:
            st.sidebar.error("Please enter at least one stock.")
        else:
            st.session_state.stocks = valid_stocks
            start_analysis()
            st.rerun()
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["Analysis Process", "Results", "Portfolio View"])
    
    with tab1:
        if st.session_state.current_analysis is not None:
            # Display progress
            st.header("Analysis Progress")
            
            total_stocks = len(st.session_state.stocks)
            current_index = st.session_state.current_analysis
            
            if current_index < total_stocks:
                # Still analyzing
                progress = current_index / total_stocks
                st.progress(progress)
                
                current_stock = st.session_state.stocks[current_index]
                st.write(f"Analyzing {current_stock['ticker']} ({current_stock['company_name']})...")
                
                # Perform the analysis
                ticker = current_stock["ticker"]
                company_name = current_stock["company_name"]
                
                try:
                    # Display the process steps
                    process_status = st.empty()
                    
                    # Research step
                    process_status.write("Step 1: Researching stock information...")
                    
                    # Start the analysis
                    result = analyze_stock(ticker, company_name)
                    
                    if "error" in result and result["error"]:
                        st.error(f"Error analyzing {ticker}: {result['error']}")
                    else:
                        st.session_state.results[ticker] = result
                        st.success(f"Analysis of {ticker} complete!")
                    
                    # Move to the next stock
                    st.session_state.current_analysis += 1
                    time.sleep(1)  # Give the user time to see the success message
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.session_state.current_analysis = None
            
            else:
                # All stocks analyzed
                st.success("All stocks analyzed!")
                st.session_state.current_analysis = None
        
        else:
            st.info("Click 'Analyze Stocks' to start the analysis.")
    
    with tab2:
        if st.session_state.results:
            st.header("Analysis Results")
            
            # Create tabs for each stock
            stock_tabs = st.tabs([ticker for ticker in st.session_state.results.keys()])
            
            for i, ticker in enumerate(st.session_state.results.keys()):
                with stock_tabs[i]:
                    result = st.session_state.results[ticker]
                    recommendation = result["recommendation_results"]
                    score = recommendation["score"]
                    
                    # Display score and recommendation
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        # Score card
                        st.subheader(f"{ticker} - {score.overall_score}/100")
                        st.write(f"**Recommendation:** {score.investment_recommendation}")
                        st.write(f"**Confidence:** {score.confidence_level}")
                        
                        # Radar chart for score components
                        categories = ['Financial Health', 'Growth Potential', 
                                      'Analyst Sentiment', 'Momentum', 'Risk Level']
                        values = [score.financial_health_score, score.growth_potential_score,
                                  score.analyst_sentiment_score, score.momentum_score, score.risk_score]
                        
                        # Close the loop for the radar chart
                        categories = categories + [categories[0]]
                        values = values + [values[0]]
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatterpolar(
                            r=values,
                            theta=categories,
                            fill='toself',
                            name=ticker
                        ))
                        
                        fig.update_layout(
                            polar=dict(
                                radialaxis=dict(
                                    visible=True,
                                    range=[0, 10]
                                )
                            ),
                            height=400,
                            margin=dict(l=10, r=10, t=30, b=10)
                        )
                        
                        st.plotly_chart(fig)
                        
                        # Display reasoning
                        st.subheader("Score Reasoning")
                        for category, reasoning in score.reasoning.items():
                            st.write(f"**{category}:** {reasoning}")
                    
                    with col2:
                        # Detailed recommendation
                        st.subheader("Investment Recommendation")
                        st.markdown(recommendation["recommendation"])
                        
                        # Show sources
                        st.subheader("Information Sources")
                        extraction_results = result["extraction_results"]
                        for i, insight in enumerate(extraction_results["extracted_insights"]):
                            with st.expander(f"Source {i+1}: {insight['url']}"):
                                st.write("**Summary:**")
                                st.write(insight["summary"])
        
        else:
            st.info("Analysis results will appear here after processing.")
    
    with tab3:
        if st.session_state.results:
            st.header("Portfolio View")
            
            # Create a DataFrame with stock scores
            scores_data = []
            for ticker, result in st.session_state.results.items():
                recommendation = result["recommendation_results"]
                score = recommendation["score"]
                
                scores_data.append({
                    "Ticker": ticker,
                    "Company": result["recommendation_results"]["company_name"],
                    "Overall Score": score.overall_score,
                    "Financial Health": score.financial_health_score,
                    "Growth Potential": score.growth_potential_score,
                    "Analyst Sentiment": score.analyst_sentiment_score,
                    "Momentum": score.momentum_score,
                    "Risk Level": score.risk_score,
                    "Recommendation": score.investment_recommendation,
                    "Confidence": score.confidence_level
                })
            
            scores_df = pd.DataFrame(scores_data)
            
            # Display scores table
            st.dataframe(scores_df.sort_values("Overall Score", ascending=False))
            
            # Create a horizontal bar chart of overall scores
            bar_data = scores_df.sort_values("Overall Score")
            
            fig = go.Figure()
            
            # Add color based on recommendation
            colors = bar_data["Recommendation"].map({
                "Buy": "green",
                "Hold": "orange",
                "Sell": "red"
            }).fillna("gray")
            
            fig.add_trace(go.Bar(
                x=bar_data["Overall Score"],
                y=bar_data["Ticker"],
                orientation='h',
                marker_color=colors,
                text=bar_data["Overall Score"],
                textposition='auto'
            ))
            
            fig.update_layout(
                title="Stock Rankings",
                xaxis_title="Overall Score",
                yaxis_title="Stock",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Portfolio allocation suggestion
            st.subheader("Portfolio Allocation Suggestion")
            
            # Simple allocation strategy based on scores
            scores = scores_df[["Ticker", "Overall Score"]].copy()
            scores["Normalized"] = scores["Overall Score"] / scores["Overall Score"].sum()
            
            # Only allocate to stocks with positive recommendations
            buy_stocks = scores_df[scores_df["Recommendation"] == "Buy"]
            
            if len(buy_stocks) > 0:
                buy_tickers = buy_stocks["Ticker"].tolist()
                scores["Allocation"] = scores.apply(
                    lambda x: x["Normalized"] / sum(scores[scores["Ticker"].isin(buy_tickers)]["Normalized"]) * 100 
                    if x["Ticker"] in buy_tickers else 0,
                    axis=1
                )
                
                # Create pie chart
                fig = go.Figure(data=[go.Pie(
                    labels=scores["Ticker"],
                    values=scores["Allocation"],
                    hole=.3,
                    textinfo='label+percent'
                )])
                
                fig.update_layout(title="Recommended Portfolio Allocation")
                st.plotly_chart(fig)
                
                # Display allocation table
                allocation_df = scores[["Ticker", "Allocation"]].copy()
                allocation_df["Allocation"] = allocation_df["Allocation"].round(2).astype(str) + "%"
                allocation_df = allocation_df.sort_values("Allocation", ascending=False)
                
                st.table(allocation_df.set_index("Ticker"))
            else:
                st.warning("No 'Buy' recommendations found for portfolio allocation.")
        
        else:
            st.info("Portfolio view will appear here after analysis.")
    
    # Add timestamp
    st.sidebar.write(f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    create_streamlit_app()