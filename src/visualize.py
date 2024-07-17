import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import argparse
from datetime import timezone, timedelta
from utils import load_config
import os

def visualize_data(master_csv: str, notable_events: dict, currency_pair: str, event_date: str, time_window: int, show: bool = False) -> None:
    data = pd.read_csv(master_csv, header=None, names=[
        "Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time",
        "Base Asset Volume", "Number of Trades", "Taker Buy Volume",
        "Taker Buy Base Asset Volume", "Ignore"
    ])
    data["Open Time"] = pd.to_datetime(data["Open Time"], unit='ms', utc=True)
    data["Close Time"] = pd.to_datetime(data["Close Time"], unit='ms', utc=True)

    event_datetime = pd.to_datetime(event_date).tz_localize(timezone.utc)
    start_date = event_datetime - timedelta(days=time_window)
    end_date = event_datetime + timedelta(days=time_window)

    data = data[(data["Open Time"] >= start_date) & (data["Open Time"] <= end_date)]

    plt.figure(figsize=(15, 10))
    sns.lineplot(x=data["Open Time"], y=data["Open"], label="Open", color="blue")

    for date_str, description in notable_events.items():
        notable_time = pd.to_datetime(date_str).tz_convert('UTC')
        if start_date <= notable_time <= end_date:
            plt.axvline(x=notable_time, color='purple', linestyle='--', label=description)
            plt.text(notable_time, data["Open"].max() * 0.9, description, rotation=30, verticalalignment='bottom', color='purple')

    plt.title(f"{currency_pair} - {time_window} days before and after {event_date}")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    output_folder = "./output_images"
    os.makedirs(output_folder, exist_ok=True)

    filename = f"{currency_pair}_{event_date}_window_{time_window}days.png"
    filepath = os.path.join(output_folder, filename)

    plt.savefig(filepath)
    print(f"Image saved as {filepath}")

    if show is True:
        plt.show()

    plt.close()

def main() -> None:
    parser = argparse.ArgumentParser(description="Visualize currency data around a specific event.")
    parser.add_argument("--currency", type=str, required=True, help="The currency pair you wish to visualize")
    parser.add_argument("--event-date", type=str, required=True, help="The date of the event in YYYY-MM-DD format")
    parser.add_argument("--time-window", type=int, default=2, help="Number of days before and after the event to visualize")
    args = parser.parse_args()

    config_file = "config.yaml"
    config = load_config(config_file)

    currency_pair = args.currency
    data_folder = f"./data/{currency_pair}"
    master_csv = f"{data_folder}/master_data.csv"

    visualize_data(master_csv, config['notable_events'], currency_pair, args.event_date, args.time_window)

if __name__ == "__main__":
    main()