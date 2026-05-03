🧠 Home Credit Risk Modeling Pipeline (XGBoost)
📌 Project Overview

This project builds an end-to-end credit risk modeling pipeline using the Home Credit dataset.

It simulates how financial institutions assess loan default risk by combining:

Data ingestion & storage
Data modeling & feature engineering
Machine learning (XGBoost)
Risk scoring output & visualization

The goal is to replicate a simplified real-world risk analytics workflow rather than a standalone modeling task.

🏗️ Pipeline Architecture
Raw Data (Kaggle)
   ↓
Data Storage (Azure Blob / Local Staging)
   ↓
Data Modeling (Relational Structure Simulation)
   ↓
Data Processing & Feature Engineering (Python / SQL)
   ↓
Model Training (XGBoost)
   ↓
Risk Scoring Output
   ↓
Visualization (Tableau)

📂 Data Architecture (Simulated Data Warehouse)

To reflect real-world financial data systems, the dataset is structured into a relational format:

Core Tables
application → customer-level information (main table)
bureau → external credit history
previous_application → past loan applications
Data Modeling Approach
Designed a simplified star-schema-like structure
Performed table joins and aggregations to create features
Built customer-level features such as:
Credit history length
Previous default signals
Loan behavior patterns

This step simulates how raw financial data is transformed into model-ready datasets in enterprise environments.

💾 Data Storage & Processing
Data Storage
Raw data stored in:
Local staging (/data/raw)
(Planned) Azure Blob Storage
Data Layers
/data
   /raw          → original data
   /processed    → cleaned data
   /features     → model-ready dataset
Processing
Python (Pandas, NumPy)
SQL-style transformations (joins, aggregations)
Missing value handling & feature scaling
⚙️ Feature Engineering

Key feature engineering techniques:

Aggregation of bureau and previous applications
Ratio features (e.g., debt/income)
Temporal features (credit history length)
Handling categorical variables (encoding)

🤖 Model Development
Model: XGBoost
Objective: Binary classification (default / non-default)
Techniques:
Cross-validation
Feature importance analysis

📊 Output & Business Interpretation
Risk Scoring
Output: Probability of default (PD)
Customers are ranked based on risk level
Visualization
Built dashboard using Tableau:
Risk distribution
Feature importance
Customer segmentation

🧩 Key Highlights
Built a complete ML pipeline, not just a model
Simulated real-world financial data flow
Applied data modeling concepts (relational + aggregation)
Focused on business interpretability (risk scoring)

🚀 Future Improvements
Deploy pipeline using Azure (Blob + Data Factory)
Add model monitoring
Automate pipeline execution
Improve feature engineering with time-series logic

## Result
Private Score AUC 0.7612 On Kaggle!

## How to Run
1. Clone this repo.
2. Run the notebook in Kaggle or Jupyter.
