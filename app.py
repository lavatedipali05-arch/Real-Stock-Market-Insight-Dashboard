import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.ensemble import RandomForestRegressor
import ta.momentum
import ta.trend
import ta.volatility # Import for Bollinger Bands
import os # Import os for file path checks

# --- Custom CSS Theme: Midnight Blue & Soft Gray ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0e1117; /* Dark background */
        color: #fafafa; /* Off-white text */
    }
    .stSidebar > div:first-child {
        background-color: #161b22; /* Slightly lighter sidebar */
    }
    h1, h2, h3, h4, h5, h6 {
        color: #58a6ff; /* GitHub-style blue headers */
    }
    .stSelectbox label, .stSidebar label {
        color: #8b949e !important;
    }
    /* Customize buttons and other elements */
    .stButton>button {
        color: #ffffff;
        background-color: #238636;
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# --- End Custom CSS Theme ---

st.title("📈 Pro Stock Dashboard")

# Initialize session state for stock selections if not already present
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = "TCS.NS"
if 'compare_stock_ticker' not in st.session_state:
    st.session_state.compare_stock_ticker = "HDFCBANK.NS"

# Stock selection in sidebar (Primary Stock)
st.sidebar.subheader("Primary Stock Selection")
stock_options = ["TCS.NS", "INFY.NS", "RELIANCE.NS", "GOOG", "AMZN"]
selected_primary_stock = st.sidebar.selectbox(
    "Select Primary Stock",
    stock_options,
    key='primary_stock_selector',
    on_change=lambda: st.session_state.__setitem__('selected_stock', st.session_state.primary_stock_selector)
)

# Data validation for primary stock
st.session_state.selected_stock = selected_primary_stock

# Load data for primary stock
data = yf.download(st.session_state.selected_stock, period="max", interval="1d")

if data.empty:
    st.warning("No data available for the primary stock.")
else:
    data.columns = data.columns.get_level_values(0)

    # Calculate Moving Averages
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()

    # Calculate indicators
    data['RSI'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
    macd_indicator = ta.trend.MACD(data['Close'])
    data['MACD'] = macd_indicator.macd()
    data['MACD_Signal'] = macd_indicator.macd_signal()

    # Calculate Bollinger Bands
    bollinger_bands = ta.volatility.BollingerBands(data['Close'], window=20, window_dev=2)
    data['BB_upper'] = bollinger_bands.bollinger_hband()
    data['BB_lower'] = bollinger_bands.bollinger_lband()
    data['BB_middle'] = bollinger_bands.bollinger_mavg()

    data.dropna(inplace=True)

    st.subheader(f"Raw Data for {st.session_state.selected_stock}")
    st.write(data.tail())

    # Plot the Close price with improved colors
    st.subheader("Closing Price Trend")
    plt.style.use('dark_background')
    fig_trend, ax_trend = plt.subplots(figsize=(10, 6))
    ax_trend.plot(data.index, data['Close'], color='#58a6ff')
    ax_trend.set_ylabel("Close Price")
    ax_trend.grid(True, alpha=0.2)
    st.pyplot(fig_trend)

    # LSTM Prediction
    st.subheader("🔮 LSTM Price Prediction (Next 7 Days)")
    features_for_lstm = ['Open', 'High', 'Low', 'Close', 'Volume', 'MA20', 'MA50', 'RSI', 'MACD', 'MACD_Signal', 'BB_upper', 'BB_lower', 'BB_middle']

    if all(f in data.columns for f in features_for_lstm):
        try:
            lstm_model = load_model('lstm_model.keras')
            lstm_data_raw = data[features_for_lstm].values
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_lstm_data = scaler.fit_transform(lstm_data_raw)

            sequence_length = 60
            current_input = scaled_lstm_data[-sequence_length:].reshape(1, sequence_length, len(features_for_lstm))

            predictions = []
            for _ in range(7):
                next_pred = lstm_model.predict(current_input, verbose=0)
                predictions.append(next_pred[0, 0])
                next_step = current_input[0, -1, :].copy()
                next_step[features_for_lstm.index('Close')] = next_pred[0, 0] # Use index for 'Close'
                current_input = np.append(current_input[:, 1:, :], next_step.reshape(1, 1, len(features_for_lstm)), axis=1)

            res_array = np.array(predictions).reshape(-1, 1)
            dummy = np.zeros((len(res_array), len(features_for_lstm)))
            dummy[:, features_for_lstm.index('Close')] = res_array.flatten()
            final_preds = scaler.inverse_transform(dummy)[:, features_for_lstm.index('Close')]

            future_dates = pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=7)
            pred_df = pd.DataFrame({'Date': future_dates, 'Predicted Price': final_preds})
            st.line_chart(pred_df.set_index('Date'))
        except FileNotFoundError:
            st.error("Error: 'lstm_model.keras' not found. Please ensure the LSTM model has been trained and saved in the correct directory.")
        except Exception as e:
            st.error(f"Error loading tuned LSTM model: {e}")
