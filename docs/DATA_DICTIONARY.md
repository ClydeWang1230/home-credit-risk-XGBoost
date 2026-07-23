# Data Dictionary

## 1. Purpose

This document provides business-friendly definitions for key source fields, engineered features, model outputs, SHAP explanation fields, and governance fields used in the Home Credit risk scoring project.

The dictionary supports data quality review, data modelling, explainability, and analyst interpretation. It focuses on the most important fields and feature groups rather than documenting every model input feature.

## 2. Identifier and Target Fields

| Field | Layer | Definition | Business Interpretation |
|---|---|---|---|
| `SK_ID_CURR` | Source / model base | Applicant-level unique identifier. | Primary key used to connect application records, engineered feature tables, model scores, explanations, and audit outputs. |
| `TARGET` | Source / validation | Observed default outcome in the dataset; `1` indicates observed default and `0` indicates observed non-default. | Historical outcome used for supervised model training and validation. |

## 3. Core Application-Level Fields

| Field | Layer | Definition | Business Interpretation |
|---|---|---|---|
| `AMT_INCOME_TOTAL` | Source application | Applicant reported total income. | Indicates borrower income capacity. |
| `AMT_CREDIT` | Source application | Requested credit amount. | Captures loan exposure requested by the applicant. |
| `AMT_ANNUITY` | Source application | Scheduled annuity or repayment amount. | Indicates expected repayment burden. |
| `AMT_GOODS_PRICE` | Source application | Price of the goods associated with the loan. | Helps compare loan amount against financed asset or purchase value. |
| `DAYS_BIRTH` | Source application | Applicant age represented as relative days in the original dataset. | Used as an age-related demographic signal after interpretation as relative days. |
| `DAYS_EMPLOYED` | Source application | Employment duration represented as relative days in the original dataset. | Employment stability signal; `DAYS_EMPLOYED = 365243` is a dataset-specific special encoded value and should not be interpreted as literal employment duration. |
| `EXT_SOURCE_1` | Source application | External source score from the original dataset. | External risk score signal; in this model, higher values generally tend to reduce predicted default risk. Internal composition is not disclosed. |
| `EXT_SOURCE_2` | Source application | External source score from the original dataset. | External risk score signal; in this model, higher values generally tend to reduce predicted default risk. Internal composition is not disclosed. |
| `EXT_SOURCE_3` | Source application | External source score from the original dataset. | External risk score signal; in this model, higher values generally tend to reduce predicted default risk. Internal composition is not disclosed. |

Amount fields capture income, requested credit, repayment amount, and goods price. Day-based fields are stored as relative day values in the original dataset. External source fields should be treated as externally defined score signals, not fully transparent economic variables.

## 4. Engineered Application Ratio Features

| Field | Layer | Definition | Business Interpretation |
|---|---|---|---|
| `credit_income_ratio` | Engineered application feature | `AMT_CREDIT / AMT_INCOME_TOTAL`. | Captures loan-to-income pressure and borrower affordability. |
| `credit_annuity_ratio` | Engineered application feature | `AMT_CREDIT / AMT_ANNUITY`. | Approximates repayment horizon or amortization pressure. |
| `credit_goods_ratio` | Engineered application feature | `AMT_CREDIT / AMT_GOODS_PRICE`. | Captures financing coverage and borrower self-funding context. |
| `income_per_family_member` | Engineered application feature | `AMT_INCOME_TOTAL / CNT_FAM_MEMBERS`. | Adjusts income capacity for household size. |

These features translate raw application amounts into business-oriented affordability, repayment burden, financing coverage, and household income context indicators.

## 5. Bureau Aggregated Features

| Field | Layer | Definition | Business Interpretation |
|---|---|---|---|
| `n_active_bureau_credits` | Engineered bureau feature | Count of active external bureau credit records by applicant. | Measures current external credit activity. |
| `total_overdue_amount` | Engineered bureau feature | Total overdue amount across bureau records. | Captures external delinquency amount. |
| `bureau_debt_credit_ratio` | Engineered bureau feature | Total bureau debt divided by total bureau credit amount. | Indicates external debt burden and credit utilization pressure. |
| `avg_credit_sum` | Engineered bureau feature | Average bureau credit amount by applicant. | Summarizes typical external credit exposure. |

Bureau features summarize external credit history and external credit burden at applicant level.

## 6. Previous-Application Aggregated Features

| Field | Layer | Definition | Business Interpretation |
|---|---|---|---|
| `prev_refusal_rate` | Engineered previous-application feature | Share of previous applications refused for the applicant. | Captures historical rejection behavior and potential prior credit risk signals. |
| `prev_refusal_count` | Engineered previous-application feature | Count of previous refused applications; currently represented in the feature pipeline as `n_prev_refusals`. | Measures frequency of prior refusals. |
| `avg_down_payment_prev` | Engineered previous-application feature | Average previous down payment amount by applicant. | Indicates prior self-funding behavior. |
| `avg_credit_prev` | Engineered previous-application feature | Average previous credit amount by applicant. | Summarizes typical prior credit size. |
| `max_credit_prev` | Engineered previous-application feature | Maximum previous credit amount by applicant. | Captures largest historical credit exposure. |
| `days_decision_mean` | Engineered previous-application feature | Average relative decision day across previous applications. | Indicates timing pattern of previous credit applications. |

