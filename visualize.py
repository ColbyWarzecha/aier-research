import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import yaml

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

def visualize_data(master_csv: str, target_dates: dict) -> None:
    """
    Visualizes the data in the master CSV file with important dates marked.

    Args:
        master_csv (str): The path to the master CSV file.
        target_dates (dict): A dictionary of important dates and their descriptions.

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
    
    plt.figure(figsize=(15, 10))
    sns.lineplot(x=data["Open Time"], y=data["Open"], label="Open", color="blue")
    
    for date_str, description in target_dates.items():
        victory_time = pd.to_datetime(date_str).tz_convert('UTC')
        if data["Open Time"].min() <= victory_time <= data["Open Time"].max():
            plt.axvline(x=victory_time, color='purple', linestyle='--', label=description)
            plt.text(victory_time, data["Open"].max() * 0.92, description, rotation=45, verticalalignment='bottom', color='purple')
    
    plt.title(f"{master_csv.split('/')[-3]} - One Day Activity")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main() -> None:
    """
    Main function to visualize data based on the configuration file.

    Returns:
        None
    """
    config_file = "config.yaml"
    config = load_config(config_file)

    currency_pair = "BTCUSDT"  # Example currency pair
    target_date_str = "2023-12-21"  # Example target date
    data_folder = f"./data/{currency_pair}/{target_date_str}"
    master_csv = f"{data_folder}/master_data.csv"

    # Call visualize_data with the master CSV file and important dates
    visualize_data(master_csv, config['target_dates'])

if __name__ == "__main__":
    main()

    # TODO: Visualize these across the entire period. To do so you'll need to:
    # 1. Download data across the whole time period
    # 2. Be able to insert event markers across the whole thing