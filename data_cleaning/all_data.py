import os
import requests
import logging
from datetime import datetime, timedelta
from zipfile import ZipFile
import pandas as pd
import yaml
from src.utils import load_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_and_extract(url: str, dest_folder: str) -> None:
    """
    Fetches and extracts a ZIP file from a given URL to the destination folder.

    Args:
        url (str): The URL of the ZIP file to download.
        dest_folder (str): The folder where the ZIP file should be extracted.

    Returns:
        None
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        zip_path = os.path.join(dest_folder, os.path.basename(url))
        with open(zip_path, 'wb') as file:
            file.write(response.content)
        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(dest_folder)
        os.remove(zip_path)
        logging.info(f"Downloaded and extracted: {url}")
    except requests.RequestException as e:
        logging.error(f"Failed to download {url}: {e}")

def download_data(base_url: str, start_date: datetime, end_date: datetime, dest_folder: str) -> None:
    """
    Downloads and extracts data for a range of dates.

    Args:
        base_url (str): The base URL template for the ZIP files.
        start_date (datetime): The start date for downloading data.
        end_date (datetime): The end date for downloading data.
        dest_folder (str): The folder where the data should be extracted.

    Returns:
        None
    """
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        url = f"{base_url}{date_str}.zip"
        fetch_and_extract(url, dest_folder)
        current_date += timedelta(days=1)

def combine_csv_files(data_folder: str, master_csv: str) -> None:
    """
    Combines all CSV files in a folder into a single master CSV file.

    Args:
        data_folder (str): The folder containing the CSV files to combine.
        master_csv (str): The path of the master CSV file to create.

    Returns:
        None
    """
    all_data = []

    for file_name in os.listdir(data_folder):
        if file_name.endswith('.csv'):
            file_path = os.path.join(data_folder, file_name)
            try:
                data = pd.read_csv(file_path, header=None)
                all_data.append(data)
            except pd.errors.EmptyDataError:
                logging.warning(f"Empty CSV file: {file_path}")
    
    if all_data:
        combined_data = pd.concat(all_data, ignore_index=True)
        combined_data.to_csv(master_csv, index=False, header=False)
        logging.info(f"Master CSV created: {master_csv}")
    else:
        logging.warning("No CSV files found to combine.")

def main() -> None:
    """
    Main function to download data and combine it into a master CSV file.

    Returns:
        None
    """
    config_file = "config.yaml"
    config = load_config(config_file)

    base_url_template = "https://data.binance.vision/data/spot/daily/klines/{pair}/1m/{pair}-1m-"
    date_format = "%Y-%m-%d"
    start_date = datetime.strptime("2023-06-21", date_format).date() # change this for different date range
    end_date = datetime.strptime("2023-12-31", date_format).date() # can go beyond, but this will do

    for currency_pair in config['currency_pairs']:
        data_folder = f"./data/{currency_pair}"
        master_csv = f"{data_folder}/master_data.csv"

        base_url = base_url_template.format(pair=currency_pair)
        download_data(base_url, start_date, end_date, data_folder)
        combine_csv_files(data_folder, master_csv)

if __name__ == "__main__":
    main()

    # TODO: Look up if the markets were reflecting data as it came in for: https://www.electoral.gob.ar/nuevo/index.php 