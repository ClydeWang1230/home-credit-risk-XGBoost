# Data Quality and Governance

## 1. Purpose

This document describes how the Home Credit risk analytics project manages data quality, model input consistency, API scoring reliability, explainability, audit logging, and governance traceability.

The project is designed as a local analytical prototype that demonstrates practical data governance thinking across the credit risk workflow, from raw data preparation through model scoring and API-based decision support.

## Quality and Governance Logic

The core governance logic of this project is to make the credit risk scoring process reliable, explainable, and traceable across the full data flow.

Raw application, bureau, and previous-application data are transformed into model-ready features, passed into the XGBoost scoring model, converted into risk scores and risk bands, explained through SHAP, exposed through FastAPI, and recorded through audit logs and human review recommendations.

This means that when an applicant receives a high risk score, the project can support follow-up questions such as:

- Which features contributed to the score?
- Which raw data sources produced those features?
- Were there any missing, sentinel, or special encoded values?
- Which model version and threshold were used?
- What were the top SHAP risk drivers?
- Was the scoring event recorded with an audit log id?
- Was the case recommended for human review?

This is the practical purpose of the project’s data quality, traceability, and governance design.

## 2. Data Quality Scope

This project focuses on data quality issues that can affect model-ready feature generation, scoring consistency, API input reliability, and audit traceability.

The data quality scope includes:

- Missing values in raw and engineered features.
- Anomalous values and outliers.
- Dataset-specific sentinel or special encoded values, such as `-999`, `-1000`, and `DAYS_EMPLOYED = 365243`.
- Applicant-level consistency after aggregating bureau and previous-application records.
- Numeric feature type consistency before model training and API scoring.
- Feature completeness and ordering consistency between training and inference.
- API input reliability.
- Traceability between model inputs, model outputs, SHAP explanations, and audit logs.

## 3. Data Quality Controls

- Missing values are handled consistently where appropriate, including sentinel-based treatment for model-ready inputs.
- Sentinel and special encoded values are documented instead of being blindly interpreted as literal business values.
- Anomalous values and outliers are reviewed before deciding whether to keep, cap, or document them.
- Applicant-level merge validation helps maintain one row per applicant after joining historical feature tables.
- Numeric conversion is applied before scoring to reduce input type issues.
- Validation outputs are separated from full in-sample scoring outputs to support clearer model evaluation.

## 4. Feature Engineering Integrity Controls

- Application-level features capture applicant profile, requested loan amount, income, employment context, and affordability ratios.
- Bureau aggregation converts multiple external bureau records into applicant-level credit history indicators.
- Previous-application aggregation converts historical application records into applicant-level approval, refusal, amount, timing, and repayment behavior features.
- Many-to-one aggregation is used to keep the final model input at the applicant level.
- Feature tables are validated for duplicate `SK_ID_CURR` values before merge-sensitive reporting.
- These controls reduce inconsistent joins and help maintain a stable model-ready feature table.

## 5. Model Input Consistency Controls

The project maintains consistency between model training, validation, and API scoring through saved model and feature artifacts.

- `model.pkl` stores the trained XGBoost model artifact used by the FastAPI scoring service.
- `feature_list.json` stores the exact model input feature order used during training.
- API scoring inputs are aligned against `feature_list.json` before prediction.
- Missing model features are filled consistently where appropriate and reported in the API response.
- Validation results are separated from in-sample scoring to avoid mixing model evaluation with training outputs.
- `model_version` and `threshold_used` are returned in API responses to support traceability.

## 6. API Input Validation Controls

The FastAPI layer includes input validation checks to reduce scoring inconsistency during inference.

- `missing_feature_count` reports how many expected model features are not provided in the request.
- `missing_features_preview` shows examples of missing fields.
- `unexpected_feature_count` reports fields provided by the request but not used by the model.
- `unexpected_features_preview` shows examples of unexpected input fields.
- Numeric conversion is applied before scoring to reduce input type issues.
- `strict` mode can be used to enforce complete feature input requirements when needed.
- Feature alignment against the saved feature list keeps inference inputs consistent with training inputs.

## 7. Explainability and Governance Controls

The project uses SHAP and rule-based review logic to improve model transparency and analyst support.

- Global SHAP summaries show which features have the largest overall impact on model predictions.
- SHAP dependence plots show how selected features affect predicted risk across value ranges.
- Local applicant-level SHAP explanations identify top positive and negative risk drivers.
- Local explanation reports include value status for sentinel missing values and special encoded values.
- `human_review_recommendation` flags high-risk, borderline, or data-quality-sensitive cases for analyst review.
- The human review recommendation is rule-based decision support and does not replace analyst judgment.
- The API does not make automated approval or rejection decisions.

## 8. Audit Logging and Traceability

The API writes audit-friendly scoring logs to support traceability of model outputs.

- Each `/predict-with-explanation` response includes an `audit_log_id`.
- The `audit_log_id` links the API response to a persisted JSONL audit log entry.
- Each audit log entry records the endpoint name, timestamp, model version, risk score, risk band, top SHAP drivers, and human review recommendation.
- Runtime audit logs are stored under `outputs/api_logs/`.
- JSONL is used because each scoring event can be appended as one independent log record.
- Runtime JSONL logs are ignored by Git because they change with each API test.

## 9. Current Limitations

- The current version is a local analytical prototype.
- The API expects model-ready engineered features.
- Raw application, bureau, and previous-application records are not yet transformed through an API endpoint.
- Runtime audit logs are local JSONL files, not a production database or compliance system.
- The human review recommendation is rule-based and is not a full review queue workflow yet.
- The project demonstrates governance concepts but does not claim production-grade compliance readiness.

## 10. Future Enhancements

- Add automated data quality summary reports.
- Expand the data dictionary for core engineered features and API output fields.
- Add a lightweight human review workflow, such as review queue, case status tracking, analyst comments, and decision updates.
- Add warehouse-ready table design for future cloud data warehouse migration.
- Add a RAG or agent-based analyst explanation layer using model outputs and project documentation.
