import streamlit as st

st.set_page_config(page_title="Stock Dashboard", layout="wide")

import yfinance as yf
import plotly.graph_objects as go

st.title("📈 Stock Market Dashboard")

# Input
ticker = st.text_input("Enter Stock Symbol", "AAPL")

# Load data
df = yf.download(ticker, period="1y")

st.subheader("📊 Data Preview")
st.dataframe(df.tail())

# Candlestick chart
st.subheader("📊 Candlestick Chart")

fig = go.Figure(data=[go.Candlestick(
    x=df.index,
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close']
)])

st.plotly_chart(fig, use_container_width=True)

# Close price
st.subheader("📈 Close Price")
st.line_chart(df["Close"])
