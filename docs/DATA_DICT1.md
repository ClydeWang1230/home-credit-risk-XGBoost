## Core raw / application features
AMT_CREDIT:  Total amount of credit applied.
AMT_ANNUITY: The amount of each annuity payment
AMT_INCOME_TOTAL: The amount of the applicant income
AMT_GOODS_PRICE: The amount of price of the goods that the applied credit is for 
DAYS_BIRTH:
DAYS_EMPLOYED
EXT_SOURCE_1
EXT_SOURCE_2
EXT_SOURCE_3

## Bureau features

SD_ID_BUREAU: 
SK_ID_BUREAU
Days_Credit
AMT_ANNUITY

## Identifier / label:
- SK_ID_CURR
- TARGET

## Core application fields:
- AMT_INCOME_TOTAL
- AMT_CREDIT
- AMT_ANNUITY
- AMT_GOODS_PRICE
- DAYS_BIRTH
- DAYS_EMPLOYED
- EXT_SOURCE_1
- EXT_SOURCE_2
- EXT_SOURCE_3

Engineered application features:
-- credit_income_ratio
-- credit_annuity_ratio
--credit_income_ratio
-- family income

Bureau features:
- n_active_bureau_credits
- total_overdue_amount
- bureau_debt_credit_ratio
- avg_credit_sum

Previous application features:
- prev_refusal_rate
- prev_refusal_count
- avg_down_payment_prev
- avg_credit_prev
- max_credit_prev
- days_decision_mean

Model / API outputs:
- risk_score
- risk_band
- high_risk_flag_015
- threshold_used
- model_version
- missing_feature_count
- unexpected_feature_count

SHAP outputs:
- top_positive_risk_drivers
- top_negative_risk_drivers
- shap_value
- contribution_direction
- contribution_rank
- value_status

Governance fields:
- human_review_recommendation
- review_required
- review_priority
- review_reasons
- audit_log_id

## Previous application features

## Self-constructed features