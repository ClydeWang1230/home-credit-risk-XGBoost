# Home Credit Risk Decision-Support System

An end-to-end credit risk decision-support system using Python, XGBoost, SHAP, FastAPI, audit logging, human review workflow, and an LLM-assisted RAG-style analyst assistant.

This project started from the Home Credit Default Risk dataset and evolved from a Kaggle-style modeling prototype into a portfolio-grade credit risk analytics and decision-support system. The focus is not only model AUC, but also reproducibility, explainability, data quality, governance traceability, API design, and analyst usability.

Current milestone: V4.4, with deterministic analyst Q&A and optional LLM-assisted answer generation through `/ask-analyst`.

## Why This Project Matters

Credit risk analytics work does not stop at model training. A useful risk system needs reliable feature engineering, explainable scoring, clear thresholds, traceable decisions, analyst review support, and documentation that data and risk teams can understand.

This project demonstrates skills relevant to Data Analyst, Data Technology, Banking Analytics, FinTech Analytics, and Risk Analytics roles:

- Translating raw one-to-many credit history tables into applicant-level model features.
- Training and evaluating a default risk model.
- Explaining model behavior with global and local SHAP outputs.
- Serving model-ready scoring through FastAPI.
- Capturing input quality checks, audit logs, and review recommendations.
- Supporting analyst interpretation through deterministic and optional LLM-assisted Q&A.

## Architecture

### Data Layer

- Local-first raw data loading from `data/raw/`.
- Optional Azure Blob loading support remains available.
- Raw CSV files are excluded from GitHub through `.gitignore`.

Main source tables:

- `application_train.csv`
- `bureau.csv`
- `previous_application.csv`

### Feature Engineering Layer

Feature engineering converts raw and historical credit data into one applicant-level model row.

Key feature groups:

- Application affordability and exposure ratios:
  - `credit_income_ratio`
  - `annuity_income_ratio`
  - `credit_annuity_ratio`
  - `credit_goods_ratio`
  - `income_per_family_member`
- Bureau external credit history features:
  - active and closed bureau credit counts
  - overdue amount
  - external debt burden
  - bureau debt-to-credit ratio
- Previous-application history features:
  - approval/refusal counts and rates
  - previous credit amounts
  - down payment behavior
  - previous application timing

### Model Scoring Layer

- XGBoost classifier for default risk scoring.
- Saved model artifact:
  - `outputs/models/model.pkl`
- Saved model feature order:
  - `outputs/models/feature_list.json`
- Risk score outputs:
  - `outputs/risk_scores.csv`
- Candidate high-risk threshold:
  - `0.15`

### Explainability Layer

The project includes both global and local model explainability.

Generated outputs include:

- `outputs/reports/feature_importance.csv`
- `outputs/reports/shap_global_importance.csv`
- `outputs/plots/shap_summary_bar.png`
- `outputs/plots/shap_summary_beeswarm.png`
- selected SHAP dependence plots
- local SHAP examples

Local API explanations return:

- `top_positive_risk_drivers`
- `top_negative_risk_drivers`
- value status for sentinel and special encoded values

### API Layer

FastAPI exposes the saved model and analyst workflow as local endpoints. The API loads saved artifacts rather than retraining.

Key endpoints:

| Endpoint | Purpose |
|---|---|
| `GET /health` | Check API and model artifact readiness. |
| `POST /predict` | Score model-ready applicant features. |
| `POST /predict-with-explanation` | Score applicant features and return local SHAP drivers, review recommendation, and audit id. |
| `GET /human-review/queue` | Return a concise review queue overview. |
| `GET /human-review/{review_case_id}` | Return detailed review case context, decision history, and linked audit log. |
| `POST /human-review/{review_case_id}/decision` | Append an analyst review decision. |
| `POST /ask-analyst` | Answer a single analyst question using scoring evidence, SHAP drivers, documentation retrieval, optional review context, and optional LLM assistance. |

Detailed API instructions are in [API_USAGE.md](API_USAGE.md).

### Governance, Audit, and Human Review Layer

The API includes lightweight governance support:

- Missing feature detection.
- Unexpected feature detection.
- Feature alignment against `feature_list.json`.
- Rule-based human review recommendation.
- Audit-friendly scoring logs.
- Review queue and case detail endpoints.
- Reviewer decision logging.

Runtime JSONL logs are stored locally under:

```text
outputs/api_logs/
```

These logs are ignored by Git because they change during local API tests.

### RAG / LLM Analyst Assistant Layer

The project includes two analyst-support layers:

- `src/agent_memo.py`: generates a credit risk review memo from a scoring response and local documentation snippets.
- `src/agent_query.py`: answers one analyst question from local scoring evidence, SHAP drivers, review context, and retrieved documentation.

