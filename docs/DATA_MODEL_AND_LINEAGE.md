# Data Model and Lineage

## 1. Purpose

This document describes how raw credit application, bureau, and previous-application data are transformed into model-ready features, scoring outputs, explainability outputs, and API governance records.

The project is designed as an end-to-end credit risk data technology system covering:

- data ingestion
- feature engineering
- model-ready data design
- scoring output
- explainability
- audit traceability
- human review support

The goal is to make the project understandable not only as a machine learning model, but also as a data model and lineage flow suitable for Data Technology, Data Modelling, Data Quality, and Risk Analytics roles.

## 2. Source Data Layer

### application_train.csv

Business meaning:
Application-level applicant profile, loan request, income, employment, demographic, and target default outcome data.

Main role in the project:
Provides the base applicant population, `TARGET` label, and application-level features.

### bureau.csv

Business meaning:
External bureau credit history associated with applicants.

Main role in the project:
Provides aggregated external credit exposure, active credit count, overdue amount, and credit burden indicators.

### previous_application.csv

Business meaning:
Historical previous credit applications made by the same applicants.

Main role in the project:
Provides historical approval/refusal patterns, previous credit amount, down payment behavior, and repayment structure indicators.

## 3. Conceptual Data Model

The project is organized around the following conceptual business entities:

- Applicant
- Current loan application
- Bureau credit record
- Previous credit application
- Model score
- Risk band
- SHAP explanation
- API scoring request
- Audit log entry
- Human review recommendation

High-level relationships:

- One applicant has one current application in the model base table.
- One applicant may have many bureau credit records.
- One applicant may have many previous applications.
- Feature engineering aggregates many-to-one historical records into one applicant-level model input row.
- Each API scoring request produces one scoring response and one audit log entry.
- A scoring response may trigger a human review recommendation.

## 4. Logical Data Model

The logical data model is organized into seven layers:

1. Raw source tables
2. Applicant-level feature tables
3. Model-ready feature matrix
4. Model scoring outputs
5. Explainability outputs
6. API response outputs
7. Audit and governance outputs

Simple lineage flow:

```text
Raw source tables
-> Feature engineering layer
-> Model-ready applicant feature matrix
-> XGBoost scoring model
-> Risk score and risk band
-> SHAP explanation
-> FastAPI response
-> Audit log and human review recommendation
```

## 5. Physical Data Artifacts

### Raw Data

- `data/raw/application_train.csv`
- `data/raw/bureau.csv`
- `data/raw/previous_application.csv`

### Model Artifacts

- `outputs/models/model.pkl`
- `outputs/models/feature_list.json`

### Scoring Outputs

- `outputs/risk_scores.csv`
- `outputs/reports/validation_results.csv`

### SQL Analytics Outputs

- `outputs/sql_reports/risk_analytics_base.csv`
- `outputs/sql_reports/01_risk_band_portfolio_summary.csv`
- `outputs/sql_reports/02_income_type_risk_summary.csv`
- `outputs/sql_reports/03_high_risk_flag_summary.csv`

### Explainability Outputs

- `outputs/reports/shap_global_importance.csv`
- `outputs/plots/shap_summary_bar.png`
- `outputs/plots/shap_summary_beeswarm.png`
- `outputs/reports/local_shap_examples.csv`
- `outputs/reports/local_shap_examples.md`
- SHAP dependence plots for selected features under `outputs/plots/`

### API Sample Outputs

- `outputs/api_samples/sample_predict_payload.json`
- `outputs/api_samples/sample_predict_payload_metadata.json`
- `outputs/api_samples/sample_predict_with_explanation_response.json`
- `outputs/api_samples/sample_predict_with_governance_response.json`, if present

### Governance Outputs

- `outputs/api_logs/scoring_audit_log.jsonl`

JSONL audit logs are runtime artifacts and are ignored by Git.

## 6. Source-to-Target Mapping Summary

| Source / Layer | Input fields or data | Transformation | Output artifact | Business purpose |
| --- | --- | --- | --- | --- |
| `application_train.csv` | Applicant profile, loan request, income, employment, demographic fields, `TARGET` | Add application-level affordability and exposure ratios | Model-ready application feature columns | Represent current borrower affordability, repayment burden, and exposure |
| `bureau.csv` | `SK_ID_CURR`, bureau credit records, credit status, debt, overdue fields | Aggregate many bureau records to one applicant row | `outputs/bureau_features.csv` | Summarize external credit history and external debt burden |
| `previous_application.csv` | Previous application status, annuity, credit amount, down payment, decision timing | Aggregate many previous applications to one applicant row | `outputs/previous_application_features.csv` | Summarize historical application behavior and prior credit outcomes |
| Engineered features | Application ratios, bureau aggregates, previous-application aggregates | Select numeric/boolean model inputs and persist feature order | `outputs/models/feature_list.json` | Keep training and scoring schema consistent |
| Model-ready matrix | Prepared applicant feature matrix `X` | XGBoost probability scoring | `outputs/risk_scores.csv` | Produce applicant-level default risk scores |
| Risk score | `risk_score` | Quantile-based banding and threshold flagging | `risk_band`, `high_risk_flag_015` | Translate numeric model output into business-facing risk segments |
| Model input and SHAP values | Applicant feature row and local SHAP values | Rank positive and negative local SHAP contributors | API explanation response and local SHAP reports | Explain applicant-level risk drivers |
| API response | Score, band, input quality checks, SHAP drivers | Apply review rules and append JSONL event | `outputs/api_logs/scoring_audit_log.jsonl` | Provide audit traceability and human review support |

## 7. Data Integrity and Reconciliation Controls

The project includes several controls that support data quality, model traceability, and reproducibility:

- One-row-per-applicant validation before merging historical feature tables.
- Feature list persistence to keep training and API scoring input order consistent.
- Missing feature detection in API requests.
- Unexpected feature detection in API requests.
- Sentinel value handling for missing or special encoded values.
- Validation results used to separate model evaluation from in-sample scoring.
- Audit log id links API response to persisted scoring event.
- Model version and threshold are included in API response for traceability.

## 8. Business Use

This data model supports several business and analytics users:

- Credit analysts can receive model scores and local risk drivers.
- Risk managers can monitor portfolio segmentation and high-risk groups.
- Model governance reviewers can trace model version, input quality, threshold, and review recommendation.
- Data teams can understand how raw records become model-ready features and scoring outputs.

## 9. Current Limitations

- The current FastAPI scoring endpoint expects model-ready engineered features.
- Raw application, bureau, and previous_application records are not yet transformed through an API endpoint.
- The current runnable version uses local files and local model artifacts.
- Earlier Azure cloud storage support can be re-enabled through configuration, but the project is not currently implemented on a production database or cloud data warehouse such as BigQuery.
- GCP, BigQuery, and Looker are not implemented in the current version.
- The current data model is designed as a local analytical prototype, but the data flow can be migrated to a warehouse-backed architecture in the future.

## 10. Future Enhancements

Potential future enhancements include:

- Add raw-to-feature API transformation support.
- Add a lightweight human review workflow.
- Expand data dictionary coverage for core engineered features and API output fields.
- Add automated data quality summary reports.
- Restore or extend cloud storage integration where needed.
- Design warehouse-ready analytical tables for future cloud data warehouse migration.
- Add a RAG / Agent analyst explanation layer based on model outputs and project documentation.