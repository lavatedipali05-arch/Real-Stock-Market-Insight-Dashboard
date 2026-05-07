import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import MACD
from sklearn.linear_model import LinearRegression

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Real Stock Market Dashboard",
    page_icon="🚀",
    layout="wide"
)

# =========================
# TITLE
# =========================
st.title("🚀 Pro Real-Time Stock Dashboard")
st.markdown("Live Stock Analysis • Candlestick • RSI • MACD • ML Prediction")

# =========================
# SIDEBAR
# =========================
st.sidebar.header("⚙ Settings")

ticker = st.sidebar.text_input(
    "Stock Symbol",
    value="RELIANCE.NS"
)

period = st.sidebar.selectbox(
    "Select Period",
    ["1mo", "3mo", "6mo", "1y"],
    index=2
)

# =========================
# DOWNLOAD DATA
# =========================
try:
    df = yf.download(
        ticker,
        period=period,
        progress=False,
        auto_adjust=False
    )

    if df.empty:
        st.error("No stock data found.")
        st.stop()

except Exception as e:
    st.error(f"Error loading stock data: {e}")
    st.stop()

# =========================
# FIX MULTI-INDEX ISSUE
# =========================
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

# =========================
# CLEAN DATA
# =========================
df = df.dropna()

# =========================
# TECHNICAL INDICATORS
# =========================
df["SMA20"] = df["Close"].rolling(20).mean()
df["SMA50"] = df["Close"].rolling(50).mean()

rsi = RSIIndicator(close=df["Close"])
df["RSI"] = rsi.rsi()

macd = MACD(close=df["Close"])
df["MACD"] = macd.macd()
df["MACD_SIGNAL"] = macd.macd_signal()

# =========================
# PRICE METRICS
# =========================
latest_price = float(df["Close"].iloc[-1])
prev_price = float(df["Close"].iloc[-2])

change = latest_price - prev_price
percent = (change / prev_price) * 100

col1, col2, col3 = st.columns(3)

col1.metric(
    "Current Price",
    f"₹{latest_price:.2f}"
)

col2.metric(
    "Daily Change",
    f"₹{change:.2f}"
)

col3.metric(
    "Percent Change",
    f"{percent:.2f}%"
)

# =========================
# CANDLESTICK CHART
# =========================
st.subheader(f"📈 {ticker} Candlestick Chart")

fig = go.Figure(data=[go.Candlestick(
    x=df.index,
    open=df["Open"],
    high=df["High"],
    low=df["Low"],
    close=df["Close"],
    name="Candlestick"
)])

# SMA20
fig.add_trace(go.Scatter(
    x=df.index,
    y=df["SMA20"],
    mode="lines",
    name="SMA20"
))

# SMA50
fig.add_trace(go.Scatter(
    x=df.index,
    y=df["SMA50"],
    mode="lines",
    name="SMA50"
))

fig.update_layout(
    template="plotly_dark",
    height=650,
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# RSI CHART
# =========================
st.subheader("📉 RSI Indicator")

rsi_fig = go.Figure()

rsi_fig.add_trace(go.Scatter(
    x=df.index,
    y=df["RSI"],
    mode="lines",
    name="RSI"
))

rsi_fig.add_hline(y=70)
rsi_fig.add_hline(y=30)

rsi_fig.update_layout(
    template="plotly_dark",
    height=300
)

st.plotly_chart(rsi_fig, use_container_width=True)

# =========================
# MACD CHART
# =========================
st.subheader("📊 MACD Indicator")

macd_fig = go.Figure()

macd_fig.add_trace(go.Scatter(
    x=df.index,
    y=df["MACD"],
    mode="lines",
    name="MACD"
))

macd_fig.add_trace(go.Scatter(
    x=df.index,
    y=df["MACD_SIGNAL"],
    mode="lines",
    name="Signal"
))

macd_fig.update_layout(
    template="plotly_dark",
    height=300
)

st.plotly_chart(macd_fig, use_container_width=True)

# =========================
# ML PREDICTION
# =========================
st.subheader("🧠 ML Prediction")

df_ml = df.dropna().copy()

X = np.arange(len(df_ml)).reshape(-1, 1)
y = df_ml["Close"].values

model = LinearRegression()
model.fit(X, y)

future = np.array([[len(df_ml)]])
prediction = model.predict(future)

st.success(
    f"Predicted Next Day Price: ₹{prediction[0]:.2f}"
)

# =========================
# BUY / SELL SIGNAL
# =========================
st.subheader("📌 Trading Signal")

if df["RSI"].iloc[-1] < 30:
    st.success("BUY Signal ✅")

elif df["RSI"].iloc[-1] > 70:
    st.error("SELL Signal ❌")

else:
    st.warning("HOLD / WAIT ⚠")

# =========================
# STOCK DATA
# =========================
st.subheader("📄 Latest Stock Data")

st.dataframe(df.tail())

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("Built with Streamlit ❤️")