These features summarize historical approval/refusal behavior, previous credit size, down payment behavior, and timing of previous credit applications.

## 7. Model Output Fields

| Field | Layer | Definition | Business Interpretation |
|---|---|---|---|
| `risk_score` | Model output | Model-predicted probability-like default risk score. | Higher values indicate higher predicted default risk. |
| `risk_band` | Scoring output | Business-facing portfolio risk segment derived from `risk_score`. | Supports portfolio segmentation from lowest to highest predicted risk. |
| `high_risk_flag_015` | Scoring output | Binary flag equal to `1` when `risk_score >= 0.15`; otherwise `0`. | Candidate high-risk flag based on the 0.15 threshold. |
| `threshold_used` | API output | Threshold used for high-risk flagging. | Makes scoring rules explicit and traceable. |
| `model_version` | API output | Saved model version identifier used by the API response. | Supports model governance and score traceability. |

## 8. API Input Quality Fields

| Field | Layer | Definition | Business Interpretation |
|---|---|---|---|
| `missing_feature_count` | API input quality | Number of required model features missing from the scoring request. | Indicates completeness of submitted model-ready features. |
| `missing_features_preview` | API input quality | Preview list of missing model features. | Helps diagnose incomplete scoring requests. |
| `unexpected_feature_count` | API input quality | Number of submitted fields not used by the model. | Indicates extra input fields ignored during scoring. |
| `unexpected_features_preview` | API input quality | Preview list of unexpected submitted fields. | Helps identify request formatting or data mapping issues. |
| `strict` | API request setting | Boolean setting that controls whether missing model features should fail the request. | Supports either flexible testing or stricter feature completeness validation. |

These fields help validate scoring request quality and feature alignment against the saved model feature list.

## 9. SHAP Explanation Fields

| Field | Layer | Definition | Business Interpretation |
|---|---|---|---|
| `top_positive_risk_drivers` | API explanation output | Highest positive local SHAP contributors for an applicant. | Features increasing the model output toward higher predicted default risk. |
| `top_negative_risk_drivers` | API explanation output | Most negative local SHAP contributors for an applicant. | Features decreasing the model output toward lower predicted default risk. |
| `feature` | Explanation detail | Feature name associated with a local SHAP contribution. | Identifies the model input driving the explanation. |
| `feature_value` | Explanation detail | Applicant-specific value for the explained feature. | Shows the value associated with the local contribution. |
| `value_status` | Explanation detail | Classification of the value as `actual_value`, `sentinel_missing`, or `special_encoded_value`. | Helps distinguish literal business values from missing or special encoded signals. |
| `shap_value` | Explanation detail | Local SHAP contribution value for the feature. | Positive values increase predicted default risk; negative values reduce predicted default risk. |
| `contribution_direction` | Explanation detail | Direction label for the SHAP contribution. | Separates risk-increasing and risk-reducing drivers. |
| `contribution_rank` | Explanation detail | Rank of the feature within the positive or negative driver list. | Helps analysts focus on the most material local drivers. |

## 10. Governance and Audit Fields

| Field | Layer | Definition | Business Interpretation |
|---|---|---|---|
| `human_review_recommendation` | API governance output | Rule-based review recommendation object returned by `/predict-with-explanation`. | Provides decision support for analyst review, not automated approval or rejection. |
| `review_required` | API governance output | Boolean flag indicating whether the current rule set recommends review. | Helps identify cases needing additional analyst attention. |
| `review_priority` | API governance output | Priority label such as `high`, `medium`, or `low`. | Supports triage of review cases. |
| `review_reasons` | API governance output | List of rule-based reasons for the review recommendation. | Makes the review trigger more transparent. |
| `audit_log_id` | API audit output | Unique identifier linking the API response to a persisted JSONL audit log entry. | Supports traceability between scoring event, model output, explanation, and governance recommendation. |

## 11. Sentinel and Special Encoded Values

| Value | Meaning | Interpretation Guidance |
|---|---|---|
| `-999` | Sentinel missing value used in model-ready inputs or reporting where appropriate. | Treat as a missing, unavailable, or no-history signal rather than a literal economic value. |
| `-1000` | Possible special or missing encoding depending on feature processing context. | Interpret cautiously and review feature context before drawing business conclusions. |
| `DAYS_EMPLOYED = 365243` | Dataset-specific special encoded value. | Do not interpret as a literal employment duration. |

These values should be documented and handled carefully in model interpretation, API responses, and local SHAP explanations.

## 12. Current Limitations

- This is not a full enterprise data dictionary.
- The dictionary focuses on representative fields and key model/API outputs.
- Additional engineered features can be documented as the project evolves.
- Some original dataset fields are anonymized or externally defined, so business interpretation should remain cautious.
- The API currently expects model-ready engineered features rather than raw source-table records.
