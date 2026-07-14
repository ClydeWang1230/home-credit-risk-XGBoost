# Credit Risk Analytics Pipeline with XGBoost

## Project Structure

```text
home-credit-risk-XGBoost/
  data/
    raw/                         # Local raw CSV files, not uploaded to GitHub
  notebooks/                     # Exploratory notebook reference work
  outputs/
    metrics/
      metrics.json
    models/
      model.pkl                  # Local model artifact, not uploaded to GitHub
      feature_list.json
    reports/
      feature_importance.csv
    bureau_features.csv
    previous_application_features.csv
    risk_scores.csv
  sql_queries/                   # SQL reference queries and feature logic notes
  src/
    config.py
    data_ingestion.py
    feature_engineering.py
    model.py
  main.py
  requirements.txt
  env.example
  README.md
```

## Data

This project uses the Home Credit Default Risk dataset.

Required local files:

```text
data/raw/application_train.csv
data/raw/bureau.csv
data/raw/previous_application.csv
```

Raw CSV files, generated CSV outputs, and model pickle artifacts are excluded from GitHub through `.gitignore` because of size, licensing, and reproducibility considerations.

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Place the required raw CSV files under:

```text
data/raw/
```

Run the pipeline:
From the project root directory, run:

```bash
python main.py
```

The default data source is local:

```python
DATA_SOURCE = os.getenv("DATA_SOURCE", "local").lower()
```

Optional Azure mode can be enabled by setting:

```bash
DATA_SOURCE=azure
```

Azure credentials should be configured from `env.example` if Azure Blob Storage is used.

## Pipeline Outputs

After a successful run, the pipeline generates:

```text
outputs/metrics/metrics.json
outputs/models/model.pkl
outputs/models/feature_list.json
outputs/risk_scores.csv
outputs/reports/feature_importance.csv
```

The metrics file records validation AUC, data source, input shapes, feature table shapes, duplicate-key checks, and merge row-count validation.

## Feature Engineering

The feature engineering layer converts one-to-many historical credit tables into one-row-per-applicant features that can be safely merged into `application_train`.

### Previous Application Features

These features summarize a borrower's prior application behavior:

- `n_prev_applications`: total number of previous applications
- `n_prev_approved`: number of previously approved applications
- `n_prev_refusals`: number of previously refused applications
- `prev_approval_rate`: share of previous applications approved
- `prev_refusal_rate`: share of previous applications refused
- `avg_annuity_prev`: average prior annuity amount
- `avg_credit_prev`: average prior credit amount
- `max_credit_prev`: maximum prior credit amount
- `avg_down_payment_prev`: average prior down payment
- `days_decision_mean`: average timing of previous application decisions
- `last_application_days`: most recent previous application timing

Business interpretation: previous refusals, approval rates, prior credit amounts, and recent credit-seeking behavior help describe historical borrower risk beyond the current application.

### Application Affordability Features

These features are derived directly from `application_train`:

- `credit_income_ratio`: credit amount relative to borrower income
- `annuity_income_ratio`: scheduled repayment amount relative to income
- `credit_annuity_ratio`: credit amount relative to scheduled repayment
- `credit_goods_ratio`: credit amount relative to goods price
- `income_per_family_member`: income adjusted by family size

Business interpretation: these ratios make the model more explainable by connecting credit exposure, repayment pressure, financing coverage, and household capacity.

### Bureau Features

The current bureau feature table includes:

- `bureau_record_count`
- `avg_credit_sum`
- `total_overdue_amount`
- `avg_days_credit_update`

Business interpretation: bureau records provide external credit history signals, including exposure, overdue balances, and credit record update timing.

## Model Performance

Validation metric: ROC AUC.

| Stage | Feature Update | Validation AUC |
| --- | --- | ---: |
| Initial local baseline | Local pipeline with initial bureau and previous-application features | 0.7553 |
| Batch 2A | Added previous-application amount features | 0.7576 |
| Batch 2B | Added previous-application time features | 0.7577 |
| Batch 3A | Added application affordability and exposure ratio features | 0.7645 |

The strongest Week 1 improvement came from adding application-level affordability and exposure ratios.

## Explainability

The pipeline generates:

```text
outputs/reports/feature_importance.csv
```

The report includes:

- `feature`
- `importance`
- `importance_rank`
- `business_category`
- `business_interpretation`

Current feature importance observations:

- `EXT_SOURCE_3` and `EXT_SOURCE_2` remain top-ranked external credit score features.
- `prev_refusal_rate` ranks highly, showing that historical refusal behavior is a strong predictive signal.
- `credit_goods_ratio` ranks highly, suggesting financing coverage is meaningful for risk prediction.
- `avg_down_payment_prev` and `credit_annuity_ratio` also appear relatively high in the feature importance report.

