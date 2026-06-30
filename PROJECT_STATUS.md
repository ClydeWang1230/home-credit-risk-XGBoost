# Project Status

## Current Stage
Week 1 - Pipeline Clean & Reproducibility

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

## Feature Engineering
- bureau_features shape: (305811, 5)
- previous_application_features shape: (338857, 7)
- previous_application duplicate SK_ID_CURR count: 0

## Merge Validation
- application_train rows before previous_application feature merge: 307511
- application_train rows after previous_application feature merge: 307511
- Merge-safe validation passed.

## Model Result
- Model: XGBClassifier
- Validation AUC: 0.7553
- Full AUC value: 0.7552909080889085

## Artifacts Generated
- `outputs/metrics/metrics.json`
- `outputs/models/model.pkl`
- `outputs/models/feature_list.json`
- `outputs/risk_scores.csv`

## Notes
The project now supports local-first reproducible execution. This improves robustness because the pipeline no longer depends on Azure Blob Storage being available.

## Week 1 Progress
Completed local-first reproducible execution and saved baseline model artifacts.

## Next Steps
1. Standardize output folders.
2. Save metrics to `outputs/metrics/metrics.json`.
3. Save model artifact to `outputs/models/model.pkl`.
4. Save feature list to `outputs/models/feature_list.json`.
5. Continue previous_application Batch 2 feature expansion.