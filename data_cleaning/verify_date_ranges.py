import pandas as pd
import os

def check_minute_by_minute_data(df, event_dates):
    # Convert 'Open Time' to datetime if it's not already, and make it timezone-aware
    if df['Open Time'].dtype != 'datetime64[ns, UTC]':
        df['Open Time'] = pd.to_datetime(df['Open Time'], utc=True)
    
    # List of data sources
    sources = ['BTCUSDT', 'USDCHF']
    
    for event_date in event_dates:
        event_date = pd.to_datetime(event_date, utc=True)
        start_date = event_date - pd.Timedelta(days=5)
        end_date = event_date + pd.Timedelta(days=5)
        
        print(f"Checking data for event date: {event_date}")
        print(f"Time range: {start_date} to {end_date}")
        
        for source in sources:
            # Filter for non-null values in the source
            source_df = df[df[f'Open_{source}'].notnull()]
            source_df = source_df[(source_df['Open Time'] >= start_date) & (source_df['Open Time'] <= end_date)]
            
            if source_df.empty:
                print(f"No data available for {source} in the given time range.")
                continue
            
            # Check for minute-by-minute data
            all_minutes = pd.date_range(start=start_date, end=end_date, freq='T', tz='UTC')
            available_minutes = source_df['Open Time']
            missing_minutes = all_minutes.difference(available_minutes)
            
            if missing_minutes.empty:
                print(f"{source}: Minute-by-minute data is complete for the given time range.")
            else:
                print(f"{source}: Missing data for the following timestamps:")
                print(missing_minutes)
            print()

def main():
    file_path = './data/consolidated_data.csv'
    event_dates = [
        "2023-08-13 23:00:00-03:00",
        "2023-10-22 21:00:00-03:00",
        "2023-12-21 15:30:00-03:00"
    ]
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        check_minute_by_minute_data(df, event_dates)
    else:
        print(f"Error: {file_path} not found.")

if __name__ == "__main__":
    main()