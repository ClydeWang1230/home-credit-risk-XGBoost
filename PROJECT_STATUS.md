# Project Status

## Week 3 Progress: V4.4 Optional LLM-Assisted Analyst Q&A

Added optional LLM-assisted answer generation to `POST /ask-analyst`.

The endpoint now supports deterministic and LLM-assisted modes. Deterministic `answer_summary`, `answer_sections`, scoring evidence, driver previews, review context, retrieved context, warnings, and limitations remain available as audit-friendly fallback fields.

LLM mode is opt-in through `use_llm=true` and uses environment variables such as `OPENAI_API_KEY` and `OPENAI_MODEL`. If configuration or the LLM call fails, the endpoint falls back to deterministic V4.3 output without failing the request.

## Week 3 Progress: V4.3 FastAPI Analyst Q&A Endpoint

Added `POST /ask-analyst`, which exposes the V4.2 deterministic analyst Q&A logic through FastAPI.

The endpoint answers one analyst question using an existing scoring response, local SHAP driver fields, local project documentation retrieval, governance fields, and optional human review case context. In V4.3 this behavior was deterministic; V4.4 added optional LLM-assisted generation on top of the same structured evidence.

The `/ask-analyst` response formatting was refined with structured `answer_sections`, compact `driver_preview`, concise retrieved context previews, and optional markdown output for cleaner Swagger/API consumption.

## Week 3 Progress: V4.2 Single-Turn Analyst Q&A

Added `src/agent_query.py`, a deterministic single-turn analyst Q&A layer for the existing lightweight RAG-style module.

The script answers one analyst question using the sample API scoring response, local project documentation retrieval, SHAP driver fields, governance fields, and optional human review case context when a `review_case_id` is provided. It writes the answer to `outputs/agent_outputs/analyst_question_answer.md`.

This V4.2 layer is local and template-based. It does not use LLM calls, embeddings, vector databases, LangChain, LlamaIndex, or multi-turn orchestration.

## Week 3 Progress: Lightweight RAG / Agent Memo MVP

Added a lightweight analyst-facing memo generator in `src/agent_memo.py`. The script reads a sample API scoring response, retrieves relevant snippets from local project documentation, and generates a credit risk review memo under `outputs/agent_outputs/`.

This MVP uses local markdown documentation and simple keyword-based retrieval. It is designed as a portfolio-ready analyst workflow prototype, not a production LLM or vector database system.

## Week 3 Progress: FastAPI V3.1 Human Review Workflow

Added a lightweight human review workflow to the FastAPI layer while preserving the V4.0 agent memo module.

New API workflow capabilities:

- `/predict-with-explanation` creates a review case when the rule-based recommendation requires analyst review.
- `GET /human-review/queue` returns a concise overview list of local review cases, with optional status filtering.
- `GET /human-review/{review_case_id}` remains the detailed investigation endpoint with decision history and linked scoring audit context.
- `POST /human-review/{review_case_id}/decision` appends a reviewer decision for a selected case.
- Review cases and review decisions are stored as local JSONL runtime artifacts under `outputs/api_logs/`.

This V3.1 workflow is intended for portfolio-ready governance demonstration. It is not a production case-management system.

## Week 3 Progress: FastAPI Scoring and Governance Layer

The trained XGBoost credit risk model is now exposed through a local FastAPI service. This milestone turns the project from an offline modeling pipeline into an explainable scoring service prototype.

Completed API capabilities:

- `GET /health` checks service readiness and confirms model artifacts are loaded.
- `POST /predict` returns risk score, risk band, high-risk flag, threshold, model version, and input quality checks.
- `POST /predict-with-explanation` returns local SHAP explanations for applicant-level risk drivers.
- The API includes a rule-based human review recommendation to support analyst triage.
- The API writes audit-friendly JSONL logs with model version, score, risk band, top SHAP drivers, and review recommendation.

Runtime audit logs are written to:

- `outputs/api_logs/scoring_audit_log.jsonl`

## 2026-07-10 — SHAP Explainability Layer v1

### Status

Added a SHAP-based explainability layer for the XGBoost credit risk model.

The current SHAP workflow generates global model explanation outputs and selected feature-level dependence plots. The goal is to explain not only which features are important, but also how key engineered credit risk features contribute to predicted default risk.

### New Outputs

Generated SHAP outputs:

- `outputs/reports/shap_global_importance.csv`
- `outputs/plots/shap_summary_bar.png`
- `outputs/plots/shap_summary_beeswarm.png`
- SHAP dependence plots for selected engineered features
- Valid-range dependence plots for bounded ratio features
- p99-clipped dependence plot for `avg_down_payment_prev`

### Global SHAP Findings

The SHAP global importance report shows that the strongest model drivers are:

- `EXT_SOURCE_3`
- `EXT_SOURCE_2`
- `EXT_SOURCE_1`
- `credit_goods_ratio`
- `credit_annuity_ratio`
- `bureau_debt_credit_ratio`
- `AMT_ANNUITY`
- `DAYS_EMPLOYED`
- `DAYS_BIRTH`
- `avg_down_payment_prev`
- `prev_refusal_rate`

This confirms that the model relies heavily on a combination of external credit score signals, loan structure variables, affordability indicators, bureau debt burden, demographic/employment features, and previous application behavior.

### Engineered Feature SHAP Findings

Several engineered features show meaningful and business-consistent SHAP patterns:

