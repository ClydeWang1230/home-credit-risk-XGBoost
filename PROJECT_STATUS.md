# Project Status

## Current Stage
Week 1 - Pipeline Clean & Reproducibility

## Latest Update 
## Validation Evaluation Report

Generated:
- `outputs/reports/validation_risk_band_summary.csv`
- `outputs/reports/model_evaluation.json`

Purpose:
The existing `risk_band_summary.csv` is based on full prepared `application_train` scoring and is used as a portfolio-level diagnostic. To make the evaluation more rigorous, a separate validation-only risk band summary was added using only the validation split used for AUC calculation.

Validation setup:
- The model is trained on `X_train` / `y_train`.
- Validation AUC is calculated on `X_val` / `y_val`.
- `validation_risk_band_summary.csv` is generated from validation-set predictions only.
- The existing full-data `risk_scores.csv` and `risk_band_summary.csv` remain unchanged.

Validation risk band result:
- Validation AUC: 0.7649
- Observed default rate increases monotonically across validation risk bands:
  - Band 1 - Lowest Risk: 1.62%
  - Band 2: 3.05%
  - Band 3: 5.15%
  - Band 4: 9.09%
  - Band 5 - Highest Risk: 21.45%

Interpretation:
The validation-only risk band summary shows that the model can meaningfully rank unseen applicants by credit risk. The monotonic increase in observed default rate across risk bands supports the model's out-of-sample risk ranking ability.

Additional evaluation metrics:
`model_evaluation.json` now stores validation-level metrics, including:
- validation AUC
- precision
- recall
- F1 score
- confusion matrix
- threshold
- validation sample size

Note:
Precision, recall, F1 score, and confusion matrix currently use a baseline threshold of 0.5. Since credit default prediction is an imbalanced classification problem, this threshold is treated as a starting point rather than a final business cutoff.

## Feature importance observations after Batch 4A:
- `bureau_debt_credit_ratio` ranked 6th, suggesting that external bureau debt burden is a meaningful predictive signal.
- `n_active_bureau_credits` also appeared in the upper feature ranking, indicating that active external credit exposure contributes to risk prediction.
- Although Batch 4A only improved AUC from 0.7645 to 0.7649, the new bureau features improved the business completeness of the feature layer by adding external credit history and external debt burden signals.

## Key observations from feature importance:
- `credit_goods_ratio` ranked 7th, suggesting that financing coverage between credit amount and goods price is a meaningful predictive signal.
- `credit_annuity_ratio` ranked 13th, suggesting that the relationship between loan size and scheduled repayment amount contributes to risk prediction.
- This supports the strong AUC improvement from Batch 3A, where application-level affordability and exposure features improved AUC from 0.7577 to 0.7645.

## Batch 4A Result - bureau External Credit History Features

Added bureau history features:
- `n_active_bureau_credits`: number of active external bureau credit records.
- `n_closed_bureau_credits`: number of closed external bureau credit records.
- `active_credit_ratio`: share of active bureau credit records.
- `total_bureau_debt`: total external bureau debt amount.
- `bureau_debt_credit_ratio`: external debt relative to external credit amount.
- `max_credit_day_overdue`: maximum overdue days in bureau records.
- `n_overdue_bureau_records`: number of bureau records with overdue days greater than 0.

Validation:
- bureau_features shape: (305811, 12)
- previous_application_features shape: (338857, 12)
- application_train rows before merge: 307511
- application_train rows after merge: 307511

Model Result:
- AUC before Batch 4A: 0.7645
- AUC after Batch 4A: 0.7649
- Incremental improvement from Batch 4A: +0.0004

Interpretation:
The small lift suggests that external bureau history adds incremental predictive value. More importantly, it completes the feature layer by adding external credit behavior alongside current application affordability and internal previous-application history.

## Batch 3A Result - application_train Affordability and Exposure Features

Added application-level ratio features:
- `credit_income_ratio`: credit amount relative to borrower income.
- `annuity_income_ratio`: scheduled repayment amount relative to borrower income.
- `credit_annuity_ratio`: credit amount relative to scheduled repayment amount, approximating repayment horizon or amortization pressure.
- `credit_goods_ratio`: credit amount relative to goods price, approximating financing coverage.
- `income_per_family_member`: borrower income adjusted by family size.

