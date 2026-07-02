# Week 1 Summary

## 1. Week 1 Objective

The Week 1 objective was to move the Home Credit Risk XGBoost project from a Kaggle-style prototype toward a reproducible, business-oriented credit risk analytics pipeline.

The project is positioned for fintech, banking analytics, credit risk analytics, data analyst, and risk analyst roles. The focus is not only Kaggle AUC, but also reproducibility, explainability, disciplined feature engineering, and business interpretation.

## 2. Major Work Completed

- Refactored the pipeline to support local-first execution from `data/raw/`.
- Kept Azure Blob Storage as an optional data source.
- Fixed the Azure dependency issue caused by a disabled Azure storage account.
- Confirmed `main.py` runs end-to-end in local mode.
- Added metrics and artifact outputs:
  - `outputs/metrics/metrics.json`
  - `outputs/models/model.pkl`
  - `outputs/models/feature_list.json`
  - `outputs/risk_scores.csv`
- Updated `.gitignore` to exclude raw data, CSV outputs, model pickle artifacts, env files, virtual environments, and IDE files.
- Expanded `previous_application` feature engineering through baseline features, Batch 2A amount features, and Batch 2B time features.
- Added Batch 3A `application_train` affordability and exposure ratio features.
- Generated a feature importance report at `outputs/reports/feature_importance.csv`.
- Updated `README.md` into a Week 1 portfolio README v1.
- Updated `PROJECT_STATUS.md` and `FEATURE_EXPANSION_PLAN.md`.

## 3. Feature Engineering Progress

The feature layer now includes applicant-level features from `previous_application`, bureau history, and `application_train`.

Previous application features include:

- Baseline previous-application behavior features
- Batch 2A amount features
- Batch 2B time features

Key previous-application features include refusal history, approval behavior, average and maximum prior credit amounts, prior down payment behavior, and application recency.

Batch 3A added application-level affordability and exposure ratios, including:

- `credit_income_ratio`
- `annuity_income_ratio`
- `credit_annuity_ratio`
- `credit_goods_ratio`
- `income_per_family_member`

These features improve business interpretability by connecting borrower income, repayment burden, credit exposure, financing coverage, and household capacity.

## 4. Model Performance Progression

Validation metric: ROC AUC.

| Stage | Validation AUC |
| --- | ---: |
| Initial local baseline | 0.7553 |
| After previous_application amount features | 0.7576 |
| After previous_application time features | 0.7577 |
| After application_train affordability ratio features | 0.7645 |

The strongest Week 1 lift came from adding application-level affordability and exposure ratio features.

## 5. Explainability Progress

The pipeline now generates `outputs/reports/feature_importance.csv`, including:

- `feature`
- `importance`
- `importance_rank`
- `business_category`
- `business_interpretation`

Key feature importance observations:

- `EXT_SOURCE_3` and `EXT_SOURCE_2` remain top-ranked external credit score features.
- `prev_refusal_rate` ranked highly and acts as a strong historical rejection signal.
- `credit_goods_ratio` ranked highly and captures financing coverage.
- `avg_down_payment_prev` and `credit_annuity_ratio` also appeared relatively high.

This makes the model output easier to discuss in portfolio reviews and interviews.

## 6. Engineering and Reproducibility Improvements

- Local-first execution is now the default.
- Azure Blob Storage remains available as an optional data source.
- `main.py` runs end-to-end from local raw CSV files.
- Metrics, model artifacts, feature lists, risk scores, and feature importance reports are saved consistently.
- Raw data, generated outputs, model pickle files, env files, virtual environments, and IDE files are excluded from GitHub.
- Merge validation is built into the pipeline output and logging.

## 7. Key Learnings

- Small, business-interpretable features can improve model performance while making the project easier to explain.
- Historical refusal behavior is a strong risk signal.
- Affordability and exposure ratios provide meaningful lift and are intuitive for credit risk discussion.
- Merge validation is essential when converting one-to-many historical tables into one-row-per-applicant features.
- A portfolio project becomes stronger when predictive performance, reproducibility, and business interpretation are developed together.

## 8. Current Stable State

The current pipeline is stable in local mode.

Validation checks:

- `application_train` row count is preserved at `307511` after merges.
- `previous_application` feature table remains one row per `SK_ID_CURR`.
- Duplicate `SK_ID_CURR` count is `0`.
- Pipeline runs successfully from local `data/raw/`.

Current generated artifacts:

- `outputs/metrics/metrics.json`
- `outputs/models/model.pkl`
- `outputs/models/feature_list.json`
- `outputs/risk_scores.csv`
- `outputs/reports/feature_importance.csv`

## 9. Week 2 Planned Focus

Week 2 should build on the stable Week 1 pipeline without overclaiming unfinished work.

Priority focus areas:

1. Portfolio risk reporting
   - Add risk score bands.
   - Generate portfolio-level risk summaries by predicted risk band.
   - Compare average predicted risk and observed default rate across bands.

2. Model evaluation beyond AUC
   - Add precision, recall, F1 score, and confusion matrix.
   - Consider KS statistic or top-decile default rate after the basic evaluation report is stable.

3. Bureau feature expansion
   - Add a small batch of external credit history features with clear risk interpretation.
   - Focus on active credit count, closed credit count, overdue records, external debt, and debt-to-credit exposure.

4. Explainability improvement
   - Refresh feature importance after new bureau features.
   - Improve business interpretation for top-ranked engineered features.
   - Consider SHAP only after the feature layer is stable.

5. SQL analytics layer
   - Explore SQL-based portfolio segmentation and risk band analysis.
   - Keep this aligned with future AI-assisted analytics and SQL assistant ideas.

Future roadmap:
- FastAPI scoring endpoint
- RAG-based credit knowledge retrieval
- AI-assisted analyst workflow
