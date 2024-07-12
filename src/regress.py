import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

def load_data(master_csv):
    data = pd.read_csv(master_csv, header=None, 
                       names=["timestamp", "open", "high", "low", "close", "volume"])
    # data['Open Time'] = pd.to_datetime(data['Open Time'], unit='min')
    # data['Date'] = data['Open Time'].dt.date
    return data

def calculate_returns(data):
    data['Return'] = data['Close'].pct_change()
    return data

def load_sp500_data(sp500_csv):
    sp500_data = pd.read_csv(sp500_csv)
    sp500_data['timestamp'] = pd.to_datetime(sp500_data['timestamp'])
    sp500_data['Date'] = sp500_data['timestamp'].dt.date
    sp500_data['SP500_Return'] = sp500_data['close'].pct_change()
    return sp500_data

def estimate_market_model(merged_data, estimation_window):
    estimation_data = merged_data.head(estimation_window)
    X = estimation_data['SP500_Return'].values.reshape(-1, 1)
    y = estimation_data['Return'].values
    model = LinearRegression()
    model.fit(X, y)
    return model

def calculate_abnormal_returns(merged_data, model, event_window):
    event_data = merged_data.tail(event_window)
    X = event_data['SP500_Return'].values.reshape(-1, 1)
    expected_returns = model.predict(X)
    event_data['Abnormal_Return'] = event_data['Return'] - expected_returns
    return event_data

def perform_event_study(token_csv, sp500_csv, estimation_window, event_window):
    token_data = load_data(token_csv)
    token_data = calculate_returns(token_data)
    print(f"Token data shape: {token_data.shape}")
    
    sp500_data = load_sp500_data(sp500_csv)
    print(f"S&P 500 data shape: {sp500_data.shape}")
    
    merged_data = pd.merge(token_data, sp500_data[['Date', 'SP500_Return']], on='Date')
    print(f"Merged data shape: {merged_data.shape}")
    
    if len(merged_data) < estimation_window + event_window:
        print("Not enough data for the specified estimation and event windows")
        return
    
    market_model = estimate_market_model(merged_data, estimation_window)
    event_data = calculate_abnormal_returns(merged_data, market_model, event_window)
    
    cumulative_abnormal_return = event_data['Abnormal_Return'].sum()
    print(f"Cumulative Abnormal Return: {cumulative_abnormal_return:.4f}")
    
    # Plot abnormal returns
    plt.figure(figsize=(12, 6))
    plt.plot(event_data['Date'], event_data['Abnormal_Return'])
    plt.title('Abnormal Returns Around the Event')
    plt.xlabel('Date')
    plt.ylabel('Abnormal Return')
    plt.show()

# Usage
currency = "BTCUSDT"
token_csv = f"./data/{currency}/master_data.csv"
sp500_csv = "./data/SPY/SPY_1min_firstratedata.csv"
estimation_window = 2  # days
event_window = 2  # days

perform_event_study(token_csv, sp500_csv, estimation_window, event_window)