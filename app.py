import streamlit as st

st.set_page_config(page_title="Stock Dashboard", layout="wide")

import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.title("📈 Stock Market Dashboard")

# Input
ticker = st.text_input("Enter Stock Symbol", "AAPL")

if ticker:
    try:
        df = yf.download(ticker, period="1y")

        # 👉 IMPORTANT FIX
        if df.empty:
            st.error("❌ No data found. Try different stock (e.g. TCS.NS, RELIANCE.NS)")
        else:
            st.success("✅ Data Loaded Successfully")

            st.subheader("📊 Data Preview")
            st.dataframe(df.tail())

            # Candlestick
            fig = go.Figure(data=[go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close']
            )])

            st.subheader("🕯️ Candlestick Chart")
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error: {e}")