Validation:
- application_train shape before ratio features: (307511, 122)
- application_train shape after ratio features: (307511, 127)
- previous_application_features shape: (338857, 12)
- duplicate SK_ID_CURR count: 0
- application_train rows before merge: 307511
- application_train rows after merge: 307511

Model Result:
- AUC before Batch 3A: 0.7577
- AUC after Batch 3A: 0.7645
- Incremental improvement from Batch 3A: +0.0068

Interpretation:
The strong improvement suggests that current borrower affordability and credit exposure ratios provide meaningful predictive signals. This aligns with credit risk intuition because repayment burden and income capacity are central to default risk assessment.
## Feature Importance Report
Generated:
- `outputs/reports/feature_importance.csv`

The report includes:
- feature importance from XGBoost
- importance ranking
- business category mappings
- business interpretations for engineered features

Key observations:
- `EXT_SOURCE_3` and `EXT_SOURCE_2` are the top-ranked external credit score features.
- `prev_refusal_rate` ranked 7th, suggesting that historical refusal behavior is a strong predictive signal.
- `avg_down_payment_prev` ranked 11th, suggesting that prior borrower self-funding/down payment behavior contributes to risk prediction.
- Other engineered previous_application features such as `prev_approval_rate`, `days_decision_mean`, and `avg_annuity_prev` also appear in the importance ranking.

Interpretation:
The feature importance report helps connect model output with credit risk business logic. Engineered previous_application features are not only merge-safe and performance-improving, but also interpretable as historical application behavior and borrower affordability signals.

## Batch 2B Result - previous_application Time Features

Added time-based previous application features:
- `days_decision_mean`: average historical decision timing from previous applications.
- `last_application_days`: most recent previous application timing, calculated as max `DAYS_DECISION` because values are negative and closer to 0 means more recent.

Validation:
- previous_application_features shape: (338857, 12)
- duplicate SK_ID_CURR count: 0
- application_train rows before merge: 307511
- application_train rows after merge: 307511

Model Result:
- Baseline AUC before Batch 2A: 0.7553
- AUC after Batch 2A amount features: 0.7576
- AUC after Batch 2B time features: 0.7577
- Incremental improvement from Batch 2B: +0.0001
- Total improvement from baseline: +0.0024
- 
## Current Pipeline Status
The main pipeline can now run successfully in local mode.

## Data Source
- Default data source: local
- Raw data path: `data/raw/`
- Azure Blob integration remains optional, but is currently not used because the Azure storage account is disabled.

## Loaded Data
- application_train: (307511, 122)
- bureau: (1716428, 17)
- previous_application: (1670214, 37)

## Batch 2A Result - previous_application Amount Features

Added amount-based previous application features:
- `avg_credit_prev`: average historical credit amount from previous applications.
- `max_credit_prev`: maximum historical credit amount from previous applications.
- `avg_down_payment_prev`: average historical down payment amount from previous applications.

Validation:
- previous_application_features shape: (338857, 10)
- duplicate SK_ID_CURR count: 0
- application_train rows before merge: 307511
- application_train rows after merge: 307511

Model Result:
- Baseline AUC before Batch 2A: 0.7553
- AUC after Batch 2A: 0.7576
- AUC improvement: +0.0023


## Model Result
- Model: XGBClassifier
- Baseline AUC before Batch 2A: 0.7553
- AUC after Batch 2A: 0.7576
- AUC improvement: +0.0023

## Artifacts Generated
- `outputs/metrics/metrics.json`
- `outputs/models/model.pkl` local only, ignored by Git
- `outputs/models/feature_list.json`
- `outputs/risk_scores.csv` local only, ignored by Git

## Notes
The project now supports local-first reproducible execution. This improves robustness because the pipeline no longer depends on Azure Blob Storage being available.

## Week 1 Progress
Completed local-first reproducible execution and saved baseline model artifacts.

## Next Steps

Build feature importance/explanation report:
- Export 'outputs/reports/feature_importance.csv'
- Include 'feature', 'importance' , 'business_category' , 'business_interpretation'
- Check whether new `previous_application` features appear in top features
5. Compare new AUC against the original 1.0 baseline: 0.7553.