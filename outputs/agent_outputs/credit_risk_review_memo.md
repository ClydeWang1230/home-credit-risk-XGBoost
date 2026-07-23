# Credit Risk Review Memo

## 1. Executive Summary

The applicant received a risk score of `0.714646` and was assigned to `Band 5 - Highest Risk`. The high-risk flag is `1`. The rule-based review recommendation is review_required=`True` with priority `high`.

## 2. Model Scoring Result

- `risk_score`: `0.714646`
- `risk_band`: `Band 5 - Highest Risk`
- `high_risk_flag_015`: `1`
- `threshold_used`: `0.150000`
- `model_version`: `xgboost_v1`

## 3. Key Risk-Increasing Drivers

- `EXT_SOURCE_3`: value `0.074461`, value status `actual_value`, SHAP `0.891663`. External score signal from the original dataset. Higher values generally reduce modeled default risk, but the internal score composition is not disclosed.
- `EXT_SOURCE_2`: value `0.088762`, value status `actual_value`, SHAP `0.768572`. External score signal from the original dataset. Higher values generally reduce modeled default risk, but the internal score composition is not disclosed.
- `n_active_bureau_credits`: value `10`, value status `actual_value`, SHAP `0.467122`. Number of active external bureau credit records, capturing current external credit activity.
- `prev_refusal_rate`: value `0.666667`, value status `actual_value`, SHAP `0.329135`. Share of prior applications that were refused, capturing historical rejection behavior.
- `credit_goods_ratio`: value `1.211200`, value status `actual_value`, SHAP `0.151697`. Credit amount relative to goods price, approximating financing coverage and borrower self-funding context.
- `credit_annuity_ratio`: value `21.452356`, value status `actual_value`, SHAP `0.137280`. Credit amount relative to scheduled repayment amount, approximating repayment structure pressure.
- `credit_income_ratio`: value `17.302857`, value status `actual_value`, SHAP `0.103487`. Credit amount relative to borrower income, capturing loan-to-income pressure.
- `bureau_debt_credit_ratio`: value `0.531379`, value status `actual_value`, SHAP `0.090961`. External bureau debt relative to external credit amount, capturing external debt burden.

## 4. Key Risk-Reducing Drivers

- `DAYS_BIRTH`: value `-21824`, value status `actual_value`, SHAP `-0.174475`. Applicant age represented as relative days in the original dataset.
- `DAYS_ID_PUBLISH`: value `-4819`, value status `actual_value`, SHAP `-0.028615`. This feature is a model input signal. Its local SHAP value indicates how it affected this applicant's predicted risk.
- `max_credit_prev`: value `72387`, value status `actual_value`, SHAP `-0.026693`. Maximum previous credit amount, capturing largest historical credit exposure.
- `FLAG_WORK_PHONE`: value `0`, value status `actual_value`, SHAP `-0.022850`. This feature is a model input signal. Its local SHAP value indicates how it affected this applicant's predicted risk.
- `avg_credit_prev`: value `24129`, value status `actual_value`, SHAP `-0.022489`. Average previous credit amount, summarizing typical prior credit size.
- `avg_credit_sum`: value `125134.007143`, value status `actual_value`, SHAP `-0.011366`. Average external bureau credit amount, summarizing typical external credit exposure.
- `HOUR_APPR_PROCESS_START`: value `7`, value status `actual_value`, SHAP `-0.010841`. This feature is a model input signal. Its local SHAP value indicates how it affected this applicant's predicted risk.
- `REG_CITY_NOT_LIVE_CITY`: value `0`, value status `actual_value`, SHAP `-0.010007`. This feature is a model input signal. Its local SHAP value indicates how it affected this applicant's predicted risk.

## 5. Human Review Recommendation

- `review_required`: `True`
- `review_priority`: `high`

Review reasons:

- Risk score is above the candidate high-risk threshold.
- Strong positive SHAP risk drivers are present.
- Both risk-increasing and risk-reducing SHAP signals are material.

This recommendation is rule-based decision support. It is not automated approval or rejection and should not replace analyst judgment.

## 6. Data Quality and Input Checks

- `missing_feature_count`: `0`
- `missing_features_preview`:
  - None reported.
- `unexpected_feature_count`: `0`
- `unexpected_features_preview`:
  - None reported.

