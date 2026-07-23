# Analyst Q&A Response

## Question

Why is this applicant high risk?

## Short Answer

This applicant is high risk because the risk score `0.714646` is above the threshold `0.150000` and the applicant is in `Band 5 - Highest Risk`. The strongest positive SHAP risk drivers are EXT_SOURCE_3, EXT_SOURCE_2, n_active_bureau_credits.

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

- Source `API_USAGE.md`: - `risk_score` is the model-predicted default risk score for the submitted applicant. - `risk_band` translates the numeric score into a business-facing portfolio risk segment. - `high_risk_flag_015` indicates whether the applicant is above the candidate high-risk threshold of 0.15. - `threshold_used` records the decision threshold used in this API version for traceability. - `missing_feature_count` and `unexpected_feature_count` help validate API input quality before using the prediction for analysis or review. - `human_review_recommendation` summarizes whether the case should be reviewed by an analyst under the current rule set. - `audit_log_id` links the response to the JSONL audit log...
- Source `API_USAGE.md`: ```json { "human_review_recommendation": { "review_required": true, "review_priority": "high", "review_reasons": [ "Risk score is above the candidate high-risk threshold.", "Strong positive SHAP risk drivers are present." ] }, "audit_log_id": "b9c4f3f4-7c7e-4f5e-8c4d-55d6df4d3b4b", "human_review_case": { "review_case_id": "7d54ad71-1c47-4b38-8e40-8ef46602d310", "status": "pending_review", "review_priority": "high" } } ```
- Source `API_USAGE.md`: ```json { "risk_score": 0.7146458029747009, "risk_band": "Band 5 - Highest Risk", "high_risk_flag_015": 1, "threshold_used": 0.15, "model_version": "xgboost_v1", "missing_feature_count": 0, "missing_features_preview": [], "unexpected_feature_count": 0, "unexpected_features_preview": [] } ``` The response fields can be interpreted as follows:
- Source `docs\DATA_MODEL_AND_LINEAGE.md`: | Source / Layer | Input fields or data | Transformation | Output artifact | Business purpose | | --- | --- | --- | --- | --- | | `application_train.csv` | Applicant profile, loan request, income, employment, demographic fields, `TARGET` | Add application-level affordability and exposure ratios | Model-ready application feature columns | Represent current borrower affordability, repayment burden, and exposure | | `bureau.csv` | `SK_ID_CURR`, bureau credit records, credit status, debt, overdue fields | Aggregate many bureau records to one applicant row | `outputs/bureau_features.csv` | Summarize external credit history and external debt burden | | `previous_application.csv` | Previous appl...
- Source `docs\DATA_DICTIONARY.md`: | Field | Layer | Definition | Business Interpretation | |---|---|---|---| | `AMT_INCOME_TOTAL` | Source application | Applicant reported total income. | Indicates borrower income capacity. | | `AMT_CREDIT` | Source application | Requested credit amount. | Captures loan exposure requested by the applicant. | | `AMT_ANNUITY` | Source application | Scheduled annuity or repayment amount. | Indicates expected repayment burden. | | `AMT_GOODS_PRICE` | Source application | Price of the goods associated with the loan. | Helps compare loan amount against financed asset or purchase value. | | `DAYS_BIRTH` | Source application | Applicant age represented as relative days in the original dataset. |...
- Source `docs\DATA_DICTIONARY.md`: | Field | Layer | Definition | Business Interpretation | |---|---|---|---| | `top_positive_risk_drivers` | API explanation output | Highest positive local SHAP contributors for an applicant. | Features increasing the model output toward higher predicted default risk. | | `top_negative_risk_drivers` | API explanation output | Most negative local SHAP contributors for an applicant. | Features decreasing the model output toward lower predicted default risk. | | `feature` | Explanation detail | Feature name associated with a local SHAP contribution. | Identifies the model input driving the explanation. | | `feature_value` | Explanation detail | Applicant-specific value for the explained featu...

## Analyst Interpretation

This answer is generated from the local API scoring response, local JSONL review context when provided, and retrieved project documentation. It is analyst decision support, not automated approval or rejection. The analyst should review the strongest positive SHAP drivers, threshold position, and any human review triggers.
