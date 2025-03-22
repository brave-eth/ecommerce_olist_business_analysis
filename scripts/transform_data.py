"""
This script loads raw Olist CSV files from data/raw/,
performs merges, and outputs a single cleaned file in data/processed/.
No SQL needed -- pure Python/pandas approach.
"""

import pandas as pd
import os

# Adjust these paths for your local project
RAW_DATA_PATH = "../data/raw"
PROCESSED_DATA_PATH = "../data/processed"

def load_datasets():
    """
    Loads Olist CSV files as pandas DataFrames.
    Returns a dict of DataFrames keyed by file name.
    """
    df_orders = pd.read_csv(os.path.join(RAW_DATA_PATH, "olist_orders_dataset.csv"))
    df_order_items = pd.read_csv(os.path.join(RAW_DATA_PATH, "olist_order_items_dataset.csv"))
    df_customers = pd.read_csv(os.path.join(RAW_DATA_PATH, "olist_customers_dataset.csv"))
    df_sellers = pd.read_csv(os.path.join(RAW_DATA_PATH, "olist_sellers_dataset.csv"))
    df_products = pd.read_csv(os.path.join(RAW_DATA_PATH, "olist_products_dataset.csv"))

    return {
        "orders": df_orders,
        "order_items": df_order_items,
        "customers": df_customers,
        "sellers": df_sellers,
        "products": df_products
    }

def basic_cleaning(df_dict):
    """
    Perform basic cleaning steps on each DataFrame:
    - Fix column dtypes (e.g., convert date strings to datetime).
    - Handle missing values if needed.
    - Return the updated df_dict.
    """
    # Example: convert timestamp columns in orders to datetime
    orders = df_dict["orders"]
    date_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
    for col in date_cols:
        orders[col] = pd.to_datetime(orders[col], errors='coerce')

    df_dict["orders"] = orders
    # Repeat such conversions for other DataFrames if needed

    return df_dict

def merge_dfs(df_dict):
    """
    Merge DataFrames into one 'master' DataFrame for analysis.
    Example: link orders with customers, then link order_items, etc.
    """
    # Merge orders and customers (common key: customer_id)
    df_merged = pd.merge(
        df_dict["orders"],
        df_dict["customers"],
        on="customer_id",
        how="left"  # or 'inner' if you only want matching records
    )

    # Then merge in order_items (common key: order_id)
    df_merged = pd.merge(
        df_merged,
        df_dict["order_items"],
        on="order_id",
        how="left"
    )

    # Optionally merge sellers or products, etc., if relevant.
    # e.g., df_merged = pd.merge(df_merged, df_dict["sellers"], on="seller_id", how="left")
    # Additional merges for products, etc.

    return df_merged

def main():
    # 1. Load
    df_dict = load_datasets()

    # 2. Clean / transform data
    df_dict = basic_cleaning(df_dict)

    # 3. Merge
    df_combined = merge_dfs(df_dict)

    # 4. Example: drop rows with missing customer_id or order_id, if that makes sense
    df_combined.dropna(subset=["order_id", "customer_id"], inplace=True)

    # 5. Save the final combined DataFrame
    output_path = os.path.join(PROCESSED_DATA_PATH, "olist_combined.csv")
    df_combined.to_csv(output_path, index=False)
    print(f"Combined dataset saved to {output_path}")

if __name__ == "__main__":
    main()