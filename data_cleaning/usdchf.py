import mt4_hst
import zipfile
import os
import pandas as pd

# Define paths
zip_path = "./data/USDCHF.hst.zip"
temp_folder = "./data/temp"
hst_filename = "USDCHF.hst"
hst_path = os.path.join(temp_folder, hst_filename)
output_folder = "./data/USDCHF"
master_file = os.path.join(output_folder, "master_data.csv")

# Create temporary and output folders if they don't exist
os.makedirs(temp_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# Extract the zip file
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(temp_folder)

try:
    # Read the HST file
    df = mt4_hst.read_hst(hst_path)

    # Convert 'time' column to datetime if it's not already
    df['time'] = pd.to_datetime(df['time'])

    # Filter data for 2023 only
    df_2023 = df[df['time'].dt.year == 2023]

    # Sort the data by time
    df_2023 = df_2023.sort_values('time')

    # Save all 2023 data to master_data.csv
    df_2023.to_csv(master_file, index=False)
    print(f"All 2023 data has been extracted and saved to {master_file}")

    # Print some statistics about the data
    print("\nData Statistics:")
    print(f"Total rows: {len(df_2023)}")
    print(f"Date range: from {df_2023['time'].min()} to {df_2023['time'].max()}")
    print("\nColumn descriptions:")
    print(df_2023.describe())

finally:
    # Remove the extracted file
    os.remove(hst_path)

    # Remove the temporary folder
    if os.path.exists(temp_folder):
        os.rmdir(temp_folder)

print("Processing complete.")