import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import timezone, timedelta
import statsmodels.formula.api as smf
from statsmodels.regression.linear_model import RegressionResultsWrapper
import os
from src.utils import load_config

def load_and_prepare_data(master_csv: str, currency_pairs: list) -> pd.DataFrame:
    """
    Load and prepare the financial data from a CSV file.

    Args:
        master_csv (str): Path to the master CSV file.
        currency_pairs (list): List of currency pairs to analyze.

    Returns:
        pd.DataFrame: Prepared DataFrame with calculated returns.
    """
    data = pd.read_csv(
        master_csv,
        header=None,
        names=[
            "Open Time", "Open", "High", "Low", "Close", "Volume",
            "Close Time", "Base Asset Volume", "Number of Trades",
            "Taker Buy Volume", "Taker Buy Base Asset Volume", "Ignore"
        ]
    )
    data["Open Time"] = pd.to_datetime(data["Open Time"], unit="ms", utc=True)
    data["Close Time"] = pd.to_datetime(data["Close Time"], unit="ms", utc=True)

    for token in currency_pairs:
        data[f"{token}_return"] = data["Close"].pct_change()
        data[f"{token}_log_return"] = np.log(data["Close"]) - np.log(data["Close"].shift(1))

    return data

def visualize_data(data: pd.DataFrame, notable_events: dict, currency_pair: str,
                   event_date: str, time_window: int, output_folder: str, show: bool = False) -> None:
    """
    Visualize the financial data around a specific event date.

    Args:
        data (pd.DataFrame): Prepared financial data.
        notable_events (dict): Dictionary of notable events.
        currency_pair (str): Currency pair being analyzed.
        event_date (str): Date of the event.
        time_window (int): Number of days before and after the event to visualize.
        output_folder (str): Folder to save the output image.
        show (bool): Whether to display the plot. Defaults to False.
    """
    event_datetime = pd.to_datetime(event_date).tz_localize(timezone.utc)
    start_date = event_datetime - timedelta(days=time_window)
    end_date = event_datetime + timedelta(days=time_window)
    data_window = data[(data["Open Time"] >= start_date) & (data["Open Time"] <= end_date)]

    plt.figure(figsize=(15, 10))
    sns.lineplot(x=data_window["Open Time"], y=data_window["Open"], label="Open", color="blue")

    _plot_notable_events(notable_events, start_date, end_date)

    plt.title(f"{currency_pair} - {time_window} days before and after {event_date}")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    _save_and_show_plot(output_folder, currency_pair, event_date, time_window, show)

def _plot_notable_events(notable_events: dict, start_date: pd.Timestamp, end_date: pd.Timestamp) -> None:
    """
    Plot vertical lines for notable events within the given date range.

    Args:
        notable_events (dict): Dictionary of notable events.
        start_date (pd.Timestamp): Start date of the plot.
        end_date (pd.Timestamp): End date of the plot.
    """
    sorted_events = sorted(notable_events.items(), key=lambda x: pd.to_datetime(x[0]))
    colors = plt.cm.rainbow(np.linspace(0, 1, len(sorted_events)))

    for i, (date_str, description) in enumerate(sorted_events):
        notable_time = pd.to_datetime(date_str).tz_convert("UTC")
        if start_date <= notable_time <= end_date:
            plt.axvline(x=notable_time, color=colors[i], linestyle="--", label=description)

def _save_and_show_plot(output_folder: str, currency_pair: str, event_date: str, time_window: int, show: bool) -> None:
    """
    Save the plot to a file and optionally display it.

    Args:
        output_folder (str): Folder to save the output image.
        currency_pair (str): Currency pair being analyzed.
        event_date (str): Date of the event.
        time_window (int): Number of days before and after the event.
        show (bool): Whether to display the plot.
    """
    filename = f"{currency_pair}_{event_date}_window_{time_window}days.png"
    filepath = os.path.join(output_folder, filename)
    plt.savefig(filepath, bbox_inches="tight")
    print(f"Image saved as {filepath}")

    if show:
        plt.show()
    plt.close()

def prepare_did_data(df: pd.DataFrame, event_timestamp: pd.Timestamp, currency_pairs: list,
                     use_log_returns: bool = True, window_days: int = 2) -> pd.DataFrame:
    """
    Prepare data for Difference-in-Differences (DiD) analysis.

    Args:
        df (pd.DataFrame): The input dataframe containing the data.
        event_timestamp (pd.Timestamp): The timestamp of the event.
        currency_pairs (list): List of currency pairs to analyze.
        use_log_returns (bool): Whether to use log returns or simple returns. Defaults to True.
        window_days (int): Number of days before and after the event to include. Defaults to 2.

    Returns:
        pd.DataFrame: A long-format dataframe suitable for DiD analysis.
    """
    event_timestamp = event_timestamp.tz_localize("UTC") if event_timestamp.tzinfo is None else event_timestamp.tz_convert("UTC")
    start_time = event_timestamp - timedelta(days=window_days)
    end_time = event_timestamp + timedelta(days=window_days)

    df_window = df[(df["Open Time"] >= start_time) & (df["Open Time"] <= end_time)]

    return_type = "log_return" if use_log_returns else "return"
    value_vars = [f"{token}_{return_type}" for token in currency_pairs]

    df_long = pd.melt(df_window, id_vars=["Open Time"], value_vars=value_vars, var_name="asset", value_name="return_value")
    df_long["post"] = (df_long["Open Time"] > event_timestamp).astype(int)
    
    for token in currency_pairs:
        df_long[f"treatment_{token.lower()}"] = (df_long["asset"] == f"{token}_{return_type}").astype(int)
    
    return df_long

