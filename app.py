import streamlit as st
import pandas as pd

st.title("📊 Stock Data Dashboard")

try:
    df = pd.read_csv("stock_data.csv")

    st.subheader("Data Preview")
    st.dataframe(df)

    if "Close" in df.columns:
        st.subheader("Stock Close Price Chart")
        st.line_chart(df["Close"])
    else:
        st.error("❌ 'Close' column not found in CSV")

except FileNotFoundError:
    st.error("❌ stock_data.csv file missing in repo")
