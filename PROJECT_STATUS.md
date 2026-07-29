# Project Status

## V4.4 Completion Status

V4.4 is complete.

The project has evolved from a basic Home Credit XGBoost credit risk model into an end-to-end credit risk decision-support system. It now combines feature engineering, model scoring, explainability, FastAPI inference, audit logging, human review workflow, RAG-style documentation retrieval, deterministic analyst Q&A, and optional LLM-assisted answer generation.

This remains a portfolio-grade local analytical prototype. It is not a production credit approval engine and does not claim real bank deployment.

## Current System Capabilities

Completed components:

- Data preprocessing and feature engineering from Home Credit source tables.
- XGBoost default risk scoring model.
- Risk score and risk band generation.
- Validation-only and full-portfolio risk band reporting.
- SHAP global and local explainability.
- FastAPI scoring endpoints.
- API input feature alignment.
- Missing and unexpected feature reporting.
- JSONL audit logging.
- Rule-based human review recommendation.
- Lightweight human review workflow:
  - review queue
  - review case detail
  - reviewer decision logging
- SQL analytics reports with DuckDB.
- Lightweight RAG-style agent memo generation.
- Single-turn analyst Q&A script.
- FastAPI `/ask-analyst` endpoint.
- Optional LLM-assisted answer generation for `/ask-analyst`.
- Deterministic fallback when LLM mode is disabled, unavailable, unconfigured, or fails.

## Tested V4.4 Behavior

V4.4 testing confirmed:

- `/ask-analyst` with `use_llm=false` returns deterministic answer fields.
- `/ask-analyst` with `use_llm=true` can return an `llm_assisted` answer.
- Successful LLM-assisted response was tested with `gpt-4o-mini`.
- Fallback behavior was tested when API key, quota, or model access failed.
- Deterministic structured fields remain available even when LLM mode is enabled.
- Request-level `llm_model` override is supported.
- LLM mode does not replace scoring, SHAP, audit, review, or deterministic answer logic.

## Project Evolution and Upgrade Timeline

This timeline focuses on the post-baseline upgrade phase. Earlier exploratory data analysis and baseline XGBoost modeling were completed before the project was migrated into a more reproducible, API-driven decision-support system.

| Phase | Milestone | Summary |
|---|---|---|
| Baseline Phase | Exploratory analysis and baseline model | Established the original Home Credit analysis workflow and baseline XGBoost modeling approach before the professionalization sprint. |
| Upgrade Phase 1 | Local-first modeling pipeline | Migrated the workflow into a reproducible local pipeline using `application_train.csv`, `bureau.csv`, and `previous_application.csv`. |
| Upgrade Phase 1 | Feature engineering expansion | Added previous-application features, bureau features, and application affordability ratios. |
| Upgrade Phase 1 | Model artifacts and metrics | Saved metrics, model pickle artifact, feature list, and risk scores. |
| Upgrade Phase 2 | Risk banding and validation reports | Added portfolio and validation-only risk band summaries, threshold analysis, and model evaluation outputs. |
| Upgrade Phase 2 | SQL analytics layer | Added DuckDB reports for portfolio risk, income type segmentation, and high-risk flag analysis. |
| Upgrade Phase 2 | SHAP explainability | Added global SHAP importance, summary plots, dependence plots, and local SHAP examples. |
| Upgrade Phase 3 | FastAPI scoring service | Added `/health`, `/predict`, and `/predict-with-explanation`. |
| Upgrade Phase 3 | Governance layer | Added input checks, audit JSONL logs, and rule-based human review recommendation. |
| Upgrade Phase 3 | Human review workflow | Added review queue, case detail, and reviewer decision logging. |
| Upgrade Phase 4 | RAG-style memo MVP | Added `src/agent_memo.py` for markdown credit risk review memo generation. |
| Upgrade Phase 4 | V4.2 analyst Q&A | Added deterministic single-turn Q&A through `src/agent_query.py`. |
| Upgrade Phase 4 | V4.3 `/ask-analyst` API | Exposed deterministic analyst Q&A through FastAPI. |
| Upgrade Phase 4 | V4.4 optional LLM mode | Added opt-in LLM-assisted answer generation with deterministic fallback. |

## Model and Feature Progress

Validation metric: ROC AUC.

