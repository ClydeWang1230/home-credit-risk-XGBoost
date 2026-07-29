# FastAPI Scoring API Usage

## Purpose

This API exposes the trained Home Credit XGBoost credit risk model through local FastAPI endpoints for scoring, explanation, governance support, human review workflow, and analyst Q&A.

The current API version is V4.4. It is designed as a portfolio-grade decision-support prototype that demonstrates model serving, input validation, local SHAP explanations, audit traceability, rule-based review recommendations, RAG-style retrieval, and optional LLM-assisted analyst Q&A. It is not an automated credit approval or rejection system.

## Start the API Locally

From the project root, start the API with:

```bash
uvicorn src.api:app --reload
```

If `uvicorn` is not directly available on the command line, use:

```bash
python -m uvicorn src.api:app --reload
```

The local API runs at:

```text
http://127.0.0.1:8000
```

Swagger UI is available at:

```text
http://127.0.0.1:8000/docs
```

## Endpoint Summary

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Checks API and model artifact readiness. |
| `POST` | `/predict` | Scores one model-ready applicant feature payload. |
| `POST` | `/predict-with-explanation` | Scores one applicant and returns local SHAP risk drivers, human review recommendation, and audit metadata. |
| `GET` | `/human-review/queue` | Returns the local analyst review queue. |
| `GET` | `/human-review/{review_case_id}` | Returns one review case, decision history, latest decision, and linked audit record. |
| `POST` | `/human-review/{review_case_id}/decision` | Appends an analyst decision for one review case. |
| `POST` | `/ask-analyst` | Answers one analyst question using scoring evidence, review context, retrieved documentation, and optional LLM assistance. |

## Scoring Endpoints

### `GET /health`

Checks whether the API service and model artifacts are loaded successfully.

Example:

```text
http://127.0.0.1:8000/health
```

Example response:

```json
{
  "status": "ok",
  "model_loaded": true,
  "feature_count": 131,
  "threshold": 0.15,
  "model_version": "xgboost_v1"
}
```

### `POST /predict`

Accepts applicant model features and returns a predicted credit risk score.

Request body example:

```json
{
  "features": {
    "AMT_CREDIT": 500000,
    "AMT_ANNUITY": 25000
  },
  "strict": false
}
```

`features` is a dictionary of model feature names and values. `strict=false` fills missing model features with `-999`; `strict=true` requires all 131 model features. Unexpected extra features are ignored and reported in the response.

Key response fields:

- `risk_score`
- `risk_band`
- `high_risk_flag_015`
- `threshold_used`
- `model_version`
- `missing_feature_count`
- `missing_features_preview`
- `unexpected_feature_count`
- `unexpected_features_preview`

### `POST /predict-with-explanation`

Accepts the same request body as `/predict`, returns the same scoring fields, and adds local applicant-level SHAP explanation drivers.

The endpoint also returns a rule-based human review recommendation, writes an audit-friendly JSONL log entry, and creates a lightweight human review case when review is required.

Key additional response fields:

- `top_positive_risk_drivers`: features pushing the prediction toward higher default risk
- `top_negative_risk_drivers`: features pushing the prediction toward lower default risk
- `explanation_note`
- `human_review_recommendation`
- `audit_log_id`
- `human_review_case`, when a review case is created

Positive SHAP values increase the model output toward higher predicted default risk. Negative SHAP values decrease the model output toward lower predicted default risk.

Audit and review logs are stored locally:

```text
outputs/api_logs/scoring_audit_log.jsonl
outputs/api_logs/human_review_cases.jsonl
outputs/api_logs/human_review_decisions.jsonl
```

## Human Review Workflow

### `GET /human-review/queue`

Returns a concise local review queue for cases created by `/predict-with-explanation`.

The queue is designed as a list view. Each item includes case identifiers, status fields, risk score, risk band, review priority, audit log id, and latest decision summary fields. Cases are sorted by `created_at_utc` descending so newer cases appear first.

Example:

```text
http://127.0.0.1:8000/human-review/queue
```

Optional status filter:

```text
http://127.0.0.1:8000/human-review/queue?status=pending_review
```

### `GET /human-review/{review_case_id}`

Returns detail for one human review case.

The response includes:

- `review_case_id`
- `review_case`
- `latest_decision`
- `decision_history`
- `linked_audit_log`

