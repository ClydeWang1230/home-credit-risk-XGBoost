# Notebook to Source Migration Plan

## 1. Logic Currently Appearing in Notebooks

The current notebook reviewed is `notebooks/kaggle_eda.ipynb`. It appears to contain a Kaggle-style exploratory workflow for the Home Credit Default Risk project.

Notebook logic currently includes:

- Project framing and methodology notes based on an improved version of a Kaggle exploratory modeling workflow.
- Local Kaggle-style file loading from `../input/`, including `application_train.csv`, `application_test.csv`, and `previous_application.csv`.
- Exploratory data analysis for target distribution and default rate.
- Missing value discussion, especially the distinction between numeric missing values and categorical missing values for XGBoost.
- Previous application analysis, including object column review, missing checks, contract status distribution, and annuity visualization by contract status.
- Outlier treatment for `previous_application`, including:
  - Capping `AMT_ANNUITY` at the 99.9th percentile.
  - Filtering `AMT_ANNUITY` to positive values.
  - Filtering `DAYS_DECISION` to a reasonable historical range.
  - Keeping selected `NAME_CONTRACT_STATUS` values.
- Feature engineering from `previous_application`, including:
  - `n_prev_refusals`: count of refused previous applications by applicant.
  - `avg_annuity_prev`: average previous application annuity by applicant.
  - Merging these features into train and test application tables.
- Visualization of engineered features against default rate.
- XGBoost model training and validation using train/validation split and ROC-AUC.
- Manual categorical conversion using pandas category codes for object/category columns.
- Experimentation with XGBoost parameters, including a commented early stopping experiment.
- Kaggle-style submission generation with `SK_ID_CURR` and predicted `TARGET`.

## 2. Logic Currently Appearing in `main.py` and `src/`

The current source code already contains a small production-style pipeline, but some responsibilities are still mixed between modules and the main entry point.

Current `main.py` logic:

- Imports Azure configuration, ingestion helper, bureau feature builder, and model helpers.
- Defines `load_csv_from_blob`, which downloads a CSV from Azure Blob Storage and loads it into pandas.
- Defines `upload_file_to_blob`, which uploads a local file to Azure Blob Storage.
- Creates an Azure Blob client.
- Loads `bureau.csv` and `application_train.csv` from blob storage.
- Builds bureau-level applicant features.
- Writes `outputs/bureau_features.csv`.
- Uploads bureau features to blob storage.
- Merges bureau features into the application training data.
- Trains an XGBoost model using `src.model.train_model`.
- Prints validation AUC.
- Generates applicant risk scores with `src.model.predict`.
- Writes `outputs/risk_scores.csv`.
- Uploads risk scores to blob storage.

Current `src/config.py` logic:

- Loads environment variables using `python-dotenv`.
- Reads Azure storage account and key from environment variables.
- Defines a hard-coded container name.

Current `src/data_ingestion.py` logic:

- Creates an Azure Blob Storage client from account name and account key.

Current `src/feature_engineering.py` logic:

- Builds bureau-based aggregate features by `SK_ID_CURR`, including:
  - Bureau record count.
  - Average credit sum.
  - Total overdue amount.
  - Average days since credit update.

Current `src/model.py` logic:

- Prepares features by dropping target and applicant ID columns.
- Keeps numeric and boolean columns only.
- Fills missing values with `-999`.
- Splits training data into train and validation sets.
- Trains an `XGBClassifier`.
- Calculates validation ROC-AUC.
- Predicts risk scores using `predict_proba`.

## 3. Notebook Logic That Should Remain Exploratory

Some notebook content is valuable as analysis and project explanation, but should not be migrated directly into reusable source modules.

Keep exploratory:

- Narrative markdown explaining project motivation, Kaggle baseline context, and modeling rationale.
- One-off dataset shape inspection, `.head()` previews, and local file listing.
- Target distribution exploration and default rate visualization.
- Exploratory missing-value inspection where it is used for human understanding rather than pipeline validation.
- Contract status distribution checks used to understand the data.
- Boxplots and bar charts used for hypothesis generation.
- Written interpretation of why previous refusals and annuity may be predictive.
- Experimental markdown comparing model versions and possible future work.
- Commented-out model experiments unless they become a deliberate, repeatable training configuration.
- Kaggle-specific submission workflow as-is, unless the project still needs a formal Kaggle submission mode.

## 4. Notebook Logic That Should Be Migrated Into `src/`

Several notebook components look reusable and should eventually move into formal source modules once the target behavior is confirmed.

Candidate migration items:

- Previous application cleaning logic:
  - `AMT_ANNUITY` positive filtering.
  - `AMT_ANNUITY` high-value capping.
  - `DAYS_DECISION` range filtering.
  - Valid `NAME_CONTRACT_STATUS` filtering.
