# Project Status

## Current Stage
Week 1 - Pipeline Clean & Reproducibility

## Latest Update 
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