# Analyst Q&A Response

## Question

What does EXT_SOURCE_3 mean?

## Short Answer

`EXT_SOURCE_3` appears in this applicant's local SHAP drivers with value `0.074461` and SHAP `0.891663`. External score signal from the original dataset. Higher values generally reduce modeled default risk, but the internal score composition is not disclosed.

## Evidence from Scoring Response

- `risk_score`: `0.714646`
- `risk_band`: `Band 5 - Highest Risk`
- `high_risk_flag_015`: `1`
- `threshold_used`: `0.150000`
- `model_version`: `xgboost_v1`
- `audit_log_id`: `3d09a3f6-6132-4674-abd4-a4a348bda0c1`
- `missing_feature_count`: `0`
- `unexpected_feature_count`: `0`
- `review_required`: `True`
- `review_priority`: `high`

Top positive risk drivers:

- `EXT_SOURCE_3`: value `0.074461`, SHAP `0.891663`, value_status `actual_value`.
- `EXT_SOURCE_2`: value `0.088762`, SHAP `0.768572`, value_status `actual_value`.
- `n_active_bureau_credits`: value `10`, SHAP `0.467122`, value_status `actual_value`.
- `prev_refusal_rate`: value `0.666667`, SHAP `0.329135`, value_status `actual_value`.
- `credit_goods_ratio`: value `1.211200`, SHAP `0.151697`, value_status `actual_value`.

## Human Review Context

No review case id was provided, so local review workflow context was not loaded.

## Retrieved Project Context

- Source `API_USAGE.md`: ```json { "human_review_recommendation": { "review_required": true, "review_priority": "high", "review_reasons": [ "Risk score is above the candidate high-risk threshold.", "Strong positive SHAP risk drivers are present." ] }, "audit_log_id": "b9c4f3f4-7c7e-4f5e-8c4d-55d6df4d3b4b", "human_review_case": { "review_case_id": "7d54ad71-1c47-4b38-8e40-8ef46602d310", "status": "pending_review", "review_priority": "high" } } ```
- Source `API_USAGE.md`: - `risk_score` is the model-predicted default risk score for the submitted applicant. - `risk_band` translates the numeric score into a business-facing portfolio risk segment. - `high_risk_flag_015` indicates whether the applicant is above the candidate high-risk threshold of 0.15. - `threshold_used` records the decision threshold used in this API version for traceability. - `missing_feature_count` and `unexpected_feature_count` help validate API input quality before using the prediction for analysis or review. - `human_review_recommendation` summarizes whether the case should be reviewed by an analyst under the current rule set. - `audit_log_id` links the response to the JSONL audit log...
- Source `API_USAGE.md`: ```json { "risk_score": 0.7146458029747009, "risk_band": "Band 5 - Highest Risk", "high_risk_flag_015": 1, "threshold_used": 0.15, "model_version": "xgboost_v1", "missing_feature_count": 0, "missing_features_preview": [], "unexpected_feature_count": 0, "unexpected_features_preview": [] } ``` The response fields can be interpreted as follows:
- Source `docs\DATA_DICTIONARY.md`: | Field | Layer | Definition | Business Interpretation | |---|---|---|---| | `human_review_recommendation` | API governance output | Rule-based review recommendation object returned by `/predict-with-explanation`. | Provides decision support for analyst review, not automated approval or rejection. | | `review_required` | API governance output | Boolean flag indicating whether the current rule set recommends review. | Helps identify cases needing additional analyst attention. | | `review_priority` | API governance output | Priority label such as `high`, `medium`, or `low`. | Supports triage of review cases. | | `review_reasons` | API governance output | List of rule-based reasons for the r...
- Source `docs\DATA_MODEL_AND_LINEAGE.md`: | Source / Layer | Input fields or data | Transformation | Output artifact | Business purpose | | --- | --- | --- | --- | --- | | `application_train.csv` | Applicant profile, loan request, income, employment, demographic fields, `TARGET` | Add application-level affordability and exposure ratios | Model-ready application feature columns | Represent current borrower affordability, repayment burden, and exposure | | `bureau.csv` | `SK_ID_CURR`, bureau credit records, credit status, debt, overdue fields | Aggregate many bureau records to one applicant row | `outputs/bureau_features.csv` | Summarize external credit history and external debt burden | | `previous_application.csv` | Previous appl...
- Source `docs\DATA_QUALITY_AND_GOVERNANCE.md`: - Which features contributed to the score? - Which raw data sources produced those features? - Were there any missing, sentinel, or special encoded values? - Which model version and threshold were used? - What were the top SHAP risk drivers? - Was the scoring event recorded with an audit log id? - Was the case recommended for human review?

## Analyst Interpretation

External score signal from the original dataset. Higher values generally reduce modeled default risk, but the internal score composition is not disclosed. Interpret this feature together with the applicant's local SHAP value and the retrieved documentation context.
