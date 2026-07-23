import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RESPONSE_CANDIDATES = [
    PROJECT_ROOT / "outputs" / "api_samples" / "sample_predict_with_governance_response.json",
    PROJECT_ROOT / "outputs" / "api_samples" / "sample_predict_with_explanation_response.json",
    PROJECT_ROOT / "outputs" / "api_samples" / "v3-sample_predict_with_governance_response.json",
    PROJECT_ROOT / "outputs" / "api_samples" / "v2-sample_predict_with_explanation_response.json",
]

KNOWLEDGE_DOC_PATHS = [
    PROJECT_ROOT / "docs" / "DATA_MODEL_AND_LINEAGE.md",
    PROJECT_ROOT / "docs" / "DATA_QUALITY_AND_GOVERNANCE.md",
    PROJECT_ROOT / "docs" / "DATA_DICTIONARY.md",
    PROJECT_ROOT / "API_USAGE.md",
    PROJECT_ROOT / "SHAP_EXPLAINABILITY_SUMMARY.md",
]

OUTPUT_PATH = PROJECT_ROOT / "outputs" / "agent_outputs" / "credit_risk_review_memo.md"


FEATURE_INTERPRETATIONS = {
    "EXT_SOURCE_1": "External score signal from the original dataset. Higher values generally reduce modeled default risk, but the internal score composition is not disclosed.",
    "EXT_SOURCE_2": "External score signal from the original dataset. Higher values generally reduce modeled default risk, but the internal score composition is not disclosed.",
    "EXT_SOURCE_3": "External score signal from the original dataset. Higher values generally reduce modeled default risk, but the internal score composition is not disclosed.",
    "n_active_bureau_credits": "Number of active external bureau credit records, capturing current external credit activity.",
    "prev_refusal_rate": "Share of prior applications that were refused, capturing historical rejection behavior.",
    "credit_goods_ratio": "Credit amount relative to goods price, approximating financing coverage and borrower self-funding context.",
    "credit_annuity_ratio": "Credit amount relative to scheduled repayment amount, approximating repayment structure pressure.",
    "credit_income_ratio": "Credit amount relative to borrower income, capturing loan-to-income pressure.",
    "bureau_debt_credit_ratio": "External bureau debt relative to external credit amount, capturing external debt burden.",
    "DAYS_BIRTH": "Applicant age represented as relative days in the original dataset.",
    "DAYS_EMPLOYED": "Employment duration represented as relative days; the special value 365243 should not be interpreted literally.",
    "max_credit_prev": "Maximum previous credit amount, capturing largest historical credit exposure.",
    "avg_credit_prev": "Average previous credit amount, summarizing typical prior credit size.",
    "avg_credit_sum": "Average external bureau credit amount, summarizing typical external credit exposure.",
}


def load_sample_response():
    for path in RESPONSE_CANDIDATES:
        if path.exists():
            with path.open("r", encoding="utf-8") as file:
                return json.load(file), path

    searched_paths = "\n".join(str(path) for path in RESPONSE_CANDIDATES)
    raise FileNotFoundError(
        "No sample API response JSON was found. Searched:\n" + searched_paths
    )


def load_knowledge_documents():
    documents = []
    for path in KNOWLEDGE_DOC_PATHS:
        if path.exists():
            documents.append(
                {
                    "path": path,
                    "text": path.read_text(encoding="utf-8"),
                }
            )
    return documents


def split_markdown_into_snippets(text):
    sections = re.split(r"(?m)(?=^#{1,3}\s+)", text)
    snippets = []

    for section in sections:
        section = section.strip()
        if not section:
            continue

        if len(section) <= 900:
            snippets.append(section)
            continue

        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", section) if part.strip()]
        snippets.extend(paragraphs)

    return snippets


def build_retrieval_keywords(scoring_response):
    keywords = {
        "risk_score",
        "risk_band",
        "SHAP",
        "top_positive_risk_drivers",
        "top_negative_risk_drivers",
        "human_review_recommendation",
        "audit_log_id",
        "missing_feature_count",
        "unexpected_feature_count",
        "sentinel",
        "model_version",
        "threshold",
    }

    for driver_group in ("top_positive_risk_drivers", "top_negative_risk_drivers"):
        for driver in scoring_response.get(driver_group, []) or []:
            feature = driver.get("feature")
            if feature:
                keywords.add(str(feature))

    risk_band = scoring_response.get("risk_band")
    if risk_band:
        keywords.update(str(risk_band).replace("-", " ").split())

    return keywords


