import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Stock Dashboard", layout="wide")

# ------------------ TITLE ------------------
st.title("📈 Stock Data Dashboard & Prediction")

# ------------------ INPUT ------------------
ticker = st.text_input("Enter Stock Symbol (e.g. TCS.NS, INFY.NS, RELIANCE.NS)", "INFY.NS")

# ------------------ LOAD DATA ------------------
@st.cache_data
def load_data(ticker):
    try:
        df = yf.download(ticker, period="1y", progress=False)
        if df.empty:
            return None
        return df
    except Exception as e:
        return None

# ------------------ MAIN LOGIC ------------------
df = load_data(ticker)

if df is None:
    st.error("❌ No data found. Try valid symbols like TCS.NS, INFY.NS, RELIANCE.NS")
else:
    st.success("✅ Data Loaded Successfully")

    # ------------------ SHOW DATA ------------------
    st.subheader("📊 Recent Data")
    st.dataframe(df.tail())

    # ------------------ CHART ------------------
    st.subheader("📈 Closing Price Chart")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        name='Close Price'
    ))

    fig.update_layout(
        title="Stock Closing Price",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ------------------ SIMPLE MOVING AVERAGE ------------------
    st.subheader("📉 Moving Average")

    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Close'))
    fig2.add_trace(go.Scatter(x=df.index, y=df['MA50'], name='MA50'))
    fig2.add_trace(go.Scatter(x=df.index, y=df['MA200'], name='MA200'))

    fig2.update_layout(template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

    # ------------------ BASIC PREDICTION (PLACEHOLDER) ------------------
    st.subheader("🔮 Prediction (Demo)")

    last_price = df['Close'].iloc[-1]
    predicted_price = last_price * 1.02  # simple +2% demo prediction

    st.metric(label="Last Closing Price", value=round(last_price, 2))
    st.metric(label="Predicted Next Price", value=round(predicted_price, 2))

    st.info("⚠️ This is a demo prediction. You can replace it with LSTM model.")
