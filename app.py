import streamlit as st

st.set_page_config(page_title="Stock Dashboard", layout="wide")

import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.title("📈 Stock Market Dashboard")

ticker = st.text_input("Enter Stock Symbol", "TCS.NS")

@st.cache_data
def load_data(symbol):
    import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Stock Dashboard", layout="wide")

st.title("📈 Real-Time Stock Market Dashboard")

# Sidebar
ticker = st.sidebar.text_input("Enter Stock Symbol", "AAPL")

# Load data
@st.cache_data
def load_data(ticker):
    df = yf.download(ticker, period="1y")
    return df

df = load_data(ticker)

# Indicators
df['MA50'] = df['Close'].rolling(50).mean()
df['MA200'] = df['Close'].rolling(200).mean()

# Display data
st.subheader("📊 Data Preview")
st.dataframe(df.tail())

# Chart
st.subheader("📈 Price Chart")

fig, ax = plt.subplots()
ax.plot(df['Close'], label='Close')
ax.plot(df['MA50'], label='MA50')
ax.plot(df['MA200'], label='MA200')
ax.legend()

st.pyplot(fi
st.subheader("📊 Signal")

if df['MA50'].iloc[-1] > df['MA200'].iloc[-1]:
    st.success("BUY Signal")
else:
    st.error("SELL Signal")
try:
    df = yf.download(ticker, period="1y")

    if df.empty:
        st.error("❌ No data found. Try different stock (e.g. TCS.NS, RELIANCE.NS)")
    else:
        st.success("✅ Data loaded")
        st.dataframe(df.tail())

except Exception as e:
    st.error(f"Error: {e}")

df = load_data(ticker)

if df.empty:
    st.error("❌ Data not loading")
    st.info("Try: TCS.NS | RELIANCE.NS | INFY.NS")
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