def retrieve_relevant_snippets(documents, scoring_response, max_snippets=6):
    keywords = build_retrieval_keywords(scoring_response)
    scored_snippets = []

    for document in documents:
        for snippet in split_markdown_into_snippets(document["text"]):
            snippet_lower = snippet.lower()
            matched_keywords = [
                keyword for keyword in keywords if str(keyword).lower() in snippet_lower
            ]

            if matched_keywords:
                scored_snippets.append(
                    {
                        "score": len(set(matched_keywords)),
                        "source": document["path"].relative_to(PROJECT_ROOT),
                        "text": snippet,
                    }
                )

    scored_snippets.sort(key=lambda item: item["score"], reverse=True)

    selected = []
    seen_text = set()
    for item in scored_snippets:
        compact_text = re.sub(r"\s+", " ", item["text"]).strip()
        if compact_text in seen_text:
            continue
        seen_text.add(compact_text)
        selected.append(item)
        if len(selected) >= max_snippets:
            break

    return selected


def format_value(value):
    if value is None:
        return "not available"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def driver_interpretation(driver):
    feature = driver.get("feature", "Unknown feature")
    value_status = driver.get("value_status", "actual_value")

    if value_status == "sentinel_missing":
        return "This contribution reflects missing, unavailable, or no-history information rather than a literal economic value."
    if value_status == "special_encoded_value":
        return "This contribution reflects a dataset-specific special encoded value rather than a literal business value."

    return FEATURE_INTERPRETATIONS.get(
        feature,
        "This feature is a model input signal. Its local SHAP value indicates how it affected this applicant's predicted risk.",
    )


def format_driver_lines(drivers):
    if not drivers:
        return "- No SHAP drivers were available in the scoring response."

    lines = []
    for driver in drivers:
        feature = driver.get("feature", "Unknown feature")
        value = format_value(driver.get("feature_value"))
        value_status = driver.get("value_status", "not_available")
        shap_value = format_value(driver.get("shap_value"))
        interpretation = driver_interpretation(driver)

        lines.append(
            f"- `{feature}`: value `{value}`, value status `{value_status}`, "
            f"SHAP `{shap_value}`. {interpretation}"
        )
    return "\n".join(lines)


def build_executive_summary(scoring_response):
    risk_score = scoring_response.get("risk_score")
    risk_band = scoring_response.get("risk_band", "Unknown")
    high_risk_flag = scoring_response.get("high_risk_flag_015", "not available")
    recommendation = scoring_response.get("human_review_recommendation", {}) or {}
    review_required = recommendation.get("review_required", "not available")
    review_priority = recommendation.get("review_priority", "not available")

    return (
        f"The applicant received a risk score of `{format_value(risk_score)}` and was assigned to "
        f"`{risk_band}`. The high-risk flag is `{high_risk_flag}`. The rule-based review "
        f"recommendation is review_required=`{review_required}` with priority `{review_priority}`."
    )


def build_analyst_notes(scoring_response):
    notes = []
    risk_score = scoring_response.get("risk_score")
    threshold = scoring_response.get("threshold_used", 0.15)
    positive_drivers = scoring_response.get("top_positive_risk_drivers", []) or []
    negative_drivers = scoring_response.get("top_negative_risk_drivers", []) or []

    if isinstance(risk_score, (int, float)) and isinstance(threshold, (int, float)):
        if risk_score >= threshold:
            notes.append(
                "The applicant is above the candidate high-risk threshold, so an analyst may want to review affordability, external credit history, and prior application behavior before taking action."
            )
        elif abs(risk_score - threshold) <= 0.02:
            notes.append(
                "The applicant is close to the candidate threshold, so the case may benefit from additional review if operational capacity allows."
            )

    if positive_drivers:
        top_features = ", ".join(
            f"`{driver.get('feature')}`" for driver in positive_drivers[:3] if driver.get("feature")
        )
        if top_features:
            notes.append(f"The strongest risk-increasing signals to review are {top_features}.")

    if positive_drivers and negative_drivers:
        notes.append(
            "Both risk-increasing and risk-reducing SHAP signals are present, so the memo should be interpreted as decision support rather than a single deterministic decision."
        )

    special_value_drivers = [
        driver
        for driver in positive_drivers + negative_drivers
        if driver.get("value_status") in {"sentinel_missing", "special_encoded_value"}
    ]
    if special_value_drivers:
        notes.append(
            "Some local drivers contain sentinel missing or special encoded values, so those values should be interpreted as data signals rather than literal business quantities."
        )

    if scoring_response.get("missing_feature_count", 0) or scoring_response.get(
        "unexpected_feature_count", 0
    ):
        notes.append(
            "Input quality checks reported missing or unexpected fields. Review feature mapping before relying on the score."
        )

    if not notes:
        notes.append(
            "No major data quality or governance issue is apparent from the available scoring response fields."
        )

    return "\n\n".join(notes)


