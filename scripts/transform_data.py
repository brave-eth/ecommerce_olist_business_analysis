#!/usr/bin/env conda run -n tensorflow_env python3
"""
Olist E-commerce Data Transformation Pipeline

This script processes the Brazilian E-commerce Public Dataset by Olist.
It loads all raw CSV files, performs necessary cleaning and transformations,
and creates processed datasets ready for analysis.

Dataset source: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
"""

import os
import logging
from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)

class OlistDataTransformer:
    """
    A class to handle the transformation of Olist e-commerce data.
    """
    
    def __init__(self, raw_data_path: str, processed_data_path: str):
        """
        Initialize the transformer with input and output paths.
        
        Args:
            raw_data_path (str): Path to directory containing raw CSV files
            processed_data_path (str): Path to directory for processed outputs
        """
        self.raw_data_path = raw_data_path
        self.processed_data_path = processed_data_path
        self.datasets: Dict[str, pd.DataFrame] = {}
        
        # Create processed directory if it doesn't exist
        os.makedirs(processed_data_path, exist_ok=True)
        
        # Expected CSV files in the raw data directory
        self.expected_files = [
            "olist_orders_dataset.csv",
            "olist_order_items_dataset.csv",
            "olist_products_dataset.csv",
            "olist_customers_dataset.csv",
            "olist_sellers_dataset.csv",
            "olist_order_payments_dataset.csv",
            "olist_order_reviews_dataset.csv",
            "olist_geolocation_dataset.csv",
            "product_category_name_translation.csv"
        ]

    def validate_raw_files(self) -> bool:
        """
        Check if all required raw files exist.
        
        Returns:
            bool: True if all files exist, False otherwise
        """
        missing_files = []
        for file in self.expected_files:
            if not os.path.exists(os.path.join(self.raw_data_path, file)):
                missing_files.append(file)
        
        if missing_files:
            logging.error(f"Missing files: {missing_files}")
            return False
        return True

    def load_datasets(self) -> None:
        """
        Load all CSV files into pandas DataFrames.
        """
        logging.info("Loading datasets...")
        
        try:
            # Load each dataset
            self.datasets = {
                "orders": pd.read_csv(os.path.join(self.raw_data_path, "olist_orders_dataset.csv")),
                "order_items": pd.read_csv(os.path.join(self.raw_data_path, "olist_order_items_dataset.csv")),
                "products": pd.read_csv(os.path.join(self.raw_data_path, "olist_products_dataset.csv")),
                "customers": pd.read_csv(os.path.join(self.raw_data_path, "olist_customers_dataset.csv")),
                "sellers": pd.read_csv(os.path.join(self.raw_data_path, "olist_sellers_dataset.csv")),
                "payments": pd.read_csv(os.path.join(self.raw_data_path, "olist_order_payments_dataset.csv")),
                "reviews": pd.read_csv(os.path.join(self.raw_data_path, "olist_order_reviews_dataset.csv")),
                "geolocation": pd.read_csv(os.path.join(self.raw_data_path, "olist_geolocation_dataset.csv")),
                "category_translation": pd.read_csv(os.path.join(self.raw_data_path, "product_category_name_translation.csv"))
            }
            
            # Log the shape of each dataset
            for name, df in self.datasets.items():
                logging.info(f"Loaded {name}: {df.shape[0]} rows, {df.shape[1]} columns")
                
        except Exception as e:
            logging.error(f"Error loading datasets: {str(e)}")
            raise

    def clean_datasets(self) -> None:
        """
        Clean all datasets by handling missing values, converting data types, etc.
        """
        logging.info("Cleaning datasets...")
        
        try:
            # Clean orders dataset
            date_columns = [
                "order_purchase_timestamp",
                "order_approved_at",
                "order_delivered_carrier_date",
                "order_delivered_customer_date",
                "order_estimated_delivery_date"
            ]
            for col in date_columns:
                self.datasets["orders"][col] = pd.to_datetime(self.datasets["orders"][col])

            # Clean reviews dataset
            review_date_columns = ["review_creation_date", "review_answer_timestamp"]
            for col in review_date_columns:
                self.datasets["reviews"][col] = pd.to_datetime(self.datasets["reviews"][col])

            # Clean order_items dataset
            self.datasets["order_items"]["shipping_limit_date"] = pd.to_datetime(
                self.datasets["order_items"]["shipping_limit_date"]
            )

            # Handle missing values in products
            self.datasets["products"].fillna({
                "product_category_name": "unknown",
                "product_name_lenght": 0,
                "product_description_lenght": 0,
                "product_photos_qty": 0,
                "product_weight_g": 0,
                "product_length_cm": 0,
                "product_height_cm": 0,
                "product_width_cm": 0
            }, inplace=True)

            logging.info("Basic cleaning completed")

        except Exception as e:
            logging.error(f"Error during cleaning: {str(e)}")
            raise

    def create_analytical_datasets(self) -> None:
        """
        Create various analytical datasets by combining and transforming the raw data.
        """
        logging.info("Creating analytical datasets...")
        
        try:
            # 1. Create order-centric dataset
            df_orders_full = self.datasets["orders"].merge(
                self.datasets["customers"],
                on="customer_id",
                how="left"
            ).merge(
                self.datasets["order_items"],
                on="order_id",
                how="left"
            ).merge(
                self.datasets["sellers"],
                on="seller_id",
                how="left"
            ).merge(
                self.datasets["products"],
                on="product_id",
                how="left"
            )

            # Add payment information
            df_orders_full = df_orders_full.merge(
                self.datasets["payments"],
                on="order_id",
                how="left"
            )

            # Add review scores
            df_orders_full = df_orders_full.merge(
                self.datasets["reviews"][["order_id", "review_score"]],
                on="order_id",
                how="left"
            )

            # Add category translations
            df_orders_full = df_orders_full.merge(
                self.datasets["category_translation"],
                on="product_category_name",
                how="left"
            )

            # Calculate delivery time in days
            df_orders_full["delivery_time_days"] = (
                df_orders_full["order_delivered_customer_date"] -
                df_orders_full["order_purchase_timestamp"]
            ).dt.total_seconds() / (24 * 60 * 60)

            # Save the full dataset
            output_path = os.path.join(self.processed_data_path, "olist_orders_full.csv")
            df_orders_full.to_csv(output_path, index=False)
            logging.info(f"Saved full orders dataset to {output_path}")

            # 2. Create customer-centric dataset
            df_customer_metrics = df_orders_full.groupby("customer_id").agg({
                "order_id": "count",
                "payment_value": "sum",
                "delivery_time_days": "mean",
                "review_score": "mean"
            }).rename(columns={
                "order_id": "total_orders",
                "payment_value": "total_spent",
                "delivery_time_days": "avg_delivery_days",
                "review_score": "avg_review_score"
            })

            # Save customer metrics
            output_path = os.path.join(self.processed_data_path, "olist_customer_metrics.csv")
            df_customer_metrics.to_csv(output_path)
            logging.info(f"Saved customer metrics to {output_path}")

            # 3. Create seller performance dataset
            df_seller_metrics = df_orders_full.groupby("seller_id").agg({
                "order_id": "count",
                "payment_value": "sum",
                "review_score": "mean",
                "delivery_time_days": "mean"
            }).rename(columns={
                "order_id": "total_orders",
                "payment_value": "total_revenue",
                "review_score": "avg_review_score",
                "delivery_time_days": "avg_delivery_days"
            })

            # Save seller metrics
            output_path = os.path.join(self.processed_data_path, "olist_seller_metrics.csv")
            df_seller_metrics.to_csv(output_path)
            logging.info(f"Saved seller metrics to {output_path}")

        except Exception as e:
            logging.error(f"Error creating analytical datasets: {str(e)}")
            raise

    def run_pipeline(self) -> None:
        """
        Execute the complete data transformation pipeline.
        """
        try:
            # Start time
            start_time = datetime.now()
            logging.info("Starting data transformation pipeline...")

            # Validate raw files
            if not self.validate_raw_files():
                raise FileNotFoundError("Missing required raw files")

            # Execute pipeline steps
            self.load_datasets()
            self.clean_datasets()
            self.create_analytical_datasets()

            # End time
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logging.info(f"Pipeline completed successfully in {duration:.2f} seconds")

        except Exception as e:
            logging.error(f"Pipeline failed: {str(e)}")
            raise

def main():
    """
    Main function to run the transformation pipeline.
    """
    # Define paths (adjust these to match your project structure)
    raw_data_path = "../data/raw"
    processed_data_path = "../data/processed"

    try:
        # Initialize and run the transformer
        transformer = OlistDataTransformer(raw_data_path, processed_data_path)
        transformer.run_pipeline()
        
    except Exception as e:
        logging.error(f"Pipeline execution failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()