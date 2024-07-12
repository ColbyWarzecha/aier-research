import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from typing import Tuple

# TODO: Try out the eventstudy module: https://lemairejean-baptiste.github.io/eventstudy/get_started.html
# or here: https://github.com/zrxbeijing/EventStudy/blob/master/EventStudy/return_calculator.py

# Where I'm stuck: The below script is running (and crashing) in memory. How to fix...
# I think I need to 1) write estimates to a csv file so that this isn't all run in memory and 
# therefore 2) refactor the below code.

# I'll also need to load the USD/CHF data instead of SPY, since BTC is more like a currency than a SPY.

def load_data(token_file: str, sp500_file: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load token and S&P 500 data."""
    token_data = pd.read_csv(token_file, parse_dates=['Date'], index_col='Date')
    sp500_data = pd.read_csv(sp500_file, parse_dates=['Date'], index_col='Date')
    return token_data, sp500_data

def calculate_returns(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate daily returns."""
    return data.pct_change().dropna()

def estimate_market_model(token_returns: pd.Series, sp500_returns: pd.Series) -> Tuple[float, float]:
    """Estimate market model parameters using OLS regression."""
    model = LinearRegression()
    model.fit(sp500_returns.values.reshape(-1, 1), token_returns.values)
    return model.intercept_, model.coef_[0]

def calculate_abnormal_returns(token_returns: pd.Series, sp500_returns: pd.Series, 
                               alpha: float, beta: float) -> pd.Series:
    """Calculate abnormal returns."""
    expected_returns = alpha + beta * sp500_returns
    return token_returns - expected_returns

def event_study(token_file: str, sp500_file: str, event_date: str, 
                estimation_window: int, event_window: int) -> None:
    """Perform event study analysis."""
    # Load and prepare data
    token_data, sp500_data = load_data(token_file, sp500_file)
    token_returns = calculate_returns(token_data['Close'])
    sp500_returns = calculate_returns(sp500_data['Close'])

    # Align data and select estimation and event windows
    aligned_data = pd.concat([token_returns, sp500_returns], axis=1).dropna()
    aligned_data.columns = ['Token', 'SP500']
    
    event_date = pd.to_datetime(event_date)
    estimation_end = event_date - pd.Timedelta(days=1)
    estimation_start = estimation_end - pd.Timedelta(days=estimation_window)
    event_end = event_date + pd.Timedelta(days=event_window)

    estimation_data = aligned_data.loc[estimation_start:estimation_end]
    event_data = aligned_data.loc[event_date:event_end]

    # Estimate market model
    alpha, beta = estimate_market_model(estimation_data['Token'], estimation_data['SP500'])
    print(f"Market Model Parameters: Alpha = {alpha:.4f}, Beta = {beta:.4f}")

    # Calculate abnormal returns
    abnormal_returns = calculate_abnormal_returns(event_data['Token'], event_data['SP500'], alpha, beta)
    cumulative_abnormal_returns = abnormal_returns.cumsum()

    # Plot results
    plt.figure(figsize=(12, 6))
    plt.plot(cumulative_abnormal_returns.index, cumulative_abnormal_returns.values)
    plt.title('Cumulative Abnormal Returns')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Abnormal Returns')
    plt.axvline(x=event_date, color='r', linestyle='--', label='Event Date')
    plt.legend()
    plt.show()

    # Print summary statistics
    print("\nSummary Statistics:")
    print(abnormal_returns.describe())
    print(f"\nCumulative Abnormal Return: {cumulative_abnormal_returns.iloc[-1]:.4f}")

if __name__ == "__main__":
    token_file = "path/to/token_data.csv"  # Replace with actual path
    sp500_file = "path/to/sp500_data.csv"  # Replace with actual path
    event_date = "2023-11-19"  # Replace with actual event date
    estimation_window = 120  # Number of days for estimation window
    event_window = 10  # Number of days for event window

    event_study(token_file, sp500_file, event_date, estimation_window, event_window)