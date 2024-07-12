import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import yaml
import argparse
from datetime import datetime, timezone

def load_config(config_file: str) -> dict:
    """
    Loads configuration from a YAML file.
    
    Args:
        config_file (str): The path to the configuration file.
    Returns:
        dict: Configuration dictionary.
    """
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

def visualize_data(master_csv: str, notable_events: dict, currency_pair: str, start_date: str = None, end_date: str = None) -> None:
    """
    Visualizes the data in the master CSV file with important dates marked, filtered by start and end dates if provided.
    
    Args:
        master_csv (str): The path to the master CSV file.
        notable_events (dict): A dictionary of important dates and their descriptions.
        currency_pair (str): The currency pair being visualized.
        start_date (str): The start date for filtering data (optional).
        end_date (str): The end date for filtering data (optional).
    Returns:
        None
    """
    data = pd.read_csv(master_csv, header=None, names=[
        "Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time",
        "Base Asset Volume", "Number of Trades", "Taker Buy Volume",
        "Taker Buy Base Asset Volume", "Ignore"
    ])
    data["Open Time"] = pd.to_datetime(data["Open Time"], unit='ms', utc=True)
    data["Close Time"] = pd.to_datetime(data["Close Time"], unit='ms', utc=True)

    # Filter data based on start and end dates if provided
    if start_date:
        start_date = pd.to_datetime(start_date).tz_localize(timezone.utc)
        data = data[data["Open Time"] >= start_date]
    if end_date:
        end_date = pd.to_datetime(end_date).tz_localize(timezone.utc)
        data = data[data["Open Time"] <= end_date]

    plt.figure(figsize=(15, 10))
    sns.lineplot(x=data["Open Time"], y=data["Open"], label="Open", color="blue")

    for date_str, description in notable_events.items():
        victory_time = pd.to_datetime(date_str).tz_convert('UTC')
        if data["Open Time"].min() <= victory_time <= data["Open Time"].max():
            plt.axvline(x=victory_time, color='purple', linestyle='--', label=description)
            plt.text(victory_time, data["Open"].max() * 0.9, description, rotation=30, verticalalignment='bottom', color='purple')

    plt.title(f"{currency_pair}")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main() -> None:
    """
    Main function to visualize data based on the configuration file and command line arguments.
    Returns:
    None
    """
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Visualize currency data.")
    parser.add_argument("--currency", type=str, required=True, help="The currency you wish to visualize")
    parser.add_argument("--start", type=str, required=False, help="Start date in YYYY-MM-DD")
    parser.add_argument("--end", type=str, required=False, help="End date in YYYY-MM-DD")
    args = parser.parse_args()

    config_file = "config.yaml"
    config = load_config(config_file)

    currency_pair = args.currency

    data_folder = f"./data/{currency_pair}"
    master_csv = f"{data_folder}/master_data.csv"

    # Call visualize_data with the master CSV file, notable events, and date range
    visualize_data(master_csv, config['notable_events'], currency_pair, args.start, args.end)

if __name__ == "__main__":
    main()