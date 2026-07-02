# Feature Expansion Plan

## Batch 4A - bureau External Credit History Features

Status: Completed

Added:
- `n_active_bureau_credits`
- `n_closed_bureau_credits`
- `active_credit_ratio`
- `total_bureau_debt`
- `bureau_debt_credit_ratio`
- `max_credit_day_overdue`
- `n_overdue_bureau_records`

Result:
- bureau_features increased from 5 to 12 columns.
- Validation AUC improved from 0.7645 to 0.7649.
- Merge-safe validation passed.

Business meaning:
These features summarize external credit activity, external debt burden, bureau overdue behavior, and active credit exposure.
## Batch 3A - application_train Affordability Features

Status: Completed

Added:
- `credit_income_ratio`
- `annuity_income_ratio`
- `credit_annuity_ratio`
- `credit_goods_ratio`
- `income_per_family_member`

Result:
- application_train increased from 122 to 127 columns.
- Validation AUC improved from 0.7577 to 0.7645.
- Merge-safe validation passed.

Business meaning:
These features summarize current borrower affordability, repayment burden, credit exposure, and household income pressure.

## Batch 2B - Time Features

Status: Completed

Added:
- `days_decision_mean`
- `last_application_days`

Validation:
- previous_application_features increased from 10 to 12 columns.
- duplicate SK_ID_CURR count: 0
- application_train row count preserved: 307511 → 307511

Result:
- Validation AUC improved slightly from 0.7576 to 0.7577.
- Time-based features provided a smaller marginal lift than amount-based features.
- 
## Batch 2A - Amount Features (1. July)

Status: Completed

Added:
- `avg_credit_prev`
- `max_credit_prev`
- `avg_down_payment_prev`

Result:
- previous_application_features increased from 7 to 10 columns.
- Validation AUC improved from 0.7553 to 0.7576.
- Merge-safe validation passed.

### Previous Application Feature Expansion — Batch 1 （1. June)

Added:
- `n_prev_applications`
- `n_prev_approved`
- `prev_approval_rate`
- `prev_refusal_rate`

Validated:
- Output remains one row per `SK_ID_CURR`
- Duplicated applicant IDs = 0
- Approval and refusal rates remain within [0, 1]
- Merge into `application_train` preserves row count
- 
## 1. Purpose of Feature Expansion

The next goal is to strengthen the business interpretability and predictive usefulness of the feature layer. This is not about adding as many variables as possible. The priority is to build applicant-level features that are explainable in a banking, fintech, and credit risk analytics context, while keeping the pipeline reproducible and easy to validate.

Feature expansion should focus on converting historical one-to-many tables into clean, merge-safe, applicant-level risk signals.

## 2. Current Feature Baseline

The current `previous_application` feature builder produces:

- `SK_ID_CURR`: applicant identifier used for safe merging into `application_train`.
- `n_prev_refusals`: number of previous applications where `NAME_CONTRACT_STATUS == "Refused"`.
- `avg_annuity_prev`: average previous application annuity after positive-value filtering and percentile-based outlier capping.

The current bureau feature builder also produces applicant-level credit bureau aggregates:

- `bureau_record_count`
- `avg_credit_sum`
- `total_overdue_amount`
- `avg_days_credit_update`

This baseline is intentionally small and interpretable. It provides a clean foundation for expanding the feature layer without making the pipeline difficult to explain or debug.

## 3. Candidate `previous_application` Features

| Feature Name | Source Columns | Business Meaning | Aggregation Logic | Potential Data Quality Concern | Implementation Priority |
| --- | --- | --- | --- | --- | --- |
| `n_prev_applications` | `SK_ID_CURR` | Total prior application volume; captures borrower credit-seeking history. | Count previous application rows by `SK_ID_CURR`. | Duplicate or repeated application records may inflate counts. | High |
| `n_prev_approved` | `SK_ID_CURR`, `NAME_CONTRACT_STATUS` | Number of historically approved applications; indicates prior credit access. | Count rows where status is `Approved` by `SK_ID_CURR`. | Status spelling or unexpected categories. | High |
| `n_prev_refused` | `SK_ID_CURR`, `NAME_CONTRACT_STATUS` | Number of historically refused applications; direct risk signal. | Count rows where status is `Refused` by `SK_ID_CURR`. | Should align with existing `n_prev_refusals` naming or replace it deliberately. | High |
| `prev_approval_rate` | `SK_ID_CURR`, `NAME_CONTRACT_STATUS` | Share of prior applications approved; summarizes historical lender acceptance. | `n_prev_approved / n_prev_applications`. | Division by zero if applicant has no prior records after filtering. | High |
| `prev_refusal_rate` | `SK_ID_CURR`, `NAME_CONTRACT_STATUS` | Share of prior applications refused; summarizes rejection history. | `n_prev_refused / n_prev_applications`. | Must be consistent with included status categories. | High |
| `avg_credit_prev` | `SK_ID_CURR`, `AMT_CREDIT` | Average previous requested or granted credit amount; approximates historical borrowing size. | Mean `AMT_CREDIT` by `SK_ID_CURR` after reasonable cleaning. | Outliers, missing values, and zero values. | Medium |
| `max_credit_prev` | `SK_ID_CURR`, `AMT_CREDIT` | Largest prior credit amount; captures maximum historical exposure. | Max `AMT_CREDIT` by `SK_ID_CURR`. | Extreme high values may need percentile capping. | Medium |
| `avg_down_payment_prev` | `SK_ID_CURR`, `AMT_DOWN_PAYMENT` | Average down payment; may indicate borrower liquidity or product type. | Mean `AMT_DOWN_PAYMENT` by `SK_ID_CURR`. | Often missing depending on product type. | Medium |
| `days_decision_mean` | `SK_ID_CURR`, `DAYS_DECISION` | Average recency of previous application decisions. | Mean `DAYS_DECISION` by `SK_ID_CURR`. | Negative-day convention must be clearly documented. | Medium |
| `days_decision_min` | `SK_ID_CURR`, `DAYS_DECISION` | Oldest prior application decision timing. | Min `DAYS_DECISION` by `SK_ID_CURR`. | Very old or invalid negative values may distort history. | Low |
| `last_application_days` | `SK_ID_CURR`, `DAYS_DECISION` | Most recent prior application timing; recent applications may indicate active credit seeking. | Max `DAYS_DECISION` by `SK_ID_CURR` because values are negative days before current application. | Must confirm `DAYS_DECISION` sign convention. | High |