`original_case_status` is the status when the case entered the local review queue. `effective_review_status` reflects the latest analyst decision status when one exists; otherwise it falls back to the original case status.

Example:

```text
http://127.0.0.1:8000/human-review/<review_case_id>
```

### `POST /human-review/{review_case_id}/decision`

Records an analyst decision for a human review case. Decisions are appended to a local JSONL file.

Request body example:

```json
{
  "review_decision": "manual_review_completed",
  "reviewer": "analyst_1",
  "notes": "Reviewed high-risk drivers and confirmed case should remain in enhanced review.",
  "status": "review_completed"
}
```

This workflow supports local analyst review traceability. It is not a production case-management or approval system.

## Analyst Q&A Endpoint

### `POST /ask-analyst`

Answers one analyst-style question about an existing scoring response, optional human review case, and local project documentation. The endpoint does not run a new model prediction.

The endpoint supports two answer modes:

- deterministic mode, which uses local rules, retrieved snippets, and structured templates
- LLM-assisted mode, which adds an optional grounded natural-language answer while preserving deterministic structured output

`include_markdown_answer` defaults to `false` because API JSON is meant for structured system and frontend consumption. `markdown_answer` is optional and useful when a UI or report export wants a preformatted Markdown answer.

### `/ask-analyst` Request Fields

| Field | Type | Description |
|---|---|---|
| `question` | string | Required analyst question. |
| `scoring_response` | object or null | Optional copied response from `/predict-with-explanation`. If omitted, the endpoint may use available local sample response data for development testing. |
| `review_case_id` | string or null | Optional local review case id used to load case detail, decision history, and linked audit context. |
| `max_snippets` | integer | Maximum number of retrieved documentation snippets to include. |
| `include_markdown_answer` | boolean | Whether to include `markdown_answer`; defaults to `false`. |
| `use_llm` | boolean | Whether to attempt optional LLM-assisted generation; defaults to `false`. |
| `llm_model` | string or null | Optional per-request LLM model override, such as `gpt-4o-mini`. |
| `llm_temperature` | number | LLM temperature for answer generation; defaults to a low analyst-style value. |
| `llm_max_context_snippets` | integer | Maximum retrieved snippets passed into the LLM prompt. |
| `llm_style` | string | Optional style hint, defaulting to an analyst-oriented style. |

### `/ask-analyst` Response Fields

| Field | Description |
|---|---|
| `question` | The submitted analyst question. |
| `detected_intent` | Deterministic intent classification, such as feature definition, risk drivers, governance traceability, or review status. |
| `answer_summary` | Short deterministic summary. |
| `answer_sections` | Structured deterministic answer sections for frontend or analyst review. |
| `markdown_answer` | Optional Markdown answer when requested. |
| `scoring_response_source` | Source used for scoring evidence, such as request payload or local sample response. |
| `scoring_evidence` | Key score, threshold, model, audit, and review recommendation fields. |
| `driver_preview` | Compact positive and negative SHAP driver previews. |
| `review_context_loaded` | Whether review case context was successfully loaded. |
| `review_context_summary` | Review case status, effective status, latest decision, decision count, and linked audit availability. |
| `retrieved_context` | Local documentation snippets used as grounding context. |
| `warnings` | Non-fatal warnings, such as missing optional context. |
| `limitations` | Decision-support and interpretation limitations. |
| `answer_mode` | `deterministic` or `llm_assisted`. |
| `llm_enabled` | Whether LLM generation succeeded for this response. |
| `llm_answer` | Optional LLM-generated analyst answer, or `null` when disabled or unavailable. |
| `llm_model` | Actual LLM model attempted or used, when applicable. |
| `llm_warnings` | LLM-specific warnings and fallback reasons. |

## `/ask-analyst` Example Requests

### A. Deterministic Analyst Q&A

```json
{
  "question": "Why is this applicant high risk?",
  "max_snippets": 6,
  "include_markdown_answer": false,
  "use_llm": false
}
```

Expected behavior:

- `answer_mode` is `deterministic`
- `llm_enabled` is `false`
- `llm_answer` is `null`
- deterministic fields such as `answer_summary`, `answer_sections`, `scoring_evidence`, and `retrieved_context` are returned

### B. LLM-Assisted Analyst Q&A

