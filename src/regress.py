import statsmodels.formula.api as smf
import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt
from src.utils import load_data


# Step 2: Calculate returns
def calculate_returns(df):
    for token in ["BTCARS", "BTCUSDT", "USDCHF"]:
        df[f"{token}_return"] = df[f"Close_{token}"].pct_change()
    return df


# Step 3: Prepare data for DiD model
def prepare_did_data(df, event_timestamp):
    start_time = event_timestamp - timedelta(days=2)
    end_time = event_timestamp + timedelta(days=2)

    df_window = df[(df["Open Time"] >= start_time) & (df["Open Time"] <= end_time)]

    # Reshape data for DiD model
    df_long = pd.melt(
        df_window,
        id_vars=["Open Time"],
        value_vars=["BTCARS_return", "BTCUSDT_return", "USDCHF_return"],
        var_name="asset",
        value_name="return_value",
    )

    df_long["post"] = (df_long["Open Time"] > event_timestamp).astype(int)
    df_long["treatment_btcars"] = (df_long["asset"] == "BTCARS_return").astype(int)
    df_long["treatment_btcusdt"] = (df_long["asset"] == "BTCUSDT_return").astype(int)

    return df_long


# Step 4: Run DiD model
def run_did_model(df, treatment_var):
    formula = f"return_value ~ treatment_{treatment_var} + post + treatment_{treatment_var}:post"
    model = smf.ols(formula=formula, data=df).fit()
    return model


def visualize_results(df_did, event_timestamp):
    # Time series plot of returns
    plt.figure(figsize=(12, 6))
    for asset in ["BTCARS_return", "BTCUSDT_return", "USDCHF_return"]:
        data = df_did[df_did["asset"] == asset]
        plt.plot(data["Open Time"], data["return_value"], label=asset)
    plt.axvline(event_timestamp, color="r", linestyle="--", label="Event")
    plt.title("Asset Returns Around the Event")
    plt.xlabel("Time")
    plt.ylabel("Return")
    plt.legend()
    plt.tight_layout()
    plt.show()


# Main execution
if __name__ == "__main__":
    # Load and prepare data
    df = load_data()
    df = calculate_returns(df)

    # Define event timestamp
    event_timestamp = pd.Timestamp(
        "2023-08-13 20:00:00"
    )  # Adjust this to the exact time of Milei's victory announcement

    # Prepare data for DiD model
    df_did = prepare_did_data(df, event_timestamp)

    # Run DiD models
    model_btcars = run_did_model(df_did, "btcars")
    model_btcusdt = run_did_model(df_did, "btcusdt")

    # Print results
    print("BTCARS DiD Model Results:")
    print(model_btcars.summary())

    print("\nBTCUSDT DiD Model Results:")
    print(model_btcusdt.summary())

    # Extract and print DiD estimators
    did_btcars = model_btcars.params["treatment_btcars:post"]
    did_btcusdt = model_btcusdt.params["treatment_btcusdt:post"]

    print(f"\nBTCARS DiD Estimator: {did_btcars}")
    print(f"BTCUSDT DiD Estimator: {did_btcusdt}")

    # Visualize time series
    visualize_results(df_did, event_timestamp)
