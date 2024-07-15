import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Set the event date (August 13, 2023)
event_date = datetime(2023, 8, 13)
start_date = event_date - timedelta(days=3)
end_date = event_date + timedelta(days=3)

# Function to process each chunk
def process_chunk(chunk):
    chunk['Open Time'] = pd.to_datetime(chunk['Open Time'])
    filtered_chunk = chunk[(chunk['Open Time'] >= start_date) & (chunk['Open Time'] <= end_date)]
    if not filtered_chunk.empty:
        filtered_chunk['Return_BTCUSDT'] = filtered_chunk['Open_BTCUSDT'].pct_change()
        filtered_chunk['Return_USDCHF'] = filtered_chunk['Open_USDCHF'].pct_change()
    return filtered_chunk

# Process data in chunks and write to a new CSV
chunksize = 10000  # Adjust this based on your system's memory
output_file = './data/processed_data.csv'

for i, chunk in enumerate(pd.read_csv("./data/consolidated_data.csv", chunksize=chunksize)):
    processed_chunk = process_chunk(chunk)
    if i == 0:
        processed_chunk.to_csv(output_file, index=False, mode='w')
    else:
        processed_chunk.to_csv(output_file, index=False, mode='a', header=False)

# Read the processed data
filtered_data = pd.read_csv(output_file, parse_dates=['Open Time'])

# Run the OLS regression
filtered_data = filtered_data.dropna()  # Remove NaN values
results = smf.ols('Return_BTCUSDT ~ Return_USDCHF', data=filtered_data).fit()

# Calculate expected returns and abnormal returns
filtered_data['Expected_Return_BTCUSDT'] = results.predict(filtered_data)
filtered_data['Abnormal_Return_BTCUSDT'] = filtered_data['Return_BTCUSDT'] - filtered_data['Expected_Return_BTCUSDT']
filtered_data['Cumulative_Abnormal_Return'] = filtered_data['Abnormal_Return_BTCUSDT'].cumsum()

# Write the final results to CSV
filtered_data.to_csv('./data/final_results.csv', index=False)

# Create the plot
plt.figure(figsize=(12, 6))
plt.plot(filtered_data['Open Time'], filtered_data['Cumulative_Abnormal_Return'])
plt.axvline(event_date, color='r', linestyle='--', label='Event Date')
plt.axhline(0, color='k', linestyle='-', linewidth=0.5)
plt.title('Cumulative Abnormal Returns around August 13, 2023')
plt.xlabel('Date')
plt.ylabel('Cumulative Abnormal Return')
plt.legend()
plt.gcf().autofmt_xdate()
plt.tight_layout()
plt.savefig('./data/cumulative_abnormal_returns.png')
plt.close()

print("Processing complete. Results saved in './data/final_results.csv' and plot saved as './data/cumulative_abnormal_returns.png'")