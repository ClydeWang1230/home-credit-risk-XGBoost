import argparse
import json
import re
from pathlib import Path

from agent_memo import (
    FEATURE_INTERPRETATIONS,
    PROJECT_ROOT,
    format_retrieved_context,
    format_value,
    load_knowledge_documents,
    load_sample_response,
    split_markdown_into_snippets,
)


DEFAULT_OUTPUT_PATH = (
    PROJECT_ROOT / "outputs" / "agent_outputs" / "analyst_question_answer.md"
)
API_LOG_DIR = PROJECT_ROOT / "outputs" / "api_logs"
HUMAN_REVIEW_CASE_LOG_PATH = API_LOG_DIR / "human_review_cases.jsonl"
HUMAN_REVIEW_DECISION_LOG_PATH = API_LOG_DIR / "human_review_decisions.jsonl"
SCORING_AUDIT_LOG_PATH = API_LOG_DIR / "scoring_audit_log.jsonl"


def read_jsonl(path):  #从path里面读file, 删掉空白变成line，line添加入列表records,返回records
    if not path.exists():
        return []

    records = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def load_response_from_path(response_path):
    path = Path(response_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path  #路径变为绝对路径(如不是）

    with path.open("r", encoding="utf-8") as file:
        return json.load(file), path


def get_latest_decision(decision_history):
    if not decision_history:
        return None
    return decision_history[-1]


def find_linked_audit_log(audit_log_id):
    if not audit_log_id:
        return None

    matching_audit_logs = [
        audit_log
        for audit_log in read_jsonl(SCORING_AUDIT_LOG_PATH)
        if audit_log.get("audit_log_id") == audit_log_id
    ]
    if not matching_audit_logs:
        return None
    return matching_audit_logs[-1]


def load_review_case_detail(review_case_id):
    matching_cases = [
        review_case
        for review_case in read_jsonl(HUMAN_REVIEW_CASE_LOG_PATH)
        if review_case.get("review_case_id") == review_case_id
    ]
    if not matching_cases:
        return {
            "review_case_id": review_case_id,
            "review_case": None,
            "latest_decision": None,
            "decision_history": [],
            "linked_audit_log": None,
            "not_found": True,
        }

    review_case = matching_cases[-1]
    decision_history = [
        decision
        for decision in read_jsonl(HUMAN_REVIEW_DECISION_LOG_PATH)
        if decision.get("review_case_id") == review_case_id
    ]

    return {
        "review_case_id": review_case_id,
        "review_case": review_case,
        "latest_decision": get_latest_decision(decision_history),
        "decision_history": decision_history,
        "linked_audit_log": find_linked_audit_log(review_case.get("audit_log_id")),
        "not_found": False,
    }


def get_scoring_response_keywords(scoring_response): #scoring response is a big dictionary that analyst uploads
    keywords = {
        "risk_score",
        "risk_band",
        "threshold",
        "SHAP",
        "top_positive_risk_drivers",
        "top_negative_risk_drivers",
        "human_review_recommendation",
        "review_required",
        "review_priority",
        "review_reasons",
        "audit_log_id",
        "model_version",
        "missing_feature_count",
        "unexpected_feature_count",
        "sentinel",
        "review_case_id",
        "latest_decision",
        "decision_history",
        "linked_audit_log",
        "analyst decision",
    }

    for driver_group in ("top_positive_risk_drivers", "top_negative_risk_drivers"):
        for driver in scoring_response.get(driver_group, []) or []:
            feature = driver.get("feature")
            if feature:
                keywords.add(str(feature))

    return keywords


def build_question_keywords(question, scoring_response, review_context=None):
    question_tokens = {
        token
        for token in re.findall(r"[A-Za-z0-9_]+", question)
        if len(token) >= 3
    }
    keywords = get_scoring_response_keywords(scoring_response)
    keywords.update(question_tokens)

    if review_context:
        keywords.update(
            {
                "review_case",
                "review_case_id",
                "latest_decision",
                "decision_history",
                "linked_audit_log",
                "reviewer",
                "notes",
            }
        )

    return keywords


def retrieve_question_snippets(
    documents,
    question,
    scoring_response,
    review_context=None,
    max_snippets=6,
):
    keywords = build_question_keywords(question, scoring_response, review_context)
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


def all_driver_features(scoring_response):
    features = []
    for driver_group in ("top_positive_risk_drivers", "top_negative_risk_drivers"):
        for driver in scoring_response.get(driver_group, []) or []:
            feature = driver.get("feature")
            if feature:
                features.append(feature)
    return features


def detect_feature_in_question(question, scoring_response):
    question_lower = question.lower()
    for feature in all_driver_features(scoring_response):
        if feature.lower() in question_lower:
            return feature
    return None


def classify_question_intent(question, scoring_response=None):
    question_lower = question.lower()

    if "why" in question_lower and "high risk" in question_lower:
        return "high_risk_reason"
    if any(word in question_lower for word in ["reviewed", "latest decision", "analyst decision", "status"]):
        return "review_status"
    if any(word in question_lower for word in ["review required", "human review", "recommended for review"]):
        return "human_review"
    if any(word in question_lower for word in ["missing", "unexpected", "quality", "sentinel"]):
        return "data_quality"
    if any(word in question_lower for word in ["audit", "trace", "model version", "threshold", "linked audit"]):
        return "governance_traceability"
    if any(word in question_lower for word in ["reduce", "negative", "risk reducing"]):
        return "risk_reducing_factors"
    if any(word in question_lower for word in ["driver", "shap", "contribute"]):
        return "risk_drivers"
    if scoring_response and detect_feature_in_question(question, scoring_response):
        return "feature_definition"

    return "general_case_review"


def format_driver_summary(drivers, limit=None):
    drivers = drivers or []
    if limit:
        drivers = drivers[:limit]
    if not drivers:
        return "- No local SHAP drivers were available."

    lines = []
    for driver in drivers:
        lines.append(
            "- `{feature}`: value `{value}`, SHAP `{shap}`, value_status `{status}`.".format(
                feature=driver.get("feature", "unknown"),
                value=format_value(driver.get("feature_value")),
                shap=format_value(driver.get("shap_value")),
                status=driver.get("value_status", "not_available"),
            )
        )
    return "\n".join(lines)


def find_driver(feature, scoring_response):
    for driver_group in ("top_positive_risk_drivers", "top_negative_risk_drivers"):
        for driver in scoring_response.get(driver_group, []) or []:
            if driver.get("feature") == feature:
                return driver, driver_group
    return None, None


def format_review_reasons(recommendation):
    reasons = (recommendation or {}).get("review_reasons", []) or []
    if not reasons:
        return "- No review reasons were provided."
    return "\n".join(f"- {reason}" for reason in reasons)


def sentinel_driver_summary(scoring_response):
    special_drivers = []
    for driver_group in ("top_positive_risk_drivers", "top_negative_risk_drivers"):
        for driver in scoring_response.get(driver_group, []) or []:
            if driver.get("value_status") in {"sentinel_missing", "special_encoded_value"}:
                special_drivers.append(driver)
    return format_driver_summary(special_drivers)


def build_short_answer(intent, question, scoring_response, review_context=None):
    recommendation = scoring_response.get("human_review_recommendation", {}) or {}
    risk_score = scoring_response.get("risk_score")
    threshold = scoring_response.get("threshold_used")
    risk_band = scoring_response.get("risk_band", "Unknown")

    if intent == "high_risk_reason":
        top_features = ", ".join(
            driver.get("feature", "unknown")
            for driver in (scoring_response.get("top_positive_risk_drivers", []) or [])[:3]
        )
        return (
            f"This applicant is high risk because the risk score `{format_value(risk_score)}` "
            f"is above the threshold `{format_value(threshold)}` and the applicant is in "
            f"`{risk_band}`. The strongest positive SHAP risk drivers are {top_features or 'not available'}."
        )

    if intent == "risk_drivers":
        return (
            "The main risk drivers are the local SHAP features. Positive SHAP values increase "
            "predicted default risk, while negative SHAP values reduce predicted default risk."
        )

    if intent == "feature_definition":
        feature = detect_feature_in_question(question, scoring_response)
        driver, _ = find_driver(feature, scoring_response) if feature else (None, None)
        interpretation = FEATURE_INTERPRETATIONS.get(
            feature,
            "This feature is a model input signal. Its full business definition may be limited by the source dataset.",
        )
        if driver:
            return (
                f"`{feature}` appears in this applicant's local SHAP drivers with value "
                f"`{format_value(driver.get('feature_value'))}` and SHAP "
                f"`{format_value(driver.get('shap_value'))}`. {interpretation}"
            )
        return f"`{feature}` was detected in the question. {interpretation}"

    if intent == "human_review":
        return (
            "The human review recommendation is rule-based decision support. "
            f"review_required=`{recommendation.get('review_required', 'not available')}` and "
            f"review_priority=`{recommendation.get('review_priority', 'not available')}`."
        )

    if intent == "review_status":
        if not review_context:
            return (
                "No review case id was provided, so review status cannot be checked from the local JSONL workflow."
            )
        if review_context.get("not_found"):
            return "The requested review case id was not found in the local review case log."
        latest_decision = review_context.get("latest_decision")
        if not latest_decision:
            return "The review case exists, but no analyst decision has been recorded yet."
        return (
            f"The latest analyst decision is `{latest_decision.get('review_decision')}` "
            f"with status `{latest_decision.get('status')}`."
        )

    if intent == "data_quality":
        return (
            f"The scoring response reports missing_feature_count=`{scoring_response.get('missing_feature_count', 'not available')}` "
            f"and unexpected_feature_count=`{scoring_response.get('unexpected_feature_count', 'not available')}`. "
            "Sentinel or special encoded local drivers should be interpreted as data signals, not literal values."
        )

    if intent == "governance_traceability":
        return (
            f"The audit_log_id `{scoring_response.get('audit_log_id', 'not available')}`, "
            f"model_version `{scoring_response.get('model_version', 'not available')}`, and "
            f"threshold_used `{format_value(threshold)}` support traceability across scoring, explanation, and review workflow outputs."
        )

    if intent == "risk_reducing_factors":
        return (
            "The risk-reducing factors are the local negative SHAP drivers. These features reduced the model output toward lower predicted default risk for this applicant."
        )

    return (
        f"The applicant has risk_score `{format_value(risk_score)}`, risk_band `{risk_band}`, "
        f"and review priority `{recommendation.get('review_priority', 'not available')}`. "
        "The answer should be treated as analyst decision support."
    )


def build_evidence_section(intent, scoring_response):
    recommendation = scoring_response.get("human_review_recommendation", {}) or {}
    lines = [
        f"- `risk_score`: `{format_value(scoring_response.get('risk_score'))}`",
        f"- `risk_band`: `{scoring_response.get('risk_band', 'Unknown')}`",
        f"- `high_risk_flag_015`: `{scoring_response.get('high_risk_flag_015', 'not available')}`",
        f"- `threshold_used`: `{format_value(scoring_response.get('threshold_used'))}`",
        f"- `model_version`: `{scoring_response.get('model_version', 'not available')}`",
        f"- `audit_log_id`: `{scoring_response.get('audit_log_id', 'not available')}`",
        f"- `missing_feature_count`: `{scoring_response.get('missing_feature_count', 'not available')}`",
        f"- `unexpected_feature_count`: `{scoring_response.get('unexpected_feature_count', 'not available')}`",
        f"- `review_required`: `{recommendation.get('review_required', 'not available')}`",
        f"- `review_priority`: `{recommendation.get('review_priority', 'not available')}`",
    ]

    if intent in {"high_risk_reason", "risk_drivers", "feature_definition", "general_case_review"}:
        lines.append("\nTop positive risk drivers:\n")
        lines.append(format_driver_summary(scoring_response.get("top_positive_risk_drivers", []), limit=5))

    if intent in {"risk_drivers", "risk_reducing_factors", "general_case_review"}:
        lines.append("\nTop negative risk drivers:\n")
        lines.append(format_driver_summary(scoring_response.get("top_negative_risk_drivers", []), limit=5))

    if intent == "human_review":
        lines.append("\nReview reasons:\n")
        lines.append(format_review_reasons(recommendation))

    if intent == "data_quality":
        lines.extend(
            [
                f"- `missing_features_preview`: `{scoring_response.get('missing_features_preview', [])}`",
                f"- `unexpected_features_preview`: `{scoring_response.get('unexpected_features_preview', [])}`",
                "\nSentinel or special encoded local drivers:\n",
                sentinel_driver_summary(scoring_response),
            ]
        )

    return "\n".join(lines)


def format_human_review_context(review_context):
    if not review_context:
        return "No review case id was provided, so local review workflow context was not loaded."

    if review_context.get("not_found"):
        return (
            f"Review case `{review_context.get('review_case_id')}` was not found in the local review case log."
        )

    review_case = review_context.get("review_case") or {}
    latest_decision = review_context.get("latest_decision") or {}
    decision_history = review_context.get("decision_history", []) or []

    return "\n".join(
        [
            f"- `review_case_id`: `{review_context.get('review_case_id')}`",
            f"- `review case status`: `{review_case.get('status', 'not available')}`",
            f"- `latest_review_status`: `{latest_decision.get('status') if latest_decision else None}`",
            f"- `latest_review_decision`: `{latest_decision.get('review_decision') if latest_decision else None}`",
            f"- `latest_review_updated_at`: `{latest_decision.get('updated_at_utc') if latest_decision else None}`",
            f"- `reviewer`: `{latest_decision.get('reviewer') if latest_decision else None}`",
            f"- `notes`: `{latest_decision.get('notes') if latest_decision else None}`",
            f"- `decision_history_count`: `{len(decision_history)}`",
            f"- `linked_audit_log_available`: `{review_context.get('linked_audit_log') is not None}`",
        ]
    )


def build_analyst_interpretation(
    intent,
    question,
    scoring_response,
    review_context=None,
):
    if intent == "feature_definition":
        feature = detect_feature_in_question(question, scoring_response)
        if feature:
            return (
                FEATURE_INTERPRETATIONS.get(
                    feature,
                    "Feature interpretation is limited by available project documentation.",
                )
                + " Interpret this feature together with the applicant's local SHAP value and the retrieved documentation context."
            )

    base = (
        "This answer is generated from the local API scoring response, local JSONL review context when provided, "
        "and retrieved project documentation. It is analyst decision support, not automated approval or rejection."
    )

    if intent == "high_risk_reason":
        return base + " The analyst should review the strongest positive SHAP drivers, threshold position, and any human review triggers."
    if intent == "review_status":
        return base + " Review status reflects the local prototype review log and should be reconciled with any external operational process."
    if intent == "governance_traceability":
        return base + " Governance fields help connect the score, explanation, model version, threshold, and review workflow."
    if intent == "data_quality":
        return base + " Input quality fields help identify whether the score was generated from complete and expected model-ready features."

    return base


def generate_analyst_answer(question, scoring_response, snippets, review_context=None):
    intent = classify_question_intent(question, scoring_response)

    return f"""# Analyst Q&A Response

## Question

{question}

## Short Answer

{build_short_answer(intent, question, scoring_response, review_context)}

## Evidence from Scoring Response

{build_evidence_section(intent, scoring_response)}

## Human Review Context

{format_human_review_context(review_context)}

## Retrieved Project Context

{format_retrieved_context(snippets)}

## Analyst Interpretation

{build_analyst_interpretation(intent, question, scoring_response, review_context)}
"""


def resolve_output_path(output_path):
    path = Path(output_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a deterministic single-turn analyst Q&A answer."
    )
    parser.add_argument("--question", required=True, help="Single analyst question to answer.")
    parser.add_argument("--response-path", help="Optional API response JSON path.")
    parser.add_argument("--review-case-id", help="Optional human review case id.")
    parser.add_argument(
        "--output-path",
        default=str(DEFAULT_OUTPUT_PATH.relative_to(PROJECT_ROOT)),
        help="Output markdown path.",
    )
    parser.add_argument(
        "--max-snippets",
        type=int,
        default=6,
        help="Maximum retrieved documentation snippets.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.response_path:
        scoring_response, response_path = load_response_from_path(args.response_path)
    else:
        scoring_response, response_path = load_sample_response()

    review_context = None
    if args.review_case_id:
        review_context = load_review_case_detail(args.review_case_id)

    documents = load_knowledge_documents()
    snippets = retrieve_question_snippets(
        documents,
        args.question,
        scoring_response,
        review_context=review_context,
        max_snippets=args.max_snippets,
    )
    intent = classify_question_intent(args.question, scoring_response)

    output_path = resolve_output_path(args.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    answer = generate_analyst_answer(
        args.question,
        scoring_response,
        snippets,
        review_context=review_context,
    )
    output_path.write_text(answer, encoding="utf-8")

    print(f"Loaded API response from: {response_path}")
    print(f"Loaded project docs: {len(documents)}")
    print(f"Detected intent: {intent}")
    print(f"Retrieved snippets: {len(snippets)}")
    print(f"Analyst Q&A response saved to: {output_path}")


if __name__ == "__main__":
    main()
