import pandas as pd
import os

def check_date_ranges(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Convert 'Open Time' to datetime
    df['Open Time'] = pd.to_datetime(df['Open Time'])
    
    # List of data sources
    sources = ['BTCARS', 'BTCUSDT', 'USDCHF']
    
    for source in sources:
        # Filter for non-null values in the source
        source_df = df[df[f'Open_{source}'].notnull()]
        
        if not source_df.empty:
            start_date = source_df['Open Time'].min()
            end_date = source_df['Open Time'].max()
            print(f"{source} date range:")
            print(f"  Start: {start_date}")
            print(f"  End: {end_date}")
            print(f"  Total days: {(end_date - start_date).days + 1}")
        else:
            print(f"No data available for {source}")
        print()

def main():
    file_path = './data/consolidated_data.csv'
    
    if os.path.exists(file_path):
        check_date_ranges(file_path)
    else:
        print(f"Error: {file_path} not found.")

if __name__ == "__main__":
    main()