```json
{
  "question": "Why is this applicant high risk?",
  "max_snippets": 6,
  "include_markdown_answer": false,
  "use_llm": true,
  "llm_model": "gpt-4o-mini"
}
```

Expected behavior when LLM configuration is available:

- `answer_mode` is `llm_assisted`
- `llm_enabled` is `true`
- `llm_answer` contains a grounded analyst-style response
- deterministic structured fields are still returned for auditability and fallback

### C. Review-Status Question

```json
{
  "question": "Has this case been reviewed?",
  "review_case_id": "example-review-case-id",
  "max_snippets": 6,
  "include_markdown_answer": false,
  "use_llm": false
}
```

Expected behavior:

- `review_context_loaded` is `true` when the case exists
- `review_context_summary` shows original case status, effective review status, latest decision, decision history count, and linked audit availability

### D. LLM Fallback Example

```json
{
  "question": "Has this case been reviewed and what should the analyst watch?",
  "review_case_id": "example-review-case-id",
  "max_snippets": 6,
  "include_markdown_answer": false,
  "use_llm": true,
  "llm_model": "gpt-4o-mini"
}
```

If the API key is missing, quota is unavailable, model access fails, or the LLM package is not installed, the endpoint should still return the deterministic answer.

Expected fallback behavior:

- `answer_mode` is `deterministic`
- `llm_enabled` is `false`
- `llm_answer` is `null`
- `llm_warnings` explains why LLM generation was not used

## LLM Configuration

LLM mode uses environment variables. No API key or secret should be committed to the repository.

```text
OPENAI_API_KEY
OPENAI_MODEL
```

`llm_model` can override `OPENAI_MODEL` for a single `/ask-analyst` request. If no model override is provided, the endpoint uses the configured default model behavior in the application code.

The LLM answer is grounded in:

- scoring evidence
- SHAP driver previews
- human review context, when provided
- retrieved project documentation snippets

The LLM should not invent applicant facts, lending policies, thresholds, or approval decisions.

## Complete Sample Payloads

Complete prediction payload:

```text
outputs/api_samples/sample_predict_payload.json
```

Payload metadata:

```text
outputs/api_samples/sample_predict_payload_metadata.json
```

Sample explanation or governance responses may also be available under:

```text
outputs/api_samples/
```

These files are intended for developer testing and portfolio demonstration.

## curl Examples

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Prediction request:

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"features":{"AMT_CREDIT":500000,"AMT_ANNUITY":25000},"strict":false}'
```

Prediction with local SHAP explanation:

```bash
curl -X POST "http://127.0.0.1:8000/predict-with-explanation" \
  -H "Content-Type: application/json" \
  -d '{"features":{"AMT_CREDIT":500000,"AMT_ANNUITY":25000},"strict":false}'
```

View pending review cases:

```bash
curl "http://127.0.0.1:8000/human-review/queue?status=pending_review"
```

Ask an analyst question:

```bash
curl -X POST "http://127.0.0.1:8000/ask-analyst" \
  -H "Content-Type: application/json" \
  -d '{"question":"Why is this applicant high risk?","include_markdown_answer":false,"use_llm":false}'
```

On Windows PowerShell, `curl.exe` may be safer than `curl` because `curl` can be aliased to `Invoke-WebRequest`.

## Responsible Use

- API outputs are analyst decision support.
- The system is not an automated credit approval or rejection engine.
- Human review recommendations are rule-based triage signals, not final decisions.
- LLM-assisted answers should remain grounded in scoring evidence, SHAP drivers, retrieved documentation, and review context.
- The current implementation is a local analytical prototype, not a production banking platform.

## Current Limitations

- The API expects model-ready engineered features.
- It does not yet transform raw application, bureau, or previous application records into model features at request time.
- Audit logs and human review records are local JSONL artifacts, not a production database.
- The analyst assistant is single-turn and local-context grounded.
- LLM mode is optional and depends on external API availability when enabled.

## Future Enhancements

- Add raw-to-feature scoring support.
- Add batch scoring endpoints.
- Add authentication and access control for deployed environments.
- Add stronger monitoring and production logging patterns.
- Add richer analyst workflow screens or dashboard integration.
- Expand documentation-grounded analyst Q&A with controlled multi-turn context.
