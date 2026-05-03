import streamlit as st
st.set_page_config(page_title="Stock Dashboard", layout="wide")

import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.title("📈 Stock Market Dashboard")

ticker = st.text_input("Enter Stock Symbol", "TCS.NS")

def load_data(symbol):
    try:
        df = yf.download(symbol, period="1y", progress=False)
        return df
    except:
        return pd.DataFrame()

df = load_data(ticker)

if df.empty:
    st.warning("⚠️ AAPL not working sometimes on cloud. Try:")
    st.code("TCS.NS | RELIANCE.NS | INFY.NS")
else:
    st.success("✅ Data Loaded")

    st.dataframe(df.tail())

    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    )])

    st.plotly_chart(fig, use_container_width=True)