This report is intended to make model results more interview-ready and easier to discuss with business stakeholders.

## Validation Checks

The pipeline records and prints checks such as:

- Previous-application feature duplicate `SK_ID_CURR` count
- Application row count before and after historical feature merges
- Input data shapes
- Feature table shapes

Current merge validation confirms:

- `previous_application_features` has one row per `SK_ID_CURR`
- Duplicate `SK_ID_CURR` count is `0`
- `application_train` row count is preserved at `307511` after merge

## Roadmap

Near-term next steps:

- Add more bureau history features with clear business interpretation
- Add evaluation reporting beyond AUC
- Add risk score bands and portfolio-level risk summaries
- Improve README and project documentation as the structure stabilizes
- Add model comparison experiments only after the feature layer is stable

Future ideas, not yet completed:

- SHAP explainability
- FastAPI scoring endpoint
- AI-assisted analyst workflow
- RAG-based credit knowledge retrieval and SQL analytics assistant

## Portfolio Narrative

I expanded an original Kaggle-style credit risk notebook into a modular, reproducible analytics pipeline. The project now converts historical one-to-many credit tables into applicant-level risk features, validates merge safety, trains an XGBoost model, saves model artifacts, and produces a business-readable feature importance report.

This project demonstrates practical skills in credit risk modeling, feature engineering, model evaluation, reproducible pipelines, and business interpretation for fintech and banking analytics roles.


## Overview

This project is a reproducible, business-oriented credit risk analytics pipeline built from the Home Credit Default Risk dataset. It started as a Kaggle-style notebook project and is being migrated into a modular portfolio project for fintech, banking analytics, credit risk analytics, data analyst, and risk analyst roles.

The goal is not only to improve Kaggle AUC. The focus is to build a clear pipeline that connects credit risk feature engineering, model training, validation, feature importance, and business interpretation.

## Business Problem

Credit risk teams need to estimate the likelihood that an applicant may default while keeping decisions explainable to analysts, lenders, and business stakeholders. This project turns raw application, bureau, and previous-loan history into interpretable borrower-level risk signals and model outputs that support portfolio review and credit decision analysis.

## Week 1 Status

The Week 1 pipeline runs end-to-end in local mode from raw CSV files under `data/raw/`. Azure Blob Storage integration is still available as an optional data source, but local execution is the default.

By the end of Week 1, the pipeline:
- Loads `application_train.csv`, `bureau.csv`, and `previous_application.csv`
- Builds bureau-level applicant features
- Builds previous-application history features
- Adds application-level affordability and exposure ratio features
- Validates one-row-per-applicant historical feature tables before merging
- Trains an `XGBClassifier`
- Saves model metrics, model artifacts, risk scores, and a feature importance report
- 
## Week 2 Progress: SQL Analytics Layer

The project now includes a DuckDB-based SQL analytics layer for portfolio segmentation.

The SQL layer uses `outputs/sql_reports/risk_analytics_base.csv`, which combines model risk scores with selected applicant profile fields.

Current SQL reports include:
- risk band portfolio summary
- income type by risk band summary
- high-risk flag summary using the candidate 0.15 threshold

This layer demonstrates how model outputs can be translated into business-facing risk analytics and portfolio monitoring reports.

## SHAP Explainability Layer

The project includes a SHAP-based explainability layer to interpret the XGBoost credit risk model at both global and feature-dependence levels.

Generated outputs include:
- `outputs/reports/shap_global_importance.csv`
- `outputs/plots/shap_summary_bar.png`
- `outputs/plots/shap_summary_beeswarm.png`
- SHAP dependence plots for selected engineered credit risk features

Key SHAP findings:
- External source features are the strongest global predictors.
- Engineered features such as `credit_goods_ratio`, `credit_annuity_ratio`, `bureau_debt_credit_ratio`, `prev_refusal_rate`, `prev_approval_rate`, and `avg_down_payment_prev` show meaningful model contributions.
- `prev_refusal_rate` shows a clear positive SHAP relationship with predicted default risk.
- `prev_approval_rate` generally contributes negatively to predicted default risk as historical approval rate increases.
- `bureau_debt_credit_ratio` shows a positive SHAP relationship, supporting its interpretation as an external debt burden signal.
- `avg_down_payment_prev` shows an overall downward SHAP pattern after p99 clipping, suggesting higher historical down payment is associated with lower modeled risk contribution.
- `credit_annuity_ratio` shows a non-linear SHAP pattern, indicating that repayment structure affects model risk estimates differently across ratio ranges.

This layer helps translate model predictions into business-facing explanations and prepares the project for future local applicant-level explanation, FastAPI scoring, and RAG/Agent analyst workflows.