| Stage | Feature Update | Validation AUC |
|---|---|---:|
| Initial local baseline | Local pipeline with initial bureau and previous-application features | 0.7553 |
| Batch 2A | Added previous-application amount features | 0.7576 |
| Batch 2B | Added previous-application time features | 0.7577 |
| Batch 3A | Added application affordability and exposure ratio features | 0.7645 |
| Batch 4A | Added bureau external credit history features | 0.7649 |

Interpretation:

- Application affordability ratios produced the strongest early performance lift.
- Bureau features improved business completeness by adding external credit burden and activity signals.
- SHAP results show strong contributions from external source scores, affordability ratios, bureau debt burden, and previous-application behavior.

## API and Governance Status

Current FastAPI endpoints:

| Endpoint | Status | Purpose |
|---|---|---|
| `GET /health` | Complete | Check service and artifact readiness. |
| `POST /predict` | Complete | Score model-ready features. |
| `POST /predict-with-explanation` | Complete | Score features and return local SHAP drivers, review recommendation, and audit id. |
| `GET /human-review/queue` | Complete | Return concise review queue overview. |
| `GET /human-review/{review_case_id}` | Complete | Return case detail, decision history, and linked audit context. |
| `POST /human-review/{review_case_id}/decision` | Complete | Append analyst review decision. |
| `POST /ask-analyst` | Complete | Answer analyst questions using deterministic and optional LLM-assisted modes. |

Runtime audit and review files:

- `outputs/api_logs/scoring_audit_log.jsonl`
- `outputs/api_logs/human_review_cases.jsonl`
- `outputs/api_logs/human_review_decisions.jsonl`

These are local runtime artifacts and are ignored by Git.

## Analyst Assistant Status

Completed analyst-support layers:

- `src/agent_memo.py`
  - Generates `outputs/agent_outputs/credit_risk_review_memo.md`.
  - Uses local scoring response JSON and retrieved project documentation snippets.

- `src/agent_query.py`
  - Supports deterministic single-turn analyst Q&A.
  - Can optionally load human review context by `review_case_id`.
  - Generates `outputs/agent_outputs/analyst_question_answer.md`.

- `POST /ask-analyst`
  - Exposes analyst Q&A through FastAPI.
  - Returns structured deterministic evidence fields.
  - Supports optional LLM-assisted answer generation.
  - Falls back to deterministic output when LLM mode is unavailable or fails.

## Documentation Status

Current documentation covers:

- API usage and endpoint examples.
- Data model and lineage.
- Data quality and governance.
- Data dictionary.
- API requirements specification.
- Feature expansion and migration planning.
- Weekly and project status summaries.

Important docs:

- `README.md`
- `API_USAGE.md`
- `docs/DATA_MODEL_AND_LINEAGE.md`
- `docs/DATA_QUALITY_AND_GOVERNANCE.md`
- `docs/DATA_DICTIONARY.md`
- `docs/API_REQUIREMENTS_SPEC.md`

## Responsible-Use Positioning

This project is a portfolio-grade decision-support system, not a production credit approval engine.

It is designed to demonstrate:

- credit risk analytics
- data technology practices
- explainable model scoring
- API design
- audit traceability
- human review support
- analyst-facing AI-assisted interpretation

It does not claim:

- real bank deployment
- automated credit approval or rejection
- production compliance readiness
- regulated audit controls
- authentication or authorization hardening
- production monitoring or model governance sign-off

LLM-assisted output is optional analyst decision support only. It must be interpreted together with deterministic scoring evidence, SHAP drivers, review context, and documented limitations.

## Optional and Future Work

Remaining enhancements:

- Add raw-to-feature API transformation support.
- Add batch scoring endpoint.
- Add stronger data quality summary reports.
- Add warehouse-ready scoring and audit schema.
- Add lightweight review dashboard or UI.
- Add authentication and authorization for deployed environments.
- Add model monitoring and drift reporting.
- Add CI/testing once environment setup is stable.
- Add production deployment plan and controls if the project moves beyond local prototype scope.

## Current Stable State

The current V4.4 repository demonstrates an end-to-end local credit risk decision-support workflow:

Raw Home Credit data -> feature engineering -> XGBoost scoring -> SHAP explainability -> FastAPI scoring -> audit logging -> human review workflow -> deterministic and optional LLM-assisted analyst Q&A.

The system is ready for portfolio demonstration and interview discussion for Data Analyst, Data Technology, Risk Analytics, FinTech Analytics, and Banking Analytics roles.
