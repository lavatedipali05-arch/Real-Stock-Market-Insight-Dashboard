import streamlit as st
import pandas as pd

# Page title
st.set_page_config(page_title="Stock Dashboard", layout="wide")

# Title
st.title("📊 Real Stock Market Insight Dashboard")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("stock_data.csv")

df = load_data()

# Show raw data
st.subheader("📁 Raw Data")
st.dataframe(df)

# Select column for chart
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns

if len(numeric_cols) > 0:
    selected_col = st.selectbox("Select column for chart", numeric_cols)

    # Line chart
    st.subheader(f"📈 {selected_col} Trend")
    st.line_chart(df[selected_col])
else:
    st.warning("No numeric columns found in dataset")
