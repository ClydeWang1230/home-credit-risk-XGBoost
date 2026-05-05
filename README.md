# Credit Risk Modeling (Kaggle + Azure Pipeline)

## 📌 Overview

This project started as a **Kaggle-based credit risk modeling task** and was later extended into a **production-style ML pipeline with Azure integration**.

It demonstrates both:

* 📊 **Data analysis & modeling skills (Kaggle workflow)**
* ⚙️ **Data engineering & pipeline design (production workflow)**

---

# 🧠 Part 1: Data Analysis & Modeling (Kaggle)

## 🔍 Dataset

* Home Credit Default Risk dataset
* Multiple relational tables:

  * application_train
  * bureau
  * previous_application
  * etc.

---

## 📊 Exploratory Data Analysis

* Distribution of target variable
* Income vs default patterns
* Credit behavior insights

---

## 🧮 Feature Engineering

* Aggregations from relational tables:

  * `previous_application`
  * `bureau`
* Handling missing values
* Encoding categorical variables

---

## 🧠 Modeling

* Model: XGBoost
* Evaluation: AUC
* Feature importance analysis

---

## 🗄️ SQL Usage

* Data extraction and joins
* Feature aggregation logic

---

## 📈 Tableau Dashboard

* Visualized credit risk patterns
* Business-oriented insights

---

# ⚙️ Part 2: Production-Style Pipeline (Azure)

## 🚀 Motivation

Transform notebook-based workflow into a **scalable and reusable pipeline**

---

## 🏗️ Architecture

```id="7a3vkl"
Local Python (PyCharm)
        ↓
Azure Blob Storage
        ↓
Feature Engineering
        ↓
Model Training
        ↓
Prediction Output
```

---

## 🧱 Project Structure

```id="4n0m2p"
project/
│
├── src/
│   ├── data_ingestion.py
│   ├── feature_engineering.py
│   ├── model.py
│   └── config.py
│
├── main.py
├── .env
└── README.md
```

---

## 🔄 Pipeline Steps

### 1. Data Ingestion

* Load raw data from Azure Blob

### 2. Feature Engineering

* Example (bureau):

```python id="oj9k6g"
bureau.groupby("SK_ID_CURR").agg({
    "SK_ID_BUREAU": "count",
    "AMT_CREDIT_SUM": "mean",
    "AMT_CREDIT_SUM_OVERDUE": "sum"
})
```

---

### 3. Model Training

* Merge features with main dataset
* Train XGBoost model

---

### 4. Prediction & Output

* Generate risk scores
* Save & upload to Azure Blob

---

## 🔐 Environment Setup

```id="j1k7xn"
AZURE_STORAGE_ACCOUNT=your_account
AZURE_STORAGE_KEY=your_key
```

---

## ▶️ Run

```bash id="1ybhsl"
python main.py
```

---

# 💡 Key Highlights

* Combined **Kaggle modeling + real-world pipeline design**
* Integrated **Azure cloud storage**
* Built **modular and reusable code structure**
* Demonstrated both **analysis and engineering skills**

---

# 🎯 Future Improvements

* Multi-table feature pipeline
* Model deployment (API)
* Automated pipeline scheduling

---

# 👨‍💻 Author

Clyde Wang

This project demonstrates my transition from:
- Notebook-based experimentation (Kaggle)
- To production-style machine learning pipeline with Azure

Focus areas:
- Credit risk modeling
- Feature engineering on relational datasets
- Cloud-based data pipeline design

---

