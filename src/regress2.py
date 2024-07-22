# Purpose: A simpler version of the regress.py script
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta
import os
import statsmodels.formula.api as smf
from src.utils import load_config, load_data

def prepare_did_data(data, event_date, window_days):
    """Prepare data for DiD analysis."""
    event_date = pd.to_datetime(event_date)
    start_date = event_date - timedelta(days=window_days)
    end_date = event_date + timedelta(days=window_days)
    
    data_window = data[(data['Open Time'] >= start_date) & (data['Open Time'] <= end_date)]
    
    # Create DiD variables
    data_window['Treatment'] = (data_window['Currency'] == 'BTCUSDT').astype(int)
    data_window['Post'] = (data_window['Open Time'] >= event_date).astype(int)
    data_window['Treatment_Post'] = data_window['Treatment'] * data_window['Post']
    print(data_window)
    
    return data_window

def run_did_regression(data):
    """Run DiD regression."""
    model = smf.ols(formula='Close ~ Treatment + Post + Treatment_Post', data=data)
    results = model.fit()
    return results

def visualize_prices(data, event_date, window_days, output_folder):
    """Visualize price data around a specific event date."""
    event_date = pd.to_datetime(event_date)
    start_date = event_date - timedelta(days=window_days)
    end_date = event_date + timedelta(days=window_days)
    
    plt.figure(figsize=(12, 6))
    for currency in data['Currency'].unique():
        currency_data = data[data['Currency'] == currency]
        plt.plot(currency_data['Open Time'], currency_data['Close'], label=currency)
    
    plt.axvline(x=event_date, color='r', linestyle='--', label='Event Date')
    plt.title(f'Asset Prices - {window_days} days before and after {event_date.date()}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    filename = f'asset_prices_{event_date.date()}.png'
    plt.savefig(os.path.join(output_folder, filename))
    plt.close()

def main():
    config = load_config("config.yaml")
    
    # Configuration
    event_dates = config['event_dates']
    window_days = config['time_window']
    output_folder = './output'
    
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Load data
    data = load_data()
    
    for event_date in event_dates:
        # Prepare data for DiD analysis
        did_data = prepare_did_data(data, event_date, window_days)
        
        # Run DiD regression
        results = run_did_regression(did_data)
        print(f"DiD Results for event on {event_date}:")
        print(results.summary())
        
        # Visualize prices
        visualize_prices(did_data, event_date, window_days, output_folder)

if __name__ == "__main__":
    main()