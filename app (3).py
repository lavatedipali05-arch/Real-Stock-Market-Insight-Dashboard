import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Stock Dashboard", layout="wide")

st.title("📈 Stock Data Dashboard & Buy/Sell Signals")

# --------------------------
# INPUT
# --------------------------
ticker_input = st.text_input(
    "Enter Stock Symbol (e.g. TCS.NS, INFY.NS, RELIANCE.NS)",
    "TCS.NS"
)

# --------------------------
# LOAD DATA
# --------------------------
@st.cache_data
def load_data(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d")
        if df.empty:
            return None
        return df
    except Exception:
        return None

df = load_data(ticker_input)

# --------------------------
# ERROR HANDLING
# --------------------------
if df is None:
    st.error("❌ No data found. Use correct NSE format like TCS.NS, INFY.NS")
    st.stop()

# --------------------------
# CALCULATIONS
# --------------------------
df["MA20"] = df["Close"].rolling(20).mean()
df["MA50"] = df["Close"].rolling(50).mean()

# BUY/SELL SIGNAL
df["Signal"] = 0
df.loc[df["MA20"] > df["MA50"], "Signal"] = 1
df["Position"] = df["Signal"].diff()

# --------------------------
# LAYOUT
# --------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Price Chart")
    st.line_chart(df[["Close", "MA20", "MA50"]])

with col2:
    st.subheader("📍 Latest Signal")

    last_signal = df["Position"].iloc[-1]

    if last_signal == 1:
        st.success("🟢 BUY Signal")
    elif last_signal == -1:
        st.error("🔴 SELL Signal")
    else:
        st.warning("⚪ HOLD")

# --------------------------
# DETAILS
# --------------------------
st.subheader("📋 Recent Data")
st.dataframe(df.tail())

# --------------------------
# EXTRA INSIGHTS
# --------------------------
st.subheader("📈 Insights")

latest_price = df["Close"].iloc[-1]
ma20 = df["MA20"].iloc[-1]
ma50 = df["MA50"].iloc[-1]

st.write(f"Current Price: {latest_price:.2f}")
st.write(f"20-Day MA: {ma20:.2f}")
st.write(f"50-Day MA: {ma50:.2f}")

if ma20 > ma50:
    st.success("Trend: Bullish 📈")
else:
    st.error("Trend: Bearish 📉")
    @st.cache_data
def load_data(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d")

        if df.empty:
            return None

        # ✅ FIX: flatten columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        return df

    except Exception:
        return None
