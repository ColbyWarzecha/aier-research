import os
import pandas as pd

def combine_csv_files(data_folder, master_csv):
    all_data = []

    for file_name in os.listdir(data_folder):
        if file_name.endswith('.csv'):
            file_path = os.path.join(data_folder, file_name)
            data = pd.read_csv(file_path, header=None)
            all_data.append(data)
    
    if all_data:
        combined_data = pd.concat(all_data, ignore_index=True)
        combined_data.to_csv(master_csv, index=False, header=False)
        print(f"Master CSV created: {master_csv}")
    else:
        print("No CSV files found to combine.")

def main():
    data_folder = "./data"
    master_csv = f"{data_folder}/master_data.csv"
    combine_csv_files(data_folder, master_csv)

if __name__ == "__main__":
    main()
