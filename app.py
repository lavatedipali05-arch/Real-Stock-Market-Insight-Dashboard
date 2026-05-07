import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time
from sklearn.linear_model import LinearRegression

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(page_title="📈 Pro Stock Dashboard", layout="wide")

st.title("🚀 Pro Real-Time Stock Dashboard")

# ----------------------------
# Sidebar
# ----------------------------
stock = st.sidebar.text_input("Stock Symbol", "RELIANCE.NS")

refresh_rate = st.sidebar.slider("Auto Refresh (sec)", 5, 60, 10)

# Multi stock compare
compare_stocks = st.sidebar.text_input("Compare Stocks (comma)", "TCS.NS,INFY.NS")

# ----------------------------
# Auto Refresh Trick (No while True)
# ----------------------------
st_autorefresh = st.empty()
time.sleep(refresh_rate)

# ----------------------------
# Load Data
# ----------------------------
df = yf.download(stock, period="3mo", interval="1d")

df.dropna(inplace=True)

# =========================
# Candlestick Chart
# =========================

st.subheader(f"📈 {stock} Candlestick Chart")

# Download Data
df = yf.download(stock, period="6mo", interval="1d", auto_adjust=False)

# Fix MultiIndex issue
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df.reset_index(inplace=True)

# Remove empty rows
df.dropna(inplace=True)

# Check data exists
if df.empty:
    st.error("No stock data found.")
    st.stop()

# Create Figure
fig = go.Figure(data=[go.Candlestick(
    x=df['Date'],
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close'],
    increasing_line_color='green',
    decreasing_line_color='red',
    name='Candlestick'
)])

# SMA Lines
df['SMA20'] = df['Close'].rolling(20).mean()
df['SMA50'] = df['Close'].rolling(50).mean()

fig.add_trace(go.Scatter(
    x=df['Date'],
    y=df['SMA20'],
    mode='lines',
    name='SMA 20'
))

fig.add_trace(go.Scatter(
    x=df['Date'],
    y=df['SMA50'],
    mode='lines',
    name='SMA 50'
))

# Layout
fig.update_layout(
    template="plotly_dark",
    height=600,
    xaxis_rangeslider_visible=False,
    title=f"{stock} Candlestick Chart",
)

# Show Chart
st.plotly_chart(fig, width="stretch")

# ----------------------------
# RSI
# ----------------------------
delta = df['Close'].diff()

gain = (delta.where(delta > 0, 0)).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()

rs = gain / loss
rsi = 100 - (100 / (1 + rs))

st.subheader("📊 RSI Indicator")
st.line_chart(rsi)

# ----------------------------
# MACD
# ----------------------------
exp1 = df['Close'].ewm(span=12, adjust=False).mean()
exp2 = df['Close'].ewm(span=26, adjust=False).mean()

macd = exp1 - exp2
signal = macd.ewm(span=9, adjust=False).mean()

st.subheader("📉 MACD Indicator")
st.line_chart(macd - signal)

# ----------------------------
# Buy/Sell Signal
# ----------------------------
latest_rsi = rsi.iloc[-1]

st.subheader("📢 Signal")

if latest_rsi < 30:
    st.success("🟢 BUY Signal")
elif latest_rsi > 70:
    st.error("🔴 SELL Signal")
else:
    st.info("⚪ HOLD")

# ----------------------------
# ML Prediction
# ----------------------------
st.subheader("🤖 ML Prediction (Next Day)")

df['Days'] = np.arange(len(df))
X = df[['Days']]
y = df['Close']

model = LinearRegression()
model.fit(X, y)

next_day = np.array([[len(df)]])
prediction = model.predict(next_day)

# ✅ FIXED HERE
st.write(f"Next Predicted Price: ₹{float(prediction[0]):.2f}")

# ----------------------------
# Multi Stock Compare
# ----------------------------
st.subheader("📊 Multi Stock Compare")

stocks_list = [s.strip() for s in compare_stocks.split(",")]

compare_df = pd.DataFrame()

for s in stocks_list:
    data = yf.download(s, period="3mo")['Close']
    compare_df[s] = data

st.line_chart(compare_df)

# ----------------------------
# Correlation Heatmap
# ----------------------------
st.subheader("🔥 Correlation")

corr = compare_df.corr()

st.dataframe(corr)

# ----------------------------
# Footer
# ----------------------------
st.caption("Made with ❤️ | Pro Trader Version 😎")