def run_did_model(df: pd.DataFrame, treatment_var: str) -> RegressionResultsWrapper:
    """
    Run a Difference-in-Differences regression model.

    Args:
        df (pd.DataFrame): Prepared data for DiD analysis.
        treatment_var (str): Name of the treatment variable.

    Returns:
        smf.OLSResults: Fitted OLS model results.
    """
    formula = f"return_value ~ treatment_{treatment_var} + post + treatment_{treatment_var}:post"
    return smf.ols(formula=formula, data=df).fit()

def visualize_did_results(df_did: pd.DataFrame, event_timestamp: pd.Timestamp, event_name: str,
                          output_folder: str, use_log_returns: bool = False) -> None:
    """
    Visualize the results of the Difference-in-Differences analysis.

    Args:
        df_did (pd.DataFrame): DataFrame with DiD analysis data.
        event_timestamp (pd.Timestamp): Timestamp of the event.
        event_name (str): Name or description of the event.
        output_folder (str): Folder to save the output image.
        use_log_returns (bool): Whether log returns were used. Defaults to True.
    """
    return_type = "Log Return" if use_log_returns else "Return"
    plt.figure(figsize=(12, 6))
    
    for asset in df_did["asset"].unique():
        data = df_did[df_did["asset"] == asset]
        plt.plot(data["Open Time"], data["return_value"], label=asset)
    
    plt.axvline(event_timestamp, color="r", linestyle="--", label="Event")
    plt.title(f"Asset {return_type}s Around the Event: {event_name}")
    plt.xlabel("Time")
    plt.ylabel(return_type)
    plt.legend()
    plt.tight_layout()

    filename = f"did_results_{event_timestamp.strftime('%Y-%m-%d')}.png"
    filepath = os.path.join(output_folder, filename)
    plt.savefig(filepath, bbox_inches="tight")
    print(f"DiD results image saved as {filepath}")
    plt.close()

def analyze_event(df: pd.DataFrame, event_timestamp: pd.Timestamp, event_name: str,
                  config: dict, output_folder: str, use_log_returns: bool = True) -> None:
    """
    Perform Difference-in-Differences analysis for a specific event.

    Args:
        df (pd.DataFrame): Prepared financial data.
        event_timestamp (pd.Timestamp): Timestamp of the event.
        event_name (str): Name or description of the event.
        config (dict): Configuration dictionary.
        output_folder (str): Folder to save output files.
        use_log_returns (bool): Whether to use log returns. Defaults to True.
    """
    currency_pairs = config["currency_pairs"]
    df_did = prepare_did_data(df, event_timestamp, currency_pairs, use_log_returns, config["time_window"])

    results_summary = f"\nAnalysis for event: {event_name} at {event_timestamp}\n"
    for token in currency_pairs:
        model = run_did_model(df_did, token.lower())
        results_summary += f"\n{token} DiD Model Results:\n"
        results_summary += str(model.summary()) + "\n"
        did_estimator = model.params[f"treatment_{token.lower()}:post"]
        results_summary += f"{token} DiD Estimator: {did_estimator}\n"

    _save_regression_results(output_folder, event_timestamp, results_summary)
    visualize_did_results(df_did, event_timestamp, event_name, output_folder, use_log_returns)

def _save_regression_results(output_folder: str, event_timestamp: pd.Timestamp, results_summary: str) -> None:
    """
    Save regression results to a file.

    Args:
        output_folder (str): Folder to save the results file.
        event_timestamp (pd.Timestamp): Timestamp of the event.
        results_summary (str): Summary of regression results.
    """
    filename = f"regression_results_{event_timestamp.strftime('%Y-%m-%d')}.txt"
    filepath = os.path.join(output_folder, filename)
    with open(filepath, "w") as f:
        f.write(results_summary)
    print(f"Regression results saved to {filepath}")

def main(config_path: str) -> None:
    """
    Main function to run the financial analysis.

    Args:
        config_path (str): Path to the configuration file.
    """
    config = load_config(config_path)
    currency_pair = config["currency"]
    data_folder = f"./data/{currency_pair}"
    master_csv = f"{data_folder}/master_data.csv"

    output_folder = f"./output_{currency_pair}"
    os.makedirs(output_folder, exist_ok=True)

    df = load_and_prepare_data(master_csv, config["currency_pairs"])

    for event_date in config["event_dates"]:
        visualize_data(df, config["notable_events"], currency_pair, event_date,
                       config["time_window"], output_folder, config["show_plots"])

        event_timestamp = pd.to_datetime(event_date)
        analyze_event(df, event_timestamp, f"Event on {event_date}", config,
                      output_folder, config.get("use_log_returns"))

if __name__ == "__main__":
    config_path = "config.yaml"
    main(config_path)