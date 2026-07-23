# API Requirements Specification

## 1. Purpose

This document defines the functional and non-functional requirements for the FastAPI scoring service in the Home Credit risk analytics project.

The API exposes a trained XGBoost credit risk model as a local scoring endpoint. It supports model scoring, local explainability, audit traceability, and rule-based human review recommendation for an analytical prototype.

## 2. Business Context

Credit analysts, risk managers, model governance reviewers, and downstream data consumers need a consistent way to submit applicant-level model-ready features and receive credit risk scoring outputs.

The service is intended to return:

- Predicted risk score.
- Risk band.
- High-risk flag.
- Local risk drivers.
- Input quality checks.
- Human review recommendation.
- Audit log reference.

This API is designed for portfolio demonstration and local analytical workflow support. It is not presented as a production credit decision system.

## 3. Primary Users and Stakeholders

| User / Stakeholder | API Expectation |
|---|---|
| Credit analyst | Receives an applicant risk score, risk band, high-risk flag, and local risk drivers to support credit review. |
| Risk manager | Uses consistent scoring outputs to understand high-risk segmentation and portfolio-level risk patterns. |
| Model governance reviewer | Reviews model version, threshold, explanation fields, audit identifiers, and traceability outputs. |
| Data analyst / data technology team | Validates feature alignment, input quality, scoring output structure, and downstream data usability. |
| API consumer / downstream application | Sends model-ready feature payloads and receives structured scoring, explanation, and governance responses. |

## 4. Endpoint Scope

### GET /health

Purpose: Check whether the API service and saved model artifacts are available.

Expected response fields:

- `status`
- `model_loaded`
- `feature_count`
- `threshold`
- `model_version`

### POST /predict

Purpose: Submit model-ready applicant features and receive model scoring output.

Expected response fields:

- `risk_score`
- `risk_band`
- `high_risk_flag_015`
- `threshold_used`
- `model_version`
- `missing_feature_count`
- `missing_features_preview`
- `unexpected_feature_count`
- `unexpected_features_preview`

### POST /predict-with-explanation

Purpose: Submit model-ready applicant features and receive scoring output plus local SHAP explanation, human review recommendation, and audit log id.

Expected response fields:

- All fields from `/predict`.
- `top_positive_risk_drivers`
- `top_negative_risk_drivers`
- `explanation_note`
- `human_review_recommendation`
- `audit_log_id`

## 5. Input Payload Requirements

The current API endpoints expect model-ready engineered features.

Expected request body:

```json
{
  "features": {
    "AMT_CREDIT": 545040.0,
    "AMT_ANNUITY": 25407.0
  },
  "strict": false
}
```

`features` contains applicant-level model input fields. `strict` controls whether missing expected features should fail the request.

In flexible testing mode, missing features can be filled consistently and reported. In strict mode, missing required features should be treated as request quality issues.

Current limitation: the API does not yet transform raw `application_train`, `bureau`, or `previous_application` records into engineered features.

## 6. Output Payload Requirements

| Output Field | Endpoint | Description | Business Purpose |
|---|---|---|---|
| `risk_score` | `/predict`, `/predict-with-explanation` | Model-predicted probability-like default risk score. | Provides applicant-level predicted risk. |
| `risk_band` | `/predict`, `/predict-with-explanation` | Business-facing risk segment derived from the score. | Supports portfolio segmentation and analyst review. |
| `high_risk_flag_015` | `/predict`, `/predict-with-explanation` | Binary flag based on whether `risk_score >= 0.15`. | Identifies applicants above the candidate high-risk threshold. |
| `threshold_used` | `/predict`, `/predict-with-explanation` | Threshold used for high-risk flagging. | Makes threshold-based logic explicit and traceable. |
| `model_version` | `/health`, `/predict`, `/predict-with-explanation` | Saved model version identifier. | Supports model governance and reproducibility. |
| `missing_feature_count` | `/predict`, `/predict-with-explanation` | Count of expected model features missing from the request. | Measures request completeness. |
| `unexpected_feature_count` | `/predict`, `/predict-with-explanation` | Count of submitted fields not used by the model. | Identifies extra or incorrectly mapped fields. |
| `top_positive_risk_drivers` | `/predict-with-explanation` | Top local SHAP features increasing predicted default risk. | Helps analysts understand key risk-increasing signals. |
| `top_negative_risk_drivers` | `/predict-with-explanation` | Top local SHAP features reducing predicted default risk. | Helps analysts understand key risk-reducing signals. |
| `human_review_recommendation` | `/predict-with-explanation` | Rule-based review recommendation object. | Supports analyst triage and decision support. |
| `audit_log_id` | `/predict-with-explanation` | Identifier linking the response to a persisted JSONL audit record. | Enables traceability of scoring events. |

