# Olist E-commerce Business Analysis

## Current Progress
- [x] Initial data loading and verification
- [x] Basic EDA
- [ ] Customer analysis
- [ ] Sales analysis & forecasting
- [ ] Seller performance metrics

## Project Overview
This project aims to analyze the Olist E-commerce business, providing insights into customer behavior, sales performance, and seller performance.

## Data Sources

- [Olist E-commerce Dataset](URL_ADDRESS.kaggle.com/datasets/olistbr/brazilian-ecommerce)

## Data Schema
![Data Schema](./images/schema.png)

## Project Structure
```
olist_ecommerce_analysis/
├── README.md
├── requirements.txt
├── .gitignore
├── setup.py
├── data/
│   ├── raw/
│   │   └── .gitkeep
│   └── processed/
│       └── .gitkeep
├── notebooks/
│   ├── 01_initial_eda.ipynb
│   ├── 02_customer_analysis.ipynb
│   └── 03_sales_analysis.ipynb
├── scripts/
│   ├── __init__.py
│   ├── transform_data.py
│   ├── utils.py
│   └── config.py
├── tests/
│   ├── __init__.py
│   └── test_transform_data.py
└── docs/
    └── data_dictionary.md
```
## Next Steps
1. Develop comprehensive data cleaning pipeline
2. Create customer segmentation analysis
3. Build sales forecasting models