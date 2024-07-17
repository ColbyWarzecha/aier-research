import pandas as pd
import os

def load_and_process_data(directory):
    file_path = os.path.join(directory, "master_data.csv")
    if os.path.exists(file_path):
        columns = [
            "Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time",
            "Base Asset Volume", "Number of Trades", "Taker Buy Volume",
            "Taker Buy Base Asset Volume", "Ignore"
        ]
        df = pd.read_csv(file_path, header=None, names=columns)
        df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
        return df[['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume']]
    else:
        print(f"Warning: {file_path} not found.")
        return pd.DataFrame()

def main():
    # Load BTC/ARS data
    btcars_df = load_and_process_data('./data/BTCARS')
    btcars_df = btcars_df.add_suffix('_BTCARS')
    btcars_df = btcars_df.rename(columns={'Open Time_BTCARS': 'Open Time'})

    # Load BTC/USDT data
    btcusdt_df = load_and_process_data('./data/BTCUSDT')
    btcusdt_df = btcusdt_df.add_suffix('_BTCUSDT')
    btcusdt_df = btcusdt_df.rename(columns={'Open Time_BTCUSDT': 'Open Time'})

    # Load USD/CHF data
    usdchf_df = load_and_process_data('./data/USDCHF')
    usdchf_df = usdchf_df.add_suffix('_USDCHF')
    usdchf_df = usdchf_df.rename(columns={'Open Time_USDCHF': 'Open Time'})

    # Merge all dataframes
    merged_df = pd.merge(btcars_df, btcusdt_df, on='Open Time', how='outer')
    merged_df = pd.merge(merged_df, usdchf_df, on='Open Time', how='outer')

    # Sort by timestamp
    merged_df = merged_df.sort_values('Open Time')

    # Save to CSV
    output_path = './data/consolidated_data.csv'
    merged_df.to_csv(output_path, index=False)
    print(f"Consolidated data saved to {output_path}")

if __name__ == "__main__":
    main()