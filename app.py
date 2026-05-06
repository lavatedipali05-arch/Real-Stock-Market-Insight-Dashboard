import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
from sklearn.linear_model import LinearRegression
import numpy as np

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(page_title="📈 Pro Stock Dashboard", layout="wide")

st.title("🚀 Pro Real-Time Stock Dashboard")

# ----------------------------
# Sidebar Inputs
# ----------------------------
stock = st.sidebar.text_input("Stock Symbol", "RELIANCE.NS")
refresh_rate = st.sidebar.slider("Auto Refresh (sec)", 5, 60, 10)

# ----------------------------
# Auto Refresh
# ----------------------------
placeholder = st.empty()

while True:
    with placeholder.container():

        # ----------------------------
        # Load Data
        # ----------------------------
        df = yf.download(stock, period="6mo", interval="1d")
        df.dropna(inplace=True)

        # ----------------------------
        # Indicators
        # ----------------------------
        df["SMA20"] = df["Close"].rolling(20).mean()
        df["SMA50"] = df["Close"].rolling(50).mean()

        # RSI
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # MACD
        exp1 = df["Close"].ewm(span=12).mean()
        exp2 = df["Close"].ewm(span=26).mean()
        df["MACD"] = exp1 - exp2
        df["Signal_Line"] = df["MACD"].ewm(span=9).

        # ----------------------------
        # BUY / SELL Signal
        # ----------------------------
        df["Signal"] = 0
        df.loc[df["SMA20"] > df["SMA50"], "Signal"] = 1
        df["Position"] = df["Signal"].diff()

        latest_signal = df["Signal"].iloc[-1]

        st.subheader("📢 Signal")
        if latest_signal == 1:
            st.success("🟢 BUY")
        else:
            st.error("🔴 SELL")

        # ----------------------------
        # Candlestick Chart (Plotly)
        # ----------------------------
        st.subheader("🕯️ Candlestick Chart")

        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close']
        )])

        fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], name="SMA20"))
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], name="SMA50"))

        st.plotly_chart(fig, use_container_width=True)

        # ----------------------------
        # RSI Chart
        # ----------------------------
        st.subheader("📉 RSI")

        rsi_fig = go.Figure()
        rsi_fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI"))
        rsi_fig.add_hline(y=70)
        rsi_fig.add_hline(y=30)

        st.plotly_chart(rsi_fig, use_container_width=True)

        # ----------------------------
        # MACD Chart
        # ----------------------------
        st.subheader("📊 MACD")

        macd_fig = go.Figure()
        macd_fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD"))
        macd_fig.add_trace(go.Scatter(x=df.index, y=df["Signal_Line"], name="Signal"))

        st.plotly_chart(macd_fig, use_container_width=True)

        # ----------------------------
        # ML Prediction (Simple)
        # ----------------------------
        st.subheader("🤖 ML Prediction (Next Day Price)")

        df_ml = df[["Close"]].reset_index()
        df_ml["Days"] = np.arange(len(df_ml))

        X = df_ml[["Days"]]
        y = df_ml["Close"]

        model = LinearRegression()
        model.fit(X, y)

        next_day = np.array([[len(df_ml)]])
        prediction = model.predict(next_day)

        st.write(f"The predicted closing price for the next day is: ${prediction[0][0]:.2f}")

        time.sleep(refresh_rate)
