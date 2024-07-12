import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns

def perform_regression(master_csv: str):
    # Load the data
    data = pd.read_csv(master_csv, header=None, names=[
        "Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time",
        "Base Asset Volume", "Number of Trades", "Taker Buy Volume",
        "Taker Buy Base Asset Volume", "Ignore"
    ])

    # Convert timestamp to datetime
    data['Open Time'] = pd.to_datetime(data['Open Time'], unit='ms')

    # Create a numeric time variable (hours since start)
    data['Hours'] = (data['Open Time'] - data['Open Time'].min()).dt.total_seconds() / 3600

    # Prepare X and y
    X = data[['Hours']]
    y = data['Open']

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and fit the model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Make predictions
    y_pred = model.predict(X_test)

    # Print results
    print(f"Coefficient: {model.coef_[0]:.4f}")
    print(f"Intercept: {model.intercept_:.4f}")
    print(f"R-squared: {model.score(X_test, y_test):.4f}")

    # Plot the results
    plt.figure(figsize=(12, 6))
    sns.scatterplot(x='Hours', y='Open', data=data.sample(n=1000), alpha=0.5)
    sns.lineplot(x=X_test['Hours'], y=y_pred, color='red')
    plt.title('Linear Regression: Open Price vs Time')
    plt.xlabel('Hours since start')
    plt.ylabel('Open Price')
    plt.show()

# Usage
currency = "BTCUSDT"
date = "2023-10-22"
master_csv = f"./data/{currency}/{date}/master_data.csv"
perform_regression(master_csv)