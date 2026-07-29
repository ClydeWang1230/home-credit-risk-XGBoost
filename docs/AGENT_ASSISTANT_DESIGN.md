# Agent Assistant Design

## 1. Purpose

The analyst assistant layer helps turn model outputs into readable credit risk decision-support context. It connects scoring results, SHAP drivers, human review signals, audit identifiers, and local project documentation so an analyst can understand why a case may need closer review.

The current assistant milestone is V4.4. This is a lightweight portfolio implementation designed to demonstrate grounded analytics communication, governance awareness, deterministic fallback, optional LLM-assisted interpretation, and analyst workflow support rather than production-grade banking automation.

## 2. Evolution

### V4.0 Lightweight RAG Memo

V4.0 introduced a local memo generator in `src/agent_memo.py`. It reads a sample API scoring response, retrieves relevant snippets from project Markdown documentation, and writes a credit risk review memo to `outputs/agent_outputs/credit_risk_review_memo.md`.

### V4.2 Single-Turn Analyst Q&A

V4.2 added a deterministic single-turn question-answering layer. It uses local scoring evidence, SHAP driver previews, review context when available, and keyword-based document retrieval to answer analyst-style questions.

### V4.3 `/ask-analyst` FastAPI Endpoint

V4.3 exposed the analyst Q&A capability through FastAPI. The endpoint returns structured JSON fields suitable for Swagger testing, frontend consumption, and audit-friendly review. It includes detected intent, scoring evidence, driver previews, review context, retrieved snippets, warnings, and limitations.

### V4.4 LLM-Assisted Answer Generation

V4.4 added optional LLM-assisted answer generation to `/ask-analyst`. The deterministic response remains the default and the structured fields are still returned when LLM mode is enabled. If LLM configuration is missing or generation fails, the endpoint falls back to deterministic output.

## 3. Inputs Used by the Analyst Assistant

The assistant can use the following inputs:

- scoring response from `/predict-with-explanation`
- risk score and risk band
- high-risk flag and candidate threshold
- SHAP positive and negative risk drivers
- human review recommendation
- audit log id
- review case detail and reviewer decision history, if a `review_case_id` is provided
- retrieved project documentation snippets from files such as data dictionary, governance notes, lineage documentation, API usage notes, and SHAP explainability summaries

## 4. Deterministic Answer Path

The deterministic path is the default behavior. It detects the intent of the analyst question, extracts structured evidence from the scoring response and review context, retrieves relevant local documentation snippets, and builds a template-based answer.

This path is useful because it is predictable, local, explainable, and available without external services. It also provides stable structured fields for downstream UI or reporting use.

## 5. LLM-Assisted Answer Path

When `use_llm=true`, the assistant attempts to generate an additional analyst-style answer using the configured LLM provider. The prompt is grounded in the same structured context used by the deterministic path:

- user question
- detected intent
- scoring evidence
- SHAP driver preview
- review context
- retrieved documentation snippets
- responsible-use limitations

The LLM answer is additive. It does not replace deterministic fields such as `answer_summary`, `answer_sections`, `scoring_evidence`, or `retrieved_context`.

## 6. Fallback Behavior

LLM mode is optional. If the API key is missing, the model is unavailable, quota fails, the client package is not installed, or the LLM response is empty, the endpoint keeps working in deterministic mode.

Fallback responses include warnings so the user can see why LLM-assisted generation was not used. This keeps the assistant usable in local-first development and portfolio review settings without requiring secrets or external API access.

## 7. Why This Is Different From Simply Asking ChatGPT Directly

The analyst assistant is grounded in project-specific evidence instead of open-ended conversation. It uses the actual scoring response, model risk band, SHAP drivers, review recommendation, audit log id, and local documentation snippets.

This makes the answer more traceable and portfolio-relevant than a generic prompt. The deterministic fields also remain available for auditability, testing, and frontend integration even when an LLM answer is generated.

## 8. Limitations

- The assistant provides decision support, not automated credit approval or rejection.
- The current implementation is single-turn and does not maintain long-running analyst conversation memory.
- Retrieval is local and keyword-based, not a production semantic search or vector database.
- LLM mode depends on external API configuration and availability.
- The API expects model-ready engineered features; raw source table transformation is not handled by the analyst assistant.
- Human review records and audit logs are local JSONL artifacts, not production workflow infrastructure.

## 9. Future Enhancements

- Add richer review workflow states and dashboard integration.
- Add controlled multi-turn analyst context.
- Add raw-to-feature scoring support before exposing broader business-user inputs.
- Add a fuller data dictionary for model features and API outputs.
- Add automated data quality summaries to strengthen governance context.
- Evaluate lightweight semantic retrieval while preserving deterministic fallback.
- Add stricter prompt and response validation for any future production-like deployment.
