import streamlit as st
import pandas as pd

st.title("📊 Stock Data Dashboard")

try:
    df = pd.read_csv("stock_data.csv")

    st.subheader("Data Preview")
    st.dataframe(df)

    if "Close" in df.columns:
        st.subheader("Stock Close Price Chart")
        st.line_chart(df["Close"])
    else:
        st.error("❌ 'Close' column not found in CSV")

except FileNotFoundError:
    st.error("❌ stock_data.csv file missing in repo")

import plotly.graph_objects as go

st.subheader("📊 Candlestick Chart")

fig = go.Figure(data=[go.Candlestick(
    x=df.index,
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close']
)])

fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Price',
    template='plotly_dark'
)

st.plotly_chart(fig, use_container_width=True)

required_cols = ['Open', 'High', 'Low', 'Close']

if not all(col in df.columns for col in required_cols):
    st.error("❌ Required OHLC data not available")
    st.stop()
