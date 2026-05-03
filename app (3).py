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

st.title("📈 Stock Data Dashboard & LSTM Prediction")

# Initialize session state for stock selections if not already present
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = "TCS.NS"
if 'compare_stock_ticker' not in st.session_state:
    st.session_state.compare_stock_ticker = "HDFCBANK.NS"

# Stock selection
stock = st.selectbox(
    "Select Primary Stock",
    ["TCS.NS", "INFY.NS", "RELIANCE.NS"],
    key='primary_stock_selector',
    on_change=lambda: st.session_state.__setitem__('selected_stock', st.session_state.primary_stock_selector)
)

st.session_state.selected_stock = stock

# Load data for primary stock
data = yf.download(st.session_state.selected_stock, period="max", interval="1d")

# --- Start new data checks ---
if data.empty:
    st.warning("No data available for the primary stock. Please select another stock or check API key/internet connection. Dashboard features will be limited.")
    print("WARNING: No data available for the primary stock. Dashboard features will be limited.")
else:
    # Flatten columns from MultiIndex to single level
    data.columns = data.columns.get_level_values(0)

    # Calculate Moving Averages (consistent with improved model training)
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()

    # Calculate new Technical Indicators: RSI and MACD
    data['RSI'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
    macd_indicator = ta.trend.MACD(data['Close'])
    data['MACD'] = macd_indicator.macd()
    data['MACD_Signal'] = macd_indicator.macd_signal()

    # Calculate Bollinger Bands
    bollinger_bands = ta.volatility.BollingerBands(data['Close'], window=20, window_dev=2)
    data['BB_upper'] = bollinger_bands.bollinger_hband()
    data['BB_lower'] = bollinger_bands.bollinger_lband()
    data['BB_middle'] = bollinger_bands.bollinger_mavg()

    # Drop rows with NaN values resulting from indicator calculations
    data.dropna(inplace=True)

    # Display the entire DataFrame
    st.subheader(f"Raw Data for {st.session_state.selected_stock}")
    st.write(data)

    # Plot the Close price
    st.subheader(f"Closing Price Trend for {st.session_state.selected_stock}")

    fig_trend, ax_trend = plt.subplots(figsize=(10, 6))
    ax_trend.plot(data.index, data['Close'])
    ax_trend.set_title(f"Closing Price Trend for {st.session_state.selected_stock}")
    ax_trend.set_xlabel("Date")
    ax_trend.set_ylabel("Close Price")
    ax_trend.grid(True)
    st.pyplot(fig_trend)

    # Add download button for the trend chart
    try:
        fig_trend.savefig('closing_price_trend.png')
        with open('closing_price_trend.png', 'rb') as f:
            st.download_button(
                label="Download Closing Price Trend (PNG)",
                data=f.read(),
                file_name=f"{st.session_state.selected_stock}_closing_price_trend.png",
                mime="image/png"
            )
    except Exception as e:
        st.warning(f"Could not save or download trend chart: {e}")

    # Calculate daily returns
    data['Daily Return'] = data['Close'].pct_change()

    # Plot the Daily Returns as a histogram
    st.subheader("Daily Returns Distribution")
    fig_hist, ax_hist = plt.subplots(figsize=(10, 6))
    ax_hist.hist(data['Daily Return'].dropna(), bins=50, edgecolor='black')
    ax_hist.set_title('Distribution of Daily Returns')
    ax_hist.set_xlabel('Daily Return')
    ax_hist.set_ylabel('Frequency')
    st.pyplot(fig_hist)

    # Add download button for the histogram
    try:
        fig_hist.savefig('daily_returns_histogram.png')
        with open('daily_returns_histogram.png', 'rb') as f:
            st.download_button(
                label="Download Daily Returns Histogram (PNG)",
                data=f.read(),
                file_name="daily_returns_histogram.png",
                mime="image/png"
            )
    except Exception as e:
        st.warning(f"Could not save or download histogram: {e}")

    # --- Comparison Feature ---
    st.subheader("📊 Compare with Another Stock")
    compare_stock_ticker = st.selectbox(
        "Select Stock for Comparison",
        ["HDFCBANK.NS", "ICICIBANK.NS", "LT.NS"],
        key='comparison_stock_selector',
        on_change=lambda: st.session_state.__setitem__('compare_stock_ticker', st.session_state.comparison_stock_selector)
    )

    st.session_state.compare_stock_ticker = compare_stock_ticker

    if st.session_state.compare_stock_ticker:
        try:
            # Load comparison data from yfinance
            compare_data = yf.download(st.session_state.compare_stock_ticker, period="max", interval="1d")
            # Flatten columns from MultiIndex to single level for compare_data
            compare_data.columns = compare_data.columns.get_level_values(0)

            if compare_data.empty or 'Close' not in compare_data.columns:
                st.info(f"No valid 'Close' price data available for comparison stock: {st.session_state.compare_stock_ticker}. Please check the stock ticker or API connection.")
            else:
                # Ensure both are Series and have a proper name for the DataFrame creation
                primary_stock_series = data['Close'].rename(st.session_state.selected_stock)
                compare_stock_series = compare_data['Close'].rename(st.session_state.compare_stock_ticker)

                combined_df = pd.concat([primary_stock_series, compare_stock_series], axis=1).dropna()

                if not combined_df.empty: # Check if combined_df is not empty after dropping NaNs
                    st.subheader(f"Closing Price Comparison: {st.session_state.selected_stock} vs {st.session_state.compare_stock_ticker}")
                    st.write("**First 5 rows of combined comparison data:**")
                    st.write(combined_df.head())

                    fig_comp, ax_comp = plt.subplots(figsize=(10, 6))
                    ax_comp.plot(combined_df.index, combined_df[st.session_state.selected_stock], label=st.session_state.selected_stock)
                    ax_comp.plot(combined_df.index, combined_df[st.session_state.compare_stock_ticker], label=st.session_state.compare_stock_ticker)
                    ax_comp.set_title(f"Closing Price Comparison: {st.session_state.selected_stock} vs {st.session_state.compare_stock_ticker}")
                    ax_comp.set_xlabel("Date")
                    ax_comp.set_ylabel("Close Price")
                    ax_comp.legend()
                    ax_comp.grid(True)
                    st.pyplot(fig_comp)

                    # Add download button for the comparison chart
                    try:
                        fig_comp.savefig('closing_price_comparison.png')
                        with open('closing_price_comparison.png', 'rb') as f:
                            st.download_button(
                                label="Download Price Comparison Chart (PNG)",
                                data=f.read(),
                                file_name=f"{st.session_state.selected_stock}_{st.session_state.compare_stock_ticker}_comparison.png",
                                mime="image/png"
                            )
                    except Exception as e:
                        st.warning(f"Could not save or download comparison chart: {e}")

                    # Add Summary Statistics for comparison stocks
                    st.subheader("📊 Summary Statistics (Comparison Stocks)")
                    st.write(combined_df.describe())

                else:
                    st.info(f"No common dates found for comparison between {st.session_state.selected_stock} and {st.session_state.compare_stock_ticker}. Please check the selected period or stocks.")
        except Exception as e:
            st.error(f"An error occurred while loading comparison data for {st.session_state.compare_stock_ticker}: {e}")

    # --- Feature Importance ---
    st.subheader("📈 Feature Importance (Random Forest)")

    # Prepare data for feature importance model
    feature_df = data.copy()
    feature_df['Close_Lag1'] = feature_df['Close'].shift(1)
    feature_df['Open_Lag1'] = feature_df['Open'].shift(1)
    feature_df['High_Lag1'] = feature_df['High'].shift(1)
    feature_df['Low_Lag1'] = feature_df['Low'].shift(1)
    feature_df = feature_df.dropna()

    if not feature_df.empty:
        # Updated features for Random Forest to include new indicators
        rf_features = ['Open', 'High', 'Low', 'Volume', 'Daily Return', 'Close_Lag1', 'Open_Lag1', 'High_Lag1', 'Low_Lag1', 'RSI', 'MACD', 'MACD_Signal', 'BB_upper', 'BB_lower', 'BB_middle']
        # Filter for only existing features in case some are NaN due to initial data size
        rf_features_existing = [f for f in rf_features if f in feature_df.columns]

        target = 'Close'

        X_rf = feature_df[rf_features_existing]
        y_rf = feature_df[target]

        try:
            rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
            rf_model.fit(X_rf, y_rf)

            feature_importances = pd.Series(rf_model.feature_importances_, index=rf_features_existing).sort_values(ascending=False)

            fig_fi, ax_fi = plt.subplots(figsize=(10, 6))
            feature_importances.plot(kind='bar', ax=ax_fi)
            ax_fi.set_title('Feature Importance for Stock Price Prediction (Random Forest)')
            ax_fi.set_ylabel('Importance')
            ax_fi.tick_params(axis='x', rotation=45)
            st.pyplot(fig_fi)

            try:
                fig_fi.savefig('feature_importance.png')
                with open('feature_importance.png', 'rb') as f:
                    st.download_button(
                        label="Download Feature Importance Chart (PNG)",
                        data=f.read(),
                        file_name="feature_importance.png",
                        mime="image/png"
                    )
            except Exception as e:
                st.warning(f"Could not save or download feature importance chart: {e}")

        except Exception as e:
            st.error(f"An error occurred during RandomForestRegressor training: {e}")
    else:
        st.info("Not enough data to calculate feature importance.")

    # --- LSTM Prediction ---
    st.subheader("🔮 LSTM Price Prediction (Next 7 Days)")

    # Define features for LSTM (must match training features for `model_improved`)
    features_for_lstm = ['Open', 'High', 'Low', 'Close', 'Volume', 'MA20', 'MA50', 'RSI', 'MACD', 'MACD_Signal', 'BB_upper', 'BB_lower', 'BB_middle']

    # Ensure all features exist before scaling
    if not all(f in data.columns for f in features_for_lstm):
        st.error("Missing one or more required features for LSTM. Check data availability and calculation.")
    else:
        lstm_data_raw = data[features_for_lstm].values

        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_lstm_data = scaler.fit_transform(lstm_data_raw)

        sequence_length = 60 # This should match the training sequence length

        if len(scaled_lstm_data) >= sequence_length:
            try:
                lstm_model = load_model('lstm_model.keras') # Corrected model name to load improved model
                print("INFO: LSTM model loaded successfully.")

                # Prepare X and y for evaluation (current data for metrics)
                X_eval_list, y_eval_list = [], []
                close_idx = features_for_lstm.index('Close') # Index of 'Close' in the features list

                for i in range(sequence_length, len(scaled_lstm_data)):
                    X_eval_list.append(scaled_lstm_data[i-sequence_length:i, :]) # All features
                    y_eval_list.append(scaled_lstm_data[i, close_idx]) # Only 'Close' for target

                if X_eval_list and y_eval_list:
                    X_eval, y_eval = np.array(X_eval_list), np.array(y_eval_list)
                    # Reshape for LSTM: (num_samples, sequence_length, num_features)
                    X_eval = np.reshape(X_eval, (X_eval.shape[0], X_eval.shape[1], len(features_for_lstm)))

                    # Make predictions on the training data for metric calculation
                    train_predictions_scaled = lstm_model.predict(X_eval, verbose=0)
                    print("INFO: LSTM predictions on training data made successfully.")

                    # Inverse transform actual and predicted values for RMSE and MAE
                    # Create dummy arrays with correct number of features for inverse_transform
                    dummy_actuals_eval = np.zeros((len(y_eval), len(features_for_lstm)))
                    dummy_actuals_eval[:, close_idx] = y_eval
                    actual_prices = scaler.inverse_transform(dummy_actuals_eval)[:, close_idx]

                    dummy_predictions_eval = np.zeros((len(train_predictions_scaled), len(features_for_lstm)))
                    dummy_predictions_eval[:, close_idx] = train_predictions_scaled.flatten()
                    predicted_prices = scaler.inverse_transform(dummy_predictions_eval)[:, close_idx]

                    # Calculate RMSE and MAE dynamically
                    rmse = np.sqrt(mean_squared_error(actual_prices, predicted_prices))
                    mae = mean_absolute_error(actual_prices, predicted_prices)
                    print("INFO: RMSE and MAE calculated.")

                    future_days = 7
                    predictions = []

                    # Use the last `sequence_length` days of *all features* for initial prediction
                    current_input = scaled_lstm_data[-sequence_length:].reshape(1, sequence_length, len(features_for_lstm))

                    for _ in range(future_days):
                        next_day_pred_scaled = lstm_model.predict(current_input, verbose=0)
                        predictions.append(next_day_pred_scaled[0, 0])

                        # Simulate next day's features: update 'Close' with prediction, replicate other features from last step
                        next_day_features_scaled = current_input[0, -1, :].copy() # Copy last day's features
                        next_day_features_scaled[close_idx] = next_day_pred_scaled[0, 0] # Update 'Close' with prediction

                        # Update input sequence
                        current_input = np.append(current_input[:, 1:, :], next_day_features_scaled.reshape(1, 1, len(features_for_lstm)), axis=1)

                    print("INFO: Future LSTM predictions generated.")

                    # Inverse transform the predictions to get actual prices
                    predictions_scaled_array = np.array(predictions).reshape(-1, 1)
                    dummy_predictions_for_inv_transform = np.zeros((len(predictions_scaled_array), len(features_for_lstm)))
                    dummy_predictions_for_inv_transform[:, close_idx] = predictions_scaled_array.flatten()
                    predictions_actual_scale = scaler.inverse_transform(dummy_predictions_for_inv_transform)[:, close_idx]

                    # Create future dates
                    last_date = data.index[-1]
                    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=future_days)

                    pred_df = pd.DataFrame(
                        {
                            'Date': future_dates,
                            'Predicted Price': predictions_actual_scale.flatten()
                        }
                    )

                    # Plot actual vs predicted prices
                    fig_lstm, ax_lstm = plt.subplots(figsize=(10, 6))
                    ax_lstm.plot(data.index, data['Close'], label='Actual Closing Price')
                    ax_lstm.plot(pred_df['Date'], pred_df['Predicted Price'], label='LSTM Predicted Price', linestyle='--', marker='o', color='red')
                    ax_lstm.set_title(f'LSTM Price Prediction for {st.session_state.selected_stock}')
                    ax_lstm.set_xlabel('Date')
                    ax_lstm.set_ylabel('Price')
                    ax_lstm.legend()
                    ax_lstm.grid(True)
                    st.pyplot(fig_lstm)
                    print("INFO: LSTM prediction chart displayed.")

                    # Add a plot for Actual vs Predicted Prices (Evaluation Data)
                    st.subheader("📈 LSTM Model: Actual vs. Predicted Prices (Evaluation)")
                    fig_eval, ax_eval = plt.subplots(figsize=(10, 6))

                    # Get dates corresponding to the evaluation period
                    eval_dates = data.index[sequence_length:len(scaled_lstm_data)]

                    ax_eval.plot(eval_dates, actual_prices, label='Actual Prices', color='blue')
                    ax_eval.plot(eval_dates, predicted_prices, label='Predicted Prices', color='orange', linestyle='--')
                    ax_eval.set_title(f'Actual vs. Predicted Prices for {st.session_state.selected_stock}')
                    ax_eval.set_xlabel('Date')
                    ax_eval.set_ylabel('Close Price')
                    ax_eval.legend()
                    ax_eval.grid(True)
                    st.pyplot(fig_eval)

                    # Display predicted values in a table
                    st.write("**Predicted Prices:**")
                    st.write(pred_df.set_index('Date'))

                    # Display RMSE and MAE
                    st.subheader("📊 Model Evaluation Metrics (on training data)")
                    st.write(f"**Root Mean Squared Error (RMSE):** {rmse:.4f}")
                    st.write(f"**Mean Absolute Error (MAE):** {mae:.4f}")

                else:
                    st.info("Not enough data for LSTM evaluation metrics calculation or to perform prediction.")
                    print("WARNING: Not enough data for LSTM evaluation metrics calculation or to perform prediction.")

            except Exception as e:
                st.error(f"Error loading or predicting with LSTM model. Please ensure 'lstm_model.keras' is available and TensorFlow is installed. Error: {e}") # Corrected model name in error message
                print(f"ERROR: Error loading or predicting with LSTM model: {e}")
        else:
            st.info("Not enough historical data (at least 60 days) to perform LSTM prediction for the selected stock.")
            print("INFO: Not enough historical data (at least 60 days) for LSTM prediction.")