FastAPI V4.4 exposes analyst Q&A through:

```text
POST /ask-analyst
```

The endpoint supports:

- deterministic answer generation by default
- optional LLM-assisted answer generation with `use_llm=true`
- deterministic fallback when the LLM is disabled, unavailable, missing configuration, or fails
- request-level LLM model override through `llm_model`

No API keys or secrets are stored in the repository. LLM configuration uses environment variables such as:

```text
OPENAI_API_KEY
OPENAI_MODEL
```

## Key Features

- Local-first reproducible ML pipeline.
- Azure Blob support as an optional data source.
- Applicant-level feature engineering from application, bureau, and previous-application data.
- XGBoost default risk model.
- Risk score, risk band, and high-risk flag generation.
- Validation-only and full-portfolio risk band reporting.
- Feature importance and SHAP explainability.
- FastAPI scoring service.
- API input quality checks.
- JSONL audit logging.
- Rule-based human review recommendation.
- Lightweight human review workflow.
- SQL analytics reports using DuckDB.
- Data model, lineage, data quality, governance, and API requirements documentation.
- Deterministic RAG-style analyst memo and Q&A tools.
- Optional LLM-assisted analyst answer generation with deterministic fallback.

## Example Analyst Questions

The `/ask-analyst` endpoint can answer questions such as:

- "Why is this applicant high risk?"
- "What are the main SHAP risk drivers?"
- "What does EXT_SOURCE_3 mean?"
- "Why was this case recommended for human review?"
- "Has this case been reviewed?"
- "What is the latest analyst decision?"
- "What does the audit_log_id support?"
- "Are there any data quality issues?"
- "Which features reduce the predicted risk?"

## Model Performance Snapshot

Validation metric: ROC AUC.

| Stage | Feature Update | Validation AUC |
|---|---|---:|
| Initial local baseline | Local pipeline with initial bureau and previous-application features | 0.7553 |
| Batch 2A | Added previous-application amount features | 0.7576 |
| Batch 2B | Added previous-application time features | 0.7577 |
| Batch 3A | Added application affordability and exposure ratio features | 0.7645 |
| Batch 4A | Added bureau external credit history features | 0.7649 |

The AUC improvements are modest but the feature layer becomes more business-complete and easier to explain in a credit risk context.

## How To Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Place raw Home Credit CSV files under:

```text
data/raw/
```

Run the training and reporting pipeline:

```bash
python main.py
```

Start the FastAPI service:

```bash
uvicorn src.api:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Generate a deterministic analyst Q&A answer locally:

```bash
python src/agent_query.py --question "Why is this applicant high risk?"
```

Use optional LLM-assisted `/ask-analyst` mode only after configuring environment variables:

```text
OPENAI_API_KEY
OPENAI_MODEL
```

## Important Repository Notes

The following are excluded from GitHub where appropriate:

- raw CSV files
- generated CSV outputs
- model pickle artifacts
- runtime JSONL audit logs
- local environment files
- virtual environments

This keeps the repository suitable for portfolio review while avoiding large files, secrets, and runtime artifacts.

## Limitations and Responsible Use

This project is a portfolio-grade analytical prototype, not a production credit approval engine.

Important limitations:

- The API expects model-ready engineered features.
- Raw application, bureau, and previous-application tables are not yet transformed through an API endpoint.
- The human review workflow is local JSONL-backed and not a production case-management system.
- Audit logs are local JSONL files, not a regulated compliance platform.
- LLM-assisted answers are optional decision support and must not be treated as automated approval or rejection.
- The Home Credit dataset contains anonymized and externally defined fields, so business interpretation should remain cautious.
- No real bank deployment, real customer decisioning, authentication, authorization, monitoring, or compliance controls are claimed.

## Future Enhancements

Suggested next steps:

- Add raw-to-feature API transformation support.
- Add batch scoring endpoint.
- Add stronger automated data quality reporting.
- Add warehouse-ready scoring and audit table design.
- Add a lightweight review dashboard or case workflow UI.
- Add authentication and authorization if moving beyond local prototype use.
- Add model monitoring and drift reporting.
- Expand documentation for data dictionary and API contracts.
- Add a production-style deployment plan without overstating current readiness.

## Portfolio Narrative

This project demonstrates how a credit risk model can be expanded into a broader decision-support system. It connects data engineering, feature design, model scoring, SHAP explainability, API delivery, audit traceability, human review workflow, SQL analytics, and optional LLM-assisted analyst support.

The result is a practical, interview-ready portfolio project for data technology, risk analytics, fintech analytics, and banking analytics roles.
