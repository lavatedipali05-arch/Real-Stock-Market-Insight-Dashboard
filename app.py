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
    import yfinance as yf
    try:
        df = yf.download(ticker, period="1y")
        if df is None or df.empty:
            return None
        return df
    except Exception:
        return None

try:
df = load_data(ticker)

if df is None:
    st.error("❌ No data found. Try: TCS.NS, RELIANCE.NS")
    st.stop()

        # Chart
        import matplotlib.pyplot as plt

        st.pyplot(fig)

except Exception as e:
    st.error(f"Error: {e}")
