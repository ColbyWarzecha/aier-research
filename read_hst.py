import mt4_hst
import zipfile
import os
import shutil

# Define paths
zip_path = "./data/USDCHF.hst.zip"
dest_folder = "./data/USDCHF"
hst_filename = "USDCHF.hst"
hst_path = os.path.join(dest_folder, hst_filename)

# Create destination folder if it doesn't exist
os.makedirs(dest_folder, exist_ok=True)

# Extract the zip file
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(dest_folder)

try:
    # Read the HST file
    df = mt4_hst.read_hst(hst_path)

    # Process the data (add your processing steps here)
    ## Simple Diagnostics
    print(df.describe())
    print(df.count())
    print(df.columns)
    print(df.tail())

    # You can add more processing steps here
    # For example:
    # df['new_column'] = df['close'] - df['open']
    # df.to_csv('processed_data.csv', index=False)

finally:
    # Re-zip the file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(hst_path, hst_filename)

    # Remove the extracted file
    os.remove(hst_path)

    # Optionally, remove the destination folder if it's empty
    if not os.listdir(dest_folder):
        os.rmdir(dest_folder)