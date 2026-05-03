@st.cache_data
def load_data(symbol):
    try:
        df = yf.download(symbol, period="1y", progress=False)

        if df.empty:
            # retry once
            df = yf.download(symbol, period="6mo", progress=False)

        return df
    except:
        return pd.DataFrame()

df = load_data(ticker)

if df.empty:
    st.error("❌ Data not loading from Yahoo (Cloud issue)")

    st.info("👉 Try these working symbols:")
    st.code("RELIANCE.NS\nINFY.NS\nHDFCBANK.NS")

else:
    st.success("✅ Data Loaded")

    st.dataframe(df.tail())

    import plotly.graph_objects as go

    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    )])

    st.plotly_chart(fig, use_container_width=True)