- `prev_refusal_rate` shows a clear positive relationship with predicted default risk after filtering to the valid 0–1 range. Higher historical refusal rate increases the model’s risk contribution.
- `prev_approval_rate` generally contributes negatively to predicted default risk as historical approval rate increases. This supports the interpretation that stronger historical lender acceptance is associated with lower modeled risk.
- `bureau_debt_credit_ratio` shows a clear positive SHAP relationship after excluding sentinel missing values. Higher external debt burden relative to credit exposure increases predicted default risk.
- `credit_goods_ratio` shows a positive non-linear relationship. Higher credit amount relative to goods price tends to increase risk contribution, supporting its interpretation as a financing coverage / borrower self-funding signal.
- `credit_annuity_ratio` shows a non-linear SHAP pattern rather than a simple monotonic relationship. This suggests repayment structure affects model risk estimates differently across ratio ranges.
- `avg_down_payment_prev` shows an overall downward SHAP pattern after p99 clipping. Higher historical average down payment tends to receive more negative SHAP contributions, suggesting lower modeled default risk.

### Visualization Hygiene

Some engineered ratio features contained sentinel missing values such as `-1000`, which distorted dependence plot axes.

To improve interpretability, additional valid-range plots were generated for bounded ratio features such as:

- `prev_refusal_rate`
- `prev_approval_rate`
- `credit_goods_ratio`
- `credit_annuity_ratio`
- `bureau_debt_credit_ratio`

For `avg_down_payment_prev`, large values were not treated as invalid. Instead, an additional p99-clipped dependence plot was created for visualization clarity while keeping the original full-range plot.

### Interpretation Notes

The SHAP results support the business interpretation that the model is not driven only by opaque model mechanics. Several top-ranked engineered features align with credit risk intuition, including historical refusal behavior, external debt burden, financing coverage, repayment structure, and prior down payment capacity.

External source features are the strongest global predictors. However, their internal definitions are not disclosed in the dataset, so they should be interpreted as external credit score signals rather than decomposed into specific economic drivers.

### Next Steps

Planned next steps for the SHAP explainability layer:

Use SHAP outputs later in:
   - FastAPI applicant-level scoring explanation
   - RAG / Agent analyst workflow
   - human review and audit-friendly model interpretation

## SQL Analytics Layer v1

Generated:
- `outputs/sql_reports/risk_analytics_base.csv`
- `outputs/sql_reports/01_risk_band_portfolio_summary.csv`
- `outputs/sql_reports/02_income_type_risk_summary.csv`
- `outputs/sql_reports/03_high_risk_flag_summary.csv`

SQL files:
- `sql_queries/01_risk_band_portfolio_summary.sql`
- `sql_queries/02_income_type_risk_summary.sql`
- `sql_queries/03_high_risk_flag_summary.sql`

Runner:
- `src/run_sql_reports.py`

Purpose:
A SQL analytics layer was added to convert model outputs into portfolio-level business analysis. The base analytics table joins predicted risk scores and risk bands with selected applicant profile fields from `application_train`.

The SQL reports are generated using DuckDB and saved as CSV outputs. This keeps the SQL logic separate from the Python modeling pipeline and makes the reporting layer easier to review and extend.

Reports created:

1. Risk band portfolio summary  
   This report summarizes applicant count, average risk score, observed default rate, high-risk flag rate, average income, average credit amount, and average annuity by predicted risk band.

2. Income type risk summary  
   This report segments applicants by `NAME_INCOME_TYPE` and `risk_band`. It helps identify how model risk bands behave across different applicant income categories. A `sample_size_note` and `interpretation_priority` field were added to avoid over-interpreting small-sample segments.

3. High-risk flag summary  
   This report compares applicants flagged by the candidate threshold `risk_score >= 0.15` against non-flagged applicants.

Key observations:
- SQL-generated risk band summaries are consistent with the earlier Python risk band reports.
- Observed default rate increases clearly from low-risk to high-risk bands.
- The income type segmentation shows that major segments such as Working, Commercial associate, Pensioner, and State servant maintain clear risk separation across bands.
- Small segments such as Unemployed, Student, Maternity leave, and Businessman should be interpreted cautiously due to limited sample size.
- The high-risk flag report shows that applicants flagged by the 0.15 threshold have a substantially higher observed default rate than non-flagged applicants.

Interpretation:
The SQL layer does not replace the ML pipeline. Instead, it extends the project from model training and scoring into portfolio segmentation and business-facing risk analytics.

## Current Stage
Week 1 - Pipeline Clean & Reproducibility

## Latest Update 

## Validation Threshold Analysis

Generated:
- `outputs/reports/threshold_analysis.csv`

Purpose:
The initial model evaluation used a baseline threshold of 0.5. This threshold produced high precision but very low recall because credit default prediction is an imbalanced classification problem and most predicted default probabilities are below 0.5.

The threshold analysis evaluates multiple candidate cutoffs on the validation set:
- 0.02
- 0.05
- 0.08
- 0.10
- 0.15
- 0.20
- 0.30
- 0.50

Key observation:
- Lower thresholds increase recall but flag a much larger share of applicants.
- Higher thresholds improve precision but miss many true default cases.
- Among the tested thresholds, `0.15` produced the highest F1 score, with:
  - predicted positive rate: 13.32%
  - precision: 25.87%
  - recall: 42.68%
  - F1 score: 32.22%

Interpretation:
The result shows the expected precision-recall trade-off in credit default prediction. A threshold of 0.15 can be treated as a candidate F1-balanced operating point, while the final business cutoff should depend on risk appetite, review capacity, and the relative cost of false positives versus false negatives.

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
