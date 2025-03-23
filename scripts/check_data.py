# 1. Download Olist dataset from Kaggle
# Place all CSV files in data/raw/

# 2. Create a quick Python script to verify data loading
# In scripts/check_data.py

import pandas as pd
import os

def check_data():
    data_path = './data/raw'
    for file in os.listdir(data_path):
        if file.endswith('.csv'):
            df = pd.read_csv(os.path.join(data_path, file))
            print(f"\nFile: {file}")
            print(f"Shape: {df.shape}")
            print("Columns:", df.columns.tolist())
            print("Missing values:", df.isnull().sum().sum())

if __name__ == "__main__":
    check_data()