- Previous application feature engineering:
  - `n_prev_refusals`.
  - `avg_annuity_prev`.
  - Merge-safe applicant-level aggregation by `SK_ID_CURR`.
- Categorical feature handling:
  - Identify object/category columns.
  - Convert categorical values in a consistent train/test-safe way.
  - Avoid notebook-only category coding that may produce inconsistent codes between train and test.
- Model evaluation:
  - ROC-AUC calculation.
  - Train/validation split configuration.
  - Optional structured metric output.
- Prediction output construction:
  - Applicant ID plus predicted risk score.
  - Eventually separate Kaggle `TARGET` submission output from portfolio risk scoring output.
- Risk scoring logic:
  - Future risk bands, thresholds, and business-facing interpretation should become source code once the core predictive pipeline is stable.

## 5. Recommended Target Module for Migrated Logic

Recommended migration mapping:

| Notebook logic | Recommended target module | Notes |
| --- | --- | --- |
| Local CSV loading from Kaggle paths | Do not migrate yet, or add later to `data_ingestion.py` | Current pipeline uses Azure Blob Storage. Local file loading can wait unless a local mode is required. |
| Previous application cleaning | `src/preprocessing.py` | Add when cleaning rules are confirmed and tested. |
| Missing-value policy notes | `src/preprocessing.py` and documentation | Numeric/categorical policy should become explicit pipeline behavior, not only markdown. |
| Previous refusal count | `src/feature_engineering.py` | Add as `build_previous_application_features` or similar. |
| Average previous annuity | `src/feature_engineering.py` | Combine with previous refusal count in one applicant-level feature builder. |
| Bureau aggregate features | Already in `src/feature_engineering.py` | Preserve and possibly align naming/style with future feature builders. |
| Train/validation split and XGBoost training | Already in `src/model.py` | Improve after feature responsibilities are clearer. |
| Manual category-code encoding | `src/preprocessing.py` or `src/model.py` | Needs careful design because independent train/test category coding can be unsafe. |
| ROC-AUC metric calculation | `src/evaluation.py` | Add later when evaluation reporting becomes broader than one AUC print. |
| Risk score prediction | Already partly in `src/model.py` | Keep prediction probability logic there for now. |
| Risk bands and decision labels | `src/scoring.py` | Future addition only after scoring policy is defined. |
| Kaggle submission creation | Future `src/scoring.py`, `src/outputs.py`, or a separate script | Do not migrate until it is clear whether the project supports Kaggle submission, business risk scoring, or both. |
| Exploratory plots | Keep in notebooks for now; later `reports/figures/` workflow | Only migrate chart generation if repeatable reports become a requirement. |

Possible future source layout:

```text
src/
  config.py
  data_ingestion.py
  preprocessing.py
  feature_engineering.py
  model.py
  evaluation.py
  scoring.py
```

This structure should be introduced gradually. Empty files should not be created before they have real responsibilities.

## 6. Safe Migration Order

1. Review the notebook outputs and confirm which engineered features are still desired for the V1.1 pipeline.
2. Keep `src/` as the formal source code directory and preserve the current working modules.
3. Extract previous application cleaning into `src/preprocessing.py` only when the cleaning rules are confirmed.
4. Add previous application feature aggregation to `src/feature_engineering.py`, preferably as a new function rather than changing the existing bureau feature function.
5. Update `main.py` later to call previous application feature logic only after the new functions are tested with real data.
6. Improve categorical handling after deciding whether the model will use numeric-only features, explicit encoding, or XGBoost categorical support.
7. Move evaluation logic into `src/evaluation.py` when the project needs reusable metrics, validation reports, or model comparison.
8. Add `src/scoring.py` only when risk bands, thresholds, or business decision labels are ready to implement.
9. Split outputs into predictions, metrics, and reports only after the pipeline consistently produces those artifacts.
10. Update `README.md` after module responsibilities and the runnable pipeline stabilize.

## 7. What Should Not Be Migrated Yet

Do not migrate yet:

- One-off EDA cells whose primary purpose is human exploration.
- Markdown narrative, interpretation, and project storytelling from the notebook.
- Temporary `.head()`, `.shape`, `.value_counts()`, and visual inspection cells.
- Kaggle-specific `../input/` assumptions unless a local data mode is intentionally added.
- Kaggle submission generation until the project decides whether submission output remains a supported deliverable.
- Commented-out hyperparameter experiments until they are selected as formal training behavior.
- Risk bands, AI/RAG, or assisted decision support layers before the core risk analytics pipeline is mature.
- Broad output restructuring before the current output files and downstream references are reviewed.
- Empty future modules or folders without working code that needs to live there.

The immediate next step should be reviewing this migration plan and deciding which notebook-derived logic should become part of the V1.1 production-style pipeline.