## 7. Validation and Error Handling Requirements

- Missing model features should be detected and reported.
- Unexpected fields should be detected and reported.
- Numeric conversion should be applied before scoring where appropriate.
- Feature alignment should follow the saved `feature_list.json`.
- If model artifacts are unavailable, the API should return a clear service or model availability error.
- If prediction fails, the API should return a clear error message rather than an ambiguous result.

The current implementation focuses on local prototype validation and does not claim production-grade error handling.

## 8. Human Review Recommendation Requirements

The API provides rule-based decision support through a `human_review_recommendation` object.

The recommendation should include:

- `review_required`
- `review_priority`
- `review_reasons`

Example review triggers include:

- Risk score above the candidate high-risk threshold.
- Score close to the decision threshold.
- Strong positive SHAP risk drivers.
- Both risk-increasing and risk-reducing SHAP signals are material.
- Missing or unexpected feature issues.

This is not automated approval or rejection. It supports analyst judgment.

## 9. Audit Logging Requirements

Each `/predict-with-explanation` request should write an audit-friendly JSONL log entry.

The log should include:

- `audit_log_id`
- Endpoint name.
- Timestamp.
- `model_version`.
- `risk_score`.
- `risk_band`.
- `threshold_used`.
- Top SHAP drivers.
- `human_review_recommendation`.

Runtime logs are stored under:

```text
outputs/api_logs/
```

JSONL logs are ignored by Git because they change with each API test run.

## 10. User Stories

- As a credit analyst, I want to receive a risk score for an applicant, so that I can prioritize credit review work.
- As a credit analyst, I want to see local risk drivers, so that I can understand why an applicant was scored as higher or lower risk.
- As a risk manager, I want to monitor high-risk segmentation, so that I can assess portfolio risk distribution.
- As a governance reviewer, I want to trace model version and audit log id, so that scoring events can be reviewed later.
- As an API consumer, I want missing and unexpected input fields to be reported, so that I can validate request quality before relying on the score.

## 11. Acceptance Criteria

- The health endpoint returns service readiness and model artifact status.
- The predict endpoint returns a numeric `risk_score` between `0` and `1`.
- The API assigns each applicant to a `risk_band`.
- The API returns `high_risk_flag_015` based on `threshold_used`.
- The explanation endpoint returns top positive and negative SHAP drivers.
- The API reports missing and unexpected feature counts.
- The API returns a `human_review_recommendation` object.
- The API returns an `audit_log_id` for explanation-enabled scoring.
- Runtime audit logs are written as JSONL records.

## 12. Non-Functional Requirements

- Explainability: local SHAP drivers should be returned for analyst interpretation.
- Traceability: `model_version`, `threshold_used`, and `audit_log_id` should be included.
- Reproducibility: saved model and feature artifacts should be reused.
- Input reliability: feature alignment and input quality checks should be performed.
- Maintainability: API usage should be documented in `API_USAGE.md`.
- Security: no production authentication or authorization is implemented in the current prototype.

## 13. Current Limitations

- The API runs as a local prototype.
- It expects model-ready engineered features.
- It does not yet include a full human review queue workflow.
- It does not use a production database, cloud data warehouse, or authentication layer.
- It is not a production credit decision system.

## 14. Future Enhancements

- Add raw-to-feature API transformation support.
- Add a lightweight human review workflow with review queue and case status updates.
- Add automated data quality reports.
- Add warehouse-ready scoring and audit tables.
- Add a RAG or agent-based analyst explanation layer using project documentation and model outputs.
- Add authentication, authorization, and deployment controls if moving toward production.
