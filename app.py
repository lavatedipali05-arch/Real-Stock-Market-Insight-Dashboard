import streamlit as st
import pandas as pd

st.title("📊 Stock Data Dashboard")

df = pd.read_csv("stock_data.csv")

st.subheader("Data Preview")
st.dataframe(df)

st.subheader("Stock Close Price Chart")
st.line_chart(df["Close"])
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

st.pyplot(fig)

# Signal
st.subheader("📊 Signal")

if df['MA50'].iloc[-1] > df['MA200'].iloc[-1]:
    st.success("BUY Signal")
else:
    st.error("SELL Signal")

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

st.title("📈 Stock Prediction using LSTM")

# Input
ticker = st.text_input("Enter Stock Symbol", "AAPL")

# Load data
@st.cache_data
def load_data(ticker):
    return yf.download(ticker, period="5y")

df = load_data(ticker)

st.subheader("📊 Raw Data")
st.dataframe(df.tail())

# Prepare data
data = df[['Close']].values

scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(data)

train_size = int(len(scaled_data) * 0.8)
train_data = scaled_data[:train_size]

# Create sequences
X_train, y_train = [], []

for i in range(60, len(train_data)):
    X_train.append(train_data[i-60:i, 0])
    y_train.append(train_data[i, 0])

X_train, y_train = np.array(X_train), np.array(y_train)
X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)

# Build model
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(X_train.shape[1],1)))
model.add(LSTM(50))
model.add(Dense(1))

model.compile(optimizer='adam', loss='mean_squared_error')

# Train
with st.spinner("Training LSTM model..."):
    model.fit(X_train, y_train, epochs=3, batch_size=32)

# Test data
test_data = scaled_data[train_size-60:]
X_test = []

for i in range(60, len(test_data)):
    X_test.append(test_data[i-60:i, 0])

X_test = np.array(X_test)
X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

# Prediction
predictions = model.predict(X_test)
predictions = scaler.inverse_transform(predictions)

# Plot
st.subheader("📊 Prediction vs Actual")

fig, ax = plt.subplots()
ax.plot(df['Close'], label="Actual Price")
ax.plot(range(train_size, train_size+len(predictions)), predictions, label="Predicted Price")
ax.legend()

st.pyplot(fig)

import plotly.graph_objects as go

st.subheader("📊 Candlestick Chart")

fig = go.Figure(data=[go.Candlestick(
    x=df.index,
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close']
)])

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Price",
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)