## 7. Governance and Traceability

- `audit_log_id`: `3d09a3f6-6132-4674-abd4-a4a348bda0c1`
- `model_version`: `xgboost_v1`
- `threshold_used`: `0.150000`

The audit log id links this scoring event to traceable model output, local explanation signals, and the rule-based review recommendation.

## 8. Retrieved Project Context

- Source `API_USAGE.md`: ```json { "risk_score": 0.7146458029747009, "risk_band": "Band 5 - Highest Risk", "high_risk_flag_015": 1, "threshold_used": 0.15, "model_version": "xgboost_v1", "missing_feature_count": 0, "missing_features_preview": [], "unexpected_feature_count": 0, "unexpected_features_preview": [] } ``` The response fields can be interpreted as follows:
- Source `API_USAGE.md`: - `risk_score` is the model-predicted default risk score for the submitted applicant. - `risk_band` translates the numeric score into a business-facing portfolio risk segment. - `high_risk_flag_015` indicates whether the applicant is above the candidate high-risk threshold of 0.15. - `threshold_used` records the decision threshold used in this API version for traceability. - `missing_feature_count` and `unexpected_feature_count` help validate API input quality before using the prediction for analysis or review. - `human_review_recommendation` summarizes whether the case should be reviewed by an analyst under the current rule set. - `audit_log_id` links the response to the JSONL audit log...
- Source `docs\DATA_DICTIONARY.md`: ## 7. Model Output Fields | Field | Layer | Definition | Business Interpretation | |---|---|---|---| | `risk_score` | Model output | Model-predicted probability-like default risk score. | Higher values indicate higher predicted default risk. | | `risk_band` | Scoring output | Business-facing portfolio risk segment derived from `risk_score`. | Supports portfolio segmentation from lowest to highest predicted risk. | | `high_risk_flag_015` | Scoring output | Binary flag equal to `1` when `risk_score >= 0.15`; otherwise `0`. | Candidate high-risk flag based on the 0.15 threshold. | | `threshold_used` | API output | Threshold used for high-risk flagging. | Makes scoring rules explicit and trac...
- Source `docs\DATA_MODEL_AND_LINEAGE.md`: | Source / Layer | Input fields or data | Transformation | Output artifact | Business purpose | | --- | --- | --- | --- | --- | | `application_train.csv` | Applicant profile, loan request, income, employment, demographic fields, `TARGET` | Add application-level affordability and exposure ratios | Model-ready application feature columns | Represent current borrower affordability, repayment burden, and exposure | | `bureau.csv` | `SK_ID_CURR`, bureau credit records, credit status, debt, overdue fields | Aggregate many bureau records to one applicant row | `outputs/bureau_features.csv` | Summarize external credit history and external debt burden | | `previous_application.csv` | Previous appl...
- Source `docs\DATA_DICTIONARY.md`: | Field | Layer | Definition | Business Interpretation | |---|---|---|---| | `top_positive_risk_drivers` | API explanation output | Highest positive local SHAP contributors for an applicant. | Features increasing the model output toward higher predicted default risk. | | `top_negative_risk_drivers` | API explanation output | Most negative local SHAP contributors for an applicant. | Features decreasing the model output toward lower predicted default risk. | | `feature` | Explanation detail | Feature name associated with a local SHAP contribution. | Identifies the model input driving the explanation. | | `feature_value` | Explanation detail | Applicant-specific value for the explained featu...
- Source `API_USAGE.md`: ```json { "human_review_recommendation": { "review_required": true, "review_priority": "high", "review_reasons": [ "Risk score is above the candidate high-risk threshold.", "Strong positive SHAP risk drivers are present." ] }, "audit_log_id": "b9c4f3f4-7c7e-4f5e-8c4d-55d6df4d3b4b" } ```

## 9. Analyst Notes

The applicant is above the candidate high-risk threshold, so an analyst may want to review affordability, external credit history, and prior application behavior before taking action.

The strongest risk-increasing signals to review are `EXT_SOURCE_3`, `EXT_SOURCE_2`, `n_active_bureau_credits`.

Both risk-increasing and risk-reducing SHAP signals are present, so the memo should be interpreted as decision support rather than a single deterministic decision.
