import streamlit as st
import pandas as pd

st.title("📊 Stock Data Dashboard")

df = pd.read_csv("stock_data.csv")

st.subheader("Data Preview")
st.dataframe(df)

st.subheader("Stock Close Price Chart")
st.line_chart(df["Close"])