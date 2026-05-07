
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from ta.momentum import RSIIndicator
from ta.trend import MACD
from sklearn.linear_model import LinearRegression

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Real Stock Market Dashboard",
    layout="wide"
)

st.title("🚀 Pro Real-Time Stock Dashboard")

# -----------------------------
# SIDEBAR
# -----------------------------
stock = st.sidebar.text_input(
    "Stock Symbol",
    "RELIANCE.NS"
)

period = st.sidebar.selectbox(
    "Select Period",
    ["1mo", "3mo", "6mo", "1y"]
)

# -----------------------------
# DATA LOAD
# -----------------------------
df = yf.download(stock, period=period)

if df.empty:
    st.error("No stock data found.")
    st.stop()

# -----------------------------
# FIX MULTI INDEX
# -----------------------------
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

# -----------------------------
# INDICATORS
# -----------------------------
df["SMA20"] = df["Close"].rolling(20).mean()
df["SMA50"] = df["Close"].rolling(50).mean()

rsi = RSIIndicator(close=df["Close"])
df["RSI"] = rsi.rsi()

macd = MACD(close=df["Close"])
df["MACD"] = macd.macd()
df["Signal_Line"] = macd.macd_signal()

# -----------------------------
# CANDLESTICK CHART
# -----------------------------
st.subheader(f"📈 {stock} Candlestick Chart")

fig = go.Figure()

fig.add_trace(
    go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Candlestick"
    )
)

fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["SMA20"],
        name="SMA20"
    )
)

fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["SMA50"],
        name="SMA50"
    )
)

fig.update_layout(
    xaxis_rangeslider_visible=False,
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# RSI CHART
# -----------------------------
st.subheader("📊 RSI Indicator")

rsi_fig = go.Figure()

rsi_fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["RSI"],
        name="RSI"
    )
)

rsi_fig.add_hline(y=70)
rsi_fig.add_hline(y=30)

st.plotly_chart(rsi_fig, use_container_width=True)

# -----------------------------
# MACD CHART
# -----------------------------
st.subheader("📉 MACD Indicator")

macd_fig = go.Figure()

macd_fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["MACD"],
        name="MACD"
    )
)

macd_fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["Signal_Line"],
        name="Signal Line"
    )
)

st.plotly_chart(macd_fig, use_container_width=True)

# -----------------------------
# ML PREDICTION
# -----------------------------
st.subheader("🤖 ML Prediction")

df_ml = df[["Close"]].dropna().reset_index()

df_ml["Days"] = np.arange(len(df_ml))

X = df_ml[["Days"]]
y = df_ml["Close"]

model = LinearRegression()
model.fit(X, y)

next_day = np.array([[len(df_ml)]])
prediction = model.predict(next_day)

st.success(f"Predicted Next Day Price: ₹{prediction[0]:.2f}")

# -----------------------------
# DATA TABLE
# -----------------------------
st.subheader("📄 Stock Data")

st.dataframe(df.tail())
