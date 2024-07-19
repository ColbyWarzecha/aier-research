import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import timezone, timedelta
import statsmodels.formula.api as smf
import os
from src.utils import load_config

def load_and_prepare_data(master_csv: str, currency_pairs: list) -> pd.DataFrame:
    data = pd.read_csv(
        master_csv,
        header=None,
        names=[
            "Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time",
            "Base Asset Volume", "Number of Trades", "Taker Buy Volume",
            "Taker Buy Base Asset Volume", "Ignore",
        ],
    )
    data["Open Time"] = pd.to_datetime(data["Open Time"], unit="ms", utc=True)
    data["Close Time"] = pd.to_datetime(data["Close Time"], unit="ms", utc=True)
    
    # Calculate returns
    for token in currency_pairs:
        data[f"{token}_return"] = data[f"Close"].pct_change()
        data[f"{token}_log_return"] = np.log(data["Close"]) - np.log(data["Close"].shift(1))
    
    return data

def visualize_data(
    data: pd.DataFrame,
    notable_events: dict,
    currency_pair: str,
    event_date: str,
    time_window: int,
    output_folder: str,
    show: bool = False,
) -> None:
    event_datetime = pd.to_datetime(event_date).tz_localize(timezone.utc)
    start_date = event_datetime - timedelta(days=time_window)
    end_date = event_datetime + timedelta(days=time_window)
    data_window = data[(data["Open Time"] >= start_date) & (data["Open Time"] <= end_date)]
    
    plt.figure(figsize=(15, 10))
    sns.lineplot(x=data_window["Open Time"], y=data_window["Open"], label="Open", color="blue")
    
    sorted_events = sorted(notable_events.items(), key=lambda x: pd.to_datetime(x[0]))
    event_positions = {}
    colors = plt.cm.rainbow(np.linspace(0, 1, len(sorted_events)))
    
    for i, (date_str, description) in enumerate(sorted_events):
        notable_time = pd.to_datetime(date_str).tz_convert("UTC")
        if start_date <= notable_time <= end_date:
            color = colors[i]
            plt.axvline(x=notable_time, color=color, linestyle="--", label=description)
            if notable_time in event_positions:
                event_positions[notable_time] += 1
            else:
                event_positions[notable_time] = 0
    
    plt.title(f"{currency_pair} - {time_window} days before and after {event_date}")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
    plt.tight_layout()
    
    filename = f"{currency_pair}_{event_date}_window_{time_window}days.png"
    filepath = os.path.join(output_folder, filename)
    plt.savefig(filepath, bbox_inches="tight")
    print(f"Image saved as {filepath}")
    
    if show:
        plt.show()
    plt.close()

def prepare_did_data(df, event_timestamp, currency_pairs, use_log_returns=True, window_days=2):
    if event_timestamp.tzinfo is None:
        event_timestamp = event_timestamp.tz_localize('UTC')
    else:
        event_timestamp = event_timestamp.tz_convert('UTC')

    start_time = event_timestamp - timedelta(days=window_days)
    end_time = event_timestamp + timedelta(days=window_days)
    
    df_window = df[(df["Open Time"] >= start_time) & (df["Open Time"] <= end_time)]
    
    return_type = "log_return" if use_log_returns else "return"
    value_vars = [f"{token}_{return_type}" for token in currency_pairs]
    
    df_long = pd.melt(
        df_window,
        id_vars=["Open Time"],
        value_vars=value_vars,
        var_name="asset",
        value_name="return_value",
    )
    df_long["post"] = (df_long["Open Time"] > event_timestamp).astype(int)
    for token in currency_pairs:
        df_long[f"treatment_{token.lower()}"] = (df_long["asset"] == f"{token}_{return_type}").astype(int)
    return df_long

def run_did_model(df, treatment_var):
    formula = f"return_value ~ treatment_{treatment_var} + post + treatment_{treatment_var}:post"
    model = smf.ols(formula=formula, data=df).fit()
    return model

def visualize_did_results(df_did, event_timestamp, event_name, output_folder, use_log_returns=True):
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

def analyze_event(df, event_timestamp, event_name, config, output_folder, use_log_returns=True):
    currency_pairs = config['currency_pairs']
    df_did = prepare_did_data(df, event_timestamp, currency_pairs, use_log_returns, config['time_window'])
    
    results_summary = f"\nAnalysis for event: {event_name} at {event_timestamp}\n"
    for token in currency_pairs:
        model = run_did_model(df_did, token.lower())
        results_summary += f"\n{token} DiD Model Results:\n"
        results_summary += str(model.summary()) + "\n"
        did_estimator = model.params[f"treatment_{token.lower()}:post"]
        results_summary += f"{token} DiD Estimator: {did_estimator}\n"
    
    # Write results to file
    filename = f"regression_results_{event_timestamp.strftime('%Y-%m-%d')}.txt"
    filepath = os.path.join(output_folder, filename)
    with open(filepath, 'w') as f:
        f.write(results_summary)
    print(f"Regression results saved to {filepath}")
    
    visualize_did_results(df_did, event_timestamp, event_name, output_folder, use_log_returns)

def main(config_path: str):
    config = load_config(config_path)
    currency_pair = config['currency']
    data_folder = f"./data/{currency_pair}"
    master_csv = f"{data_folder}/master_data.csv"

    # Create output folder
    output_folder = f"./output_{currency_pair}"
    os.makedirs(output_folder, exist_ok=True)

    df = load_and_prepare_data(master_csv, config['currency_pairs'])

    # Visualization and analysis for each event date
    for event_date in config['event_dates']:
        # Visualization
        visualize_data(
            df,
            config["notable_events"],
            currency_pair,
            event_date,
            config['time_window'],
            output_folder,
            config['show_plots']
        )

        # DiD Analysis
        event_timestamp = pd.to_datetime(event_date)
        analyze_event(df, event_timestamp, f"Event on {event_date}", config, output_folder, config.get('use_log_returns', True))

if __name__ == "__main__":
    config_path = "config.yaml"
    main(config_path)