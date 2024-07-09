import os
import requests
from datetime import datetime, timedelta
from zipfile import ZipFile

def fetch_and_extract(url, dest_folder):
    response = requests.get(url)
    if response.status_code == 200:
        zip_path = os.path.join(dest_folder, os.path.basename(url))
        with open(zip_path, 'wb') as file:
            file.write(response.content)
        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(dest_folder)
        os.remove(zip_path)
        print(f"Downloaded and extracted: {url}")
    else:
        print(f"Failed to download: {url}")

def main():
    base_url = "https://data.binance.vision/data/spot/daily/klines/BTCARS/1m/BTCARS-1m-"
    date_format = "%Y-%m-%d"
    target_date = datetime.strptime("2023-08-13", date_format)
    dest_folder = "./data"

    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    for i in range(-3, 4):
        date = target_date + timedelta(days=i)
        date_str = date.strftime(date_format)
        url = f"{base_url}{date_str}.zip"
        fetch_and_extract(url, dest_folder)

if __name__ == "__main__":
    main()
