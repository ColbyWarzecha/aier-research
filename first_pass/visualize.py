import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Sample CSV file name
csv_file = "./data/master_data.csv"

# Read the CSV file into a DataFrame
data = pd.read_csv(csv_file, header=None, names=[
    "Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time",
    "Base Asset Volume", "Number of Trades", "Taker Buy Volume",
    "Taker Buy Base Asset Volume", "Ignore"
])

# Convert the timestamps to readable date-time format
data["Open Time"] = pd.to_datetime(data["Open Time"], unit='ms')
data["Close Time"] = pd.to_datetime(data["Close Time"], unit='ms')

# Plot the data using Seaborn
plt.figure(figsize=(15, 10))

# Plot Open, High, Low, Close prices
sns.lineplot(x=data["Open Time"], y=data["Open"], label="Open", color="blue")
# sns.lineplot(x=data["Open Time"], y=data["High"], label="High", color="green")
# sns.lineplot(x=data["Open Time"], y=data["Low"], label="Low", color="red")
# sns.lineplot(x=data["Open Time"], y=data["Close"], label="Close", color="orange")

# Add a vertical line for the time when Javier Milei was declared the winner
victory_time = pd.Timestamp('2023-08-13 22:00:00')
plt.axvline(x=victory_time, color='purple', linestyle='--', label="Milei Declared Winner")
plt.text(victory_time, data["Open"].max() * 0.92, "Milei Declared Winner", rotation=0, verticalalignment='bottom', color='purple')

# Enhance the plot
plt.title("BTCARS - One Day Activity")
plt.xlabel("Time")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)

# Show the plot
plt.tight_layout()
plt.show()