def format_list(values):
    if not values:
        return "  - None reported."
    return "\n".join(f"  - `{value}`" for value in values)


def format_review_reasons(reasons):
    if not reasons:
        return "- No review reasons were provided."
    return "\n".join(f"- {reason}" for reason in reasons)


def format_retrieved_context(snippets):
    if not snippets:
        return "No matching project documentation snippets were found."

    lines = []
    for item in snippets:
        text = re.sub(r"\s+", " ", item["text"]).strip()
        if len(text) > 700:
            text = text[:697].rstrip() + "..."
        lines.append(f"- Source `{item['source']}`: {text}")
    return "\n".join(lines)


def generate_credit_risk_review_memo(scoring_response, snippets):
    recommendation = scoring_response.get("human_review_recommendation", {}) or {}

    memo = f"""# Credit Risk Review Memo

## 1. Executive Summary

{build_executive_summary(scoring_response)}

## 2. Model Scoring Result

- `risk_score`: `{format_value(scoring_response.get("risk_score"))}`
- `risk_band`: `{scoring_response.get("risk_band", "Unknown")}`
- `high_risk_flag_015`: `{scoring_response.get("high_risk_flag_015", "not available")}`
- `threshold_used`: `{format_value(scoring_response.get("threshold_used"))}`
- `model_version`: `{scoring_response.get("model_version", "not available")}`

## 3. Key Risk-Increasing Drivers

{format_driver_lines(scoring_response.get("top_positive_risk_drivers", []) or [])}

## 4. Key Risk-Reducing Drivers

{format_driver_lines(scoring_response.get("top_negative_risk_drivers", []) or [])}

## 5. Human Review Recommendation

- `review_required`: `{recommendation.get("review_required", "not available")}`
- `review_priority`: `{recommendation.get("review_priority", "not available")}`

Review reasons:

{format_review_reasons(recommendation.get("review_reasons", []) or [])}

This recommendation is rule-based decision support. It is not automated approval or rejection and should not replace analyst judgment.

## 6. Data Quality and Input Checks

- `missing_feature_count`: `{scoring_response.get("missing_feature_count", "not available")}`
- `missing_features_preview`:
{format_list(scoring_response.get("missing_features_preview", []) or [])}
- `unexpected_feature_count`: `{scoring_response.get("unexpected_feature_count", "not available")}`
- `unexpected_features_preview`:
{format_list(scoring_response.get("unexpected_features_preview", []) or [])}

## 7. Governance and Traceability

- `audit_log_id`: `{scoring_response.get("audit_log_id", "not available")}`
- `model_version`: `{scoring_response.get("model_version", "not available")}`
- `threshold_used`: `{format_value(scoring_response.get("threshold_used"))}`

The audit log id links this scoring event to traceable model output, local explanation signals, and the rule-based review recommendation.

## 8. Retrieved Project Context

{format_retrieved_context(snippets)}

## 9. Analyst Notes

{build_analyst_notes(scoring_response)}
"""
    return memo


def build_credit_risk_review_memo():
    scoring_response, response_path = load_sample_response()
    documents = load_knowledge_documents()
    snippets = retrieve_relevant_snippets(documents, scoring_response)
    print("\nRetrieved snippets preview:")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    memo = generate_credit_risk_review_memo(scoring_response, snippets)
    OUTPUT_PATH.write_text(memo, encoding="utf-8")

    print(f"Loaded API response from: {response_path}")
    print(f"Loaded project docs: {len(documents)}")
    print(f"Retrieved snippets: {len(snippets)}")
    print(f"Credit risk review memo saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_credit_risk_review_memo()
