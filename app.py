import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt

# MUST BE FIRST
st.set_page_config(page_title="Stock Dashboard", layout="wide")

st.title("📈 Stock Market Dashboard")

# Input
ticker = st.text_input("Enter Stock Symbol", "TCS.NS")

# Cache function
@st.cache_data
def load_data(ticker):
    return yf.download(ticker, period="1y")

try:
    df = load_data(ticker)

    if df.empty:
        st.error("❌ No data found. Try: TCS.NS, RELIANCE.NS")
    else:
        st.success("✅ Data Loaded")

        st.dataframe(df.tail())

        # Chart
        fig, ax = plt.subplots()
        ax.plot(df["Close"])
        ax.set_title("Closing Price")

        st.pyplot(fig)

except Exception as e:
    st.error(f"Error: {e}")
