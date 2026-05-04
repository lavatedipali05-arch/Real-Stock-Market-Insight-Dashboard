import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Stock Dashboard", layout="wide")

st.title("📈 Stock Data Dashboard with Buy/Sell Signals")

# --- INPUT ---
ticker = st.text_input("Enter Stock Symbol (e.g. TCS.NS, INFY.NS, RELIANCE.NS)", "TCS.NS")

# --- LOAD DATA ---
@st.cache_data
def load_data(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)
        if df.empty:
            return None
        return df
    except:
        return None

df = load_data(ticker)

# --- ERROR HANDLING ---
if df is None:
    st.error("❌ No data found. Use correct format like TCS.NS, INFY.NS")
    st.stop()

# --- INDICATORS ---
df["MA20"] = df["Close"].rolling(window=20).mean()
df["MA50"] = df["Close"].rolling(window=50).mean()

# --- BUY/SELL SIGNAL ---
df["Signal"] = 0
df.loc[df["MA20"] > df["MA50"], "Signal"] = 1
df.loc[df["MA20"] < df["MA50"], "Signal"] = -1

# --- LATEST SIGNAL ---
latest_signal = df["Signal"].iloc[-1]

if latest_signal == 1:
    st.success("🟢 BUY Signal (MA20 > MA50)")
elif latest_signal == -1:
    st.error("🔴 SELL Signal (MA20 < MA50)")
else:
    st.warning("⚪ HOLD")

# --- CHART ---
st.subheader("Stock Price Chart")

fig, ax = plt.subplots()

ax.plot(df.index, df["Close"], label="Close Price")
ax.plot(df.index, df["MA20"], label="MA20")
ax.plot(df.index, df["MA50"], label="MA50")

ax.legend()
st.pyplot(fig)

# --- DATA ---
st.subheader("Raw Data")
st.dataframe(df.tail())

ticker = st.text_input("Enter Stock", "TCS")

if not ticker.endswith(".NS"):
    ticker = ticker + ".NS"
