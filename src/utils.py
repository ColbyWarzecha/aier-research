import yaml
import pandas as pd

def load_config(config_file: str) -> dict:
    """
    Loads configuration from a YAML file.

    Args:
        config_file (str): The path to the configuration file.

    Returns:
        dict: Configuration dictionary.
    """
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

def load_data() -> pd.DataFrame:
    df = pd.read_csv('./data/consolidated_data.csv')
    df['Open Time'] = pd.to_datetime(df['Open Time'])
    return df