## 4. Candidate Bureau Features

| Feature Name | Source Columns | Business Meaning | Aggregation Logic | Potential Data Quality Concern | Implementation Priority |
| --- | --- | --- | --- | --- | --- |
| `active_credit_count` | `SK_ID_CURR`, `CREDIT_ACTIVE` | Number of currently active external credit records. | Count rows where `CREDIT_ACTIVE == "Active"` by applicant. | Status values may include unexpected categories. | High |
| `closed_credit_count` | `SK_ID_CURR`, `CREDIT_ACTIVE` | Number of closed external credit records; captures completed credit history. | Count rows where `CREDIT_ACTIVE == "Closed"` by applicant. | Closed records may include very old history. | Medium |
| `total_overdue_amount` | `SK_ID_CURR`, `AMT_CREDIT_SUM_OVERDUE` | Total currently overdue amount across bureau records. | Sum overdue amount by applicant. | Missing values and extreme overdue balances. | Already baseline |
| `avg_credit_sum` | `SK_ID_CURR`, `AMT_CREDIT_SUM` | Average external credit amount. | Mean credit sum by applicant. | Outliers and missing values. | Already baseline |
| `max_credit_sum` | `SK_ID_CURR`, `AMT_CREDIT_SUM` | Maximum external credit exposure. | Max credit sum by applicant. | Extreme values may need capping. | Medium |
| `avg_days_credit` | `SK_ID_CURR`, `DAYS_CREDIT` | Average age of bureau credit records. | Mean `DAYS_CREDIT` by applicant. | Negative-day convention must be documented. | Medium |
| `recent_bureau_update_days` | `SK_ID_CURR`, `DAYS_CREDIT_UPDATE` | Most recent bureau update timing; useful for data freshness and recent credit behavior. | Max `DAYS_CREDIT_UPDATE` by applicant. | Must confirm sign convention and missing values. | Medium |

## 5. Recommended Implementation Order

1. Expand `previous_application` features first because the notebook already establishes the business rationale and initial implementation pattern.
2. Validate that the expanded feature table still has one row per `SK_ID_CURR`.
3. Validate that merging the expanded feature table into `application_train` does not change the row count.
4. Compare baseline vs expanded model AUC to confirm whether the added features improve predictive ranking.
5. Expand bureau features after the previous application layer is stable.
6. Add feature importance and interpretation notes so results can be explained in a risk analytics interview.

## 6. Validation Checklist

- Confirm output shape for each feature table.
- Confirm duplicated `SK_ID_CURR` count is `0`.
- Confirm `application_train` row count before and after merge.
- Check missing value counts for each new feature.
- Review feature distributions for impossible values, extreme outliers, and heavy missingness.
- Confirm each feature has a clear banking or credit risk interpretation.
- Confirm naming is consistent and interview-friendly.
- Confirm baseline vs expanded model AUC is tracked before declaring improvement.

## 7. What Not To Do Yet

- Do not add all Home Credit tables yet.
- Do not add `installments_payments` yet.
- Do not add `POS_CASH_balance` yet.
- Do not tune model hyperparameters yet.
- Do not start RAG or an AI assistant layer yet.
- Do not over-engineer the pipeline before the feature layer is stable.
- Do not create empty modules or folders before they have a clear role.
- Do not add features that cannot be explained in a banking or risk analytics context.

## 8. Interview Narrative

I expanded the original Kaggle-style notebook into a modular feature engineering pipeline. I started with previous application history and bureau credit records, converted one-to-many historical tables into applicant-level risk features, validated merge safety, and connected the outputs to an Azure-backed pipeline.
