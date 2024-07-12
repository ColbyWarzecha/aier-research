import pandas as pd
from datetime import datetime
# Purpose: Format the USDCHF data

# currency_pair = "USDCHF"
# data_folder = f"./data/{currency_pair}"
# master_csv = f"{data_folder}/master_data.csv"

def convert_to_milliseconds(date_string):
    return int(datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)

input_file = 'input.csv'
output_file = 'output.csv'

# Read the CSV file
df = pd.read_csv(input_file, parse_dates=['time'])

# Convert time to milliseconds
df['time'] = df['time'].apply(lambda x: int(x.timestamp() * 1000))

# Reorder columns to match the desired schema
df = df[['time', 'open', 'high', 'low', 'close', 'volume']]

# Write to CSV without index and header
df.to_csv(output_file, index=False, header=False)

print(f"Data has been converted and written to {output_file}")