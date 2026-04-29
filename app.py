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
    import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Stock Dashboard", layout="wide")

st.title("📊 Real Stock Market Dashboard")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("stock_data.csv")

df = load_data()

# Show data
st.subheader("📁 Raw Data")
st.dataframe(df)

# Numeric columns
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns

# Select column
col = st.selectbox("Select column", numeric_cols)

# ---------------------------
# 📈 Line Chart
st.subheader("📈 Line Chart")
st.line_chart(df[col])

# ---------------------------
# 📊 Bar Chart
st.subheader("📊 Bar Chart")
st.bar_chart(df[col])

# ---------------------------
# 📉 Area Chart
st.subheader("📉 Area Chart")
st.area_chart(df[col])

# ---------------------------
# 📌 Histogram (Matplotlib)
st.subheader("📌 Histogram")

fig, ax = plt.subplots()
ax.hist(df[col], bins=20)
st.pyplot(fig)

# ---------------------------
# 🔥 Scatter Plot (2 columns)
st.subheader("🔵 Scatter Plot")

if len(numeric_cols) >= 2:
    x_col = st.selectbox("X-axis", numeric_cols, key="x")
    y_col = st.selectbox("Y-axis", numeric_cols, key="y")

    fig2, ax2 = plt.subplots()
    ax2.scatter(df[x_col], df[y_col])
    ax2.set_xlabel(x_col)
    ax2.set_ylabel(y_col)

    st.pyplot(fig2)
else:
    st.warning("Need at least 2 numeric columns")
else:
    st.warning("No numeric columns found in dataset")
