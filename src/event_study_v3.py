import statsmodels.formula.api as smf
import pandas as pd
import numpy as np
from scipy import stats

# Step 1: Load and prepare the data
def load_data():
    df = pd.read_csv('./data/consolidated_data.csv')
    df['Open Time'] = pd.to_datetime(df['Open Time'])
    return df

# Step 2: Calculate returns
def calculate_returns(df):
    for token in ['BTCARS', 'BTCUSDT']:
        df[f'{token}_return'] = df[f'Close_{token}'].pct_change()
    df['USDCHF_return'] = df['Close_USDCHF'].pct_change()
    return df

# Step 3: Estimate market model parameters
def estimate_market_model(df, token, estimation_window):
    estimation_data = df.tail(estimation_window)
    X = estimation_data['USDCHF_return'].values.reshape(-1, 1)
    y = estimation_data[f'{token}_return'].values
    X = np.concatenate([np.ones_like(X), X], axis=1)
    params = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(y)
    alpha, beta = params
    return alpha, beta

# Step 4: Calculate expected returns
def calculate_expected_returns(df, token, alpha, beta):
    df[f'{token}_expected_return'] = alpha + beta * df['USDCHF_return']
    return df

# Step 5: Calculate abnormal returns
def calculate_abnormal_returns(df, token):
    df[f'{token}_abnormal_return'] = df[f'{token}_return'] - df[f'{token}_expected_return']
    return df

# Step 6: Conduct event study
def conduct_event_study(df, token, event_date, event_window):
    event_data = df[(df['Open Time'] >= event_date - pd.Timedelta(days=event_window[0])) &
                    (df['Open Time'] <= event_date + pd.Timedelta(days=event_window[1]))]
    cumulative_ar = event_data[f'{token}_abnormal_return'].sum()
    t_stat, p_value = stats.ttest_1samp(event_data[f'{token}_abnormal_return'], 0)
    return cumulative_ar, t_stat, p_value

# Main function to run the analysis
def main():
    # Load data
    df = load_data()
    
    # Calculate returns
    df = calculate_returns(df)
    
    # Define tokens and event details
    tokens = ['BTCARS', 'BTCUSDT']
    event_date = pd.to_datetime('2023-11-19')  # Date of Milei's election
    event_window = (-1, 1)
    estimation_window = 1  # Adjust as needed
    
    for token in tokens:
        print(f"\nAnalysis for {token}:")
        
        # Estimate market model parameters
        alpha, beta = estimate_market_model(df, token, estimation_window)
        
        # Calculate expected returns
        df = calculate_expected_returns(df, token, alpha, beta)
        
        # Calculate abnormal returns
        df = calculate_abnormal_returns(df, token)
        
        # Conduct event study
        car, t_stat, p_value = conduct_event_study(df, token, event_date, event_window)
        
        print(f"Cumulative Abnormal Return: {car}")
        print(f"T-statistic: {t_stat}")
        print(f"P-value: {p_value}")

if __name__ == "__main__":
    main()