import json
import pickle
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import shap
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "outputs" / "models" / "model.pkl"
FEATURE_LIST_PATH = PROJECT_ROOT / "outputs" / "models" / "feature_list.json"
RISK_BAND_SUMMARY_PATH = (
    PROJECT_ROOT / "outputs" / "reports" / "risk_band_summary.csv"
)
API_LOG_DIR = PROJECT_ROOT / "outputs" / "api_logs"
SCORING_AUDIT_LOG_PATH = API_LOG_DIR / "scoring_audit_log.jsonl"
HUMAN_REVIEW_CASE_LOG_PATH = API_LOG_DIR / "human_review_cases.jsonl"
HUMAN_REVIEW_DECISION_LOG_PATH = API_LOG_DIR / "human_review_decisions.jsonl"
THRESHOLD = 0.15
MODEL_VERSION = "xgboost_v1"


class PredictionRequest(BaseModel):
    features: dict[str, Any]
    strict: bool = False


class HumanReviewDecisionRequest(BaseModel):
    review_decision: str
    reviewer: str | None = None
    notes: str | None = None
    status: str = "review_completed"


def load_model():
    if not MODEL_PATH.exists():
        raise RuntimeError(f"Model file not found: {MODEL_PATH}")

    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


def load_feature_list():
    if not FEATURE_LIST_PATH.exists():
        raise RuntimeError(f"Feature list file not found: {FEATURE_LIST_PATH}")

    with open(FEATURE_LIST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_risk_band_summary():
    if not RISK_BAND_SUMMARY_PATH.exists():
        return None

    return pd.read_csv(RISK_BAND_SUMMARY_PATH)


model = load_model()
feature_list = load_feature_list()
risk_band_summary = load_risk_band_summary()

app = FastAPI(title="Home Credit Risk Scoring API")


def assign_risk_band(risk_score):
    if risk_band_summary is None:
        return "Unknown"

    min_score = risk_band_summary["min_predicted_risk"].min()
    max_score = risk_band_summary["max_predicted_risk"].max()

    if risk_score < min_score:
        return "Band 1 - Lowest Risk"
    if risk_score > max_score:
        return "Band 5 - Highest Risk"

    matched_band = risk_band_summary[
        (risk_band_summary["min_predicted_risk"] <= risk_score)
        & (risk_score <= risk_band_summary["max_predicted_risk"])
    ]
    if matched_band.empty:
        return "Unknown"

    return matched_band.iloc[0]["risk_band"]


def align_prediction_request(request):
    input_features = request.features
    provided_features = set(input_features)
    required_features = set(feature_list)

    missing_features = [
        feature for feature in feature_list if feature not in input_features
    ]
    unexpected_features = sorted(provided_features - required_features)

    if request.strict and missing_features:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Missing required model features.",
                "missing_features": missing_features,
            },
        )

    aligned_features = {
        feature: input_features.get(feature, -999)
        for feature in feature_list
    }
    input_df = pd.DataFrame([aligned_features])
    input_df = input_df.apply(pd.to_numeric, errors="coerce").fillna(-999)

    return input_df, missing_features, unexpected_features


def score_aligned_input(input_df, missing_features, unexpected_features):
    try:
        risk_score = float(model.predict_proba(input_df)[:, 1][0])
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {exc}",
        ) from exc

    return {
        "risk_score": risk_score,
        "risk_band": assign_risk_band(risk_score),
        "high_risk_flag_015": int(risk_score >= THRESHOLD),
        "threshold_used": THRESHOLD,
        "model_version": MODEL_VERSION,
        "missing_feature_count": len(missing_features),
        "missing_features_preview": missing_features[:10],
        "unexpected_feature_count": len(unexpected_features),
        "unexpected_features_preview": unexpected_features[:10],
    }


def get_binary_shap_values(shap_values):
    if isinstance(shap_values, list):
        if len(shap_values) > 1:
            return shap_values[1]
        return shap_values[0]

    shap_values_array = np.asarray(shap_values)
    if shap_values_array.ndim == 3:
        if shap_values_array.shape[2] > 1:
            return shap_values_array[:, :, 1]
        return shap_values_array[:, :, 0]

    return shap_values_array


def get_value_status(feature, feature_value):
    if feature_value in [-999, -1000]:
        return "sentinel_missing"
    if feature == "DAYS_EMPLOYED" and feature_value == 365243:
        return "special_encoded_value"
    return "actual_value"


def build_shap_driver(row, direction, rank):
    contribution_direction = (
        "positive_risk_drive"
        if direction == "positive"
        else "negative_risk_drive"
    )
    return {
        "feature": row["feature"],
        "feature_value": row["feature_value"],
        "value_status": row["value_status"],
        "shap_value": float(row["shap_value"]),
        "contribution_direction": contribution_direction,
        "contribution_rank": rank,
    }


def build_human_review_recommendation(response: dict) -> dict:
    review_required = False
    review_reasons = []

    risk_score = response["risk_score"]
    missing_feature_count = response["missing_feature_count"]
    unexpected_feature_count = response["unexpected_feature_count"]

    if risk_score >= THRESHOLD:
        review_required = True
        review_reasons.append(
            "Risk score is above the candidate high-risk threshold."
        )

    if abs(risk_score - THRESHOLD) <= 0.02:
        review_required = True
        review_reasons.append(
            "Risk score is close to the candidate decision threshold."
        )

    if missing_feature_count > 0:
        review_required = True
        review_reasons.append(
            "Required model features were missing and filled during scoring."
        )

    if unexpected_feature_count > 0:
        review_reasons.append(
            "Unexpected input features were provided and ignored by the model."
        )

    positive_shap_sum_top3 = sum(
        driver["shap_value"]
        for driver in response.get("top_positive_risk_drivers", [])[:3]
    )
    negative_shap_abs_sum_top3 = abs(sum(
        driver["shap_value"]
        for driver in response.get("top_negative_risk_drivers", [])[:3]
    ))

    if positive_shap_sum_top3 >= 0.5:
        review_required = True
        review_reasons.append("Strong positive SHAP risk drivers are present.")

    if positive_shap_sum_top3 >= 0.5 and negative_shap_abs_sum_top3 >= 0.1:
        review_required = True
        review_reasons.append(
            "Both risk-increasing and risk-reducing SHAP signals are material."
        )

    if risk_score >= 0.30 or missing_feature_count > 10:
        review_priority = "high"
    elif review_required:
        review_priority = "medium"
    else:
        review_priority = "low"

    if not review_reasons:
        review_reasons.append(
            "No major review trigger was identified by the current rule set."
        )

    return {
        "review_required": review_required,
        "review_priority": review_priority,
        "review_reasons": review_reasons,
    }


def make_json_safe(value):
    if isinstance(value, dict):
        return {key: make_json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [make_json_safe(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def append_jsonl(path: Path, entry: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(make_json_safe(entry)) + "\n")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []

    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def write_audit_log(response: dict, endpoint_name: str) -> str:
    audit_log_id = str(uuid.uuid4())

    audit_entry = {
        "audit_log_id": audit_log_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "endpoint_name": endpoint_name,
        "model_version": response.get("model_version"),
        "threshold_used": response.get("threshold_used"),
        "risk_score": response.get("risk_score"),
        "risk_band": response.get("risk_band"),
        "high_risk_flag_015": response.get("high_risk_flag_015"),
        "missing_feature_count": response.get("missing_feature_count"),
        "unexpected_feature_count": response.get("unexpected_feature_count"),
        "top_positive_risk_drivers_preview": response.get(
            "top_positive_risk_drivers",
            []
        )[:3],
        "top_negative_risk_drivers_preview": response.get(
            "top_negative_risk_drivers",
            []
        )[:3],
        "human_review_recommendation": response.get(
            "human_review_recommendation"
        ),
    }

    append_jsonl(SCORING_AUDIT_LOG_PATH, audit_entry)

    return audit_log_id


def create_human_review_case(response: dict, endpoint_name: str) -> dict | None:
    recommendation = response.get("human_review_recommendation", {})
    if not recommendation.get("review_required"):
        return None

    review_case = {
        "review_case_id": str(uuid.uuid4()),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "pending_review",
        "endpoint_name": endpoint_name,
        "audit_log_id": response.get("audit_log_id"),
        "model_version": response.get("model_version"),
        "risk_score": response.get("risk_score"),
        "risk_band": response.get("risk_band"),
        "high_risk_flag_015": response.get("high_risk_flag_015"),
        "threshold_used": response.get("threshold_used"),
        "review_priority": recommendation.get("review_priority"),
        "review_reasons": recommendation.get("review_reasons", []),
        "missing_feature_count": response.get("missing_feature_count"),
        "unexpected_feature_count": response.get("unexpected_feature_count"),
        "top_positive_risk_drivers_preview": response.get(
            "top_positive_risk_drivers",
            []
        )[:3],
        "top_negative_risk_drivers_preview": response.get(
            "top_negative_risk_drivers",
            []
        )[:3],
    }
    append_jsonl(HUMAN_REVIEW_CASE_LOG_PATH, review_case)
    return {
        "review_case_id": review_case["review_case_id"],
        "status": review_case["status"],
        "review_priority": review_case["review_priority"],
    }


def latest_review_decisions_by_case() -> dict[str, dict]:
    decisions = read_jsonl(HUMAN_REVIEW_DECISION_LOG_PATH)
    latest_decisions = {}
    for decision in decisions:
        latest_decisions[decision.get("review_case_id")] = decision
    return latest_decisions


def build_review_queue_item(
    review_case: dict,
    latest_decision: dict | None,
    case_number: int,
) -> dict:
    visible_status = review_case.get("status", "pending_review")
    latest_review_status = None
    latest_review_decision = None
    latest_review_updated_at = None

    if latest_decision:
        latest_review_status = latest_decision.get("status")
        latest_review_decision = latest_decision.get("review_decision")
        latest_review_updated_at = latest_decision.get("updated_at_utc")
        visible_status = latest_review_status or visible_status

    risk_band = review_case.get("risk_band")
    review_priority = review_case.get("review_priority")
    case_label = (
        f"Case {case_number} | {risk_band} | "
        f"{review_priority} | {visible_status}"
    )

    return {
        "case_number": case_number,
        "case_label": case_label,
        "review_case_id": review_case.get("review_case_id"),
        "created_at_utc": review_case.get("created_at_utc"),
        "status": visible_status,
        "risk_score": review_case.get("risk_score"),
        "risk_band": risk_band,
        "review_priority": review_priority,
        "audit_log_id": review_case.get("audit_log_id"),
        "latest_review_status": latest_review_status,
        "latest_review_decision": latest_review_decision,
        "latest_review_updated_at": latest_review_updated_at,
    }


def get_human_review_queue(status: str | None = None) -> list[dict]:
    cases = read_jsonl(HUMAN_REVIEW_CASE_LOG_PATH)
    latest_decisions = latest_review_decisions_by_case()
    cases = sorted(
        cases,
        key=lambda review_case: review_case.get("created_at_utc") or "",
        reverse=True,
    )
    filtered_cases = []

    for review_case in cases:
        case_id = review_case.get("review_case_id")
        latest_decision = latest_decisions.get(case_id)
        visible_status = review_case.get("status", "pending_review")
        if latest_decision:
            visible_status = latest_decision.get(
                "status",
                visible_status,
            )

        if status and visible_status != status:
            continue
        filtered_cases.append((review_case, latest_decision))

    return [
        build_review_queue_item(review_case, latest_decision, case_number)
        for case_number, (review_case, latest_decision) in enumerate(
            filtered_cases,
            start=1,
        )
    ]


def get_human_review_case_detail(review_case_id: str) -> dict:
    matching_cases = [
        review_case
        for review_case in read_jsonl(HUMAN_REVIEW_CASE_LOG_PATH)
        if review_case.get("review_case_id") == review_case_id
    ]
    if not matching_cases:
        raise HTTPException(
            status_code=404,
            detail=f"Human review case not found: {review_case_id}",
        )

    review_case = matching_cases[-1]
    decision_history = [
        decision
        for decision in read_jsonl(HUMAN_REVIEW_DECISION_LOG_PATH)
        if decision.get("review_case_id") == review_case_id
    ]
    latest_decision = decision_history[-1] if decision_history else None

    audit_log_id = review_case.get("audit_log_id")
    linked_audit_log = None
    if audit_log_id:
        matching_audit_logs = [
            audit_log
            for audit_log in read_jsonl(SCORING_AUDIT_LOG_PATH)
            if audit_log.get("audit_log_id") == audit_log_id
        ]
        if matching_audit_logs:
            linked_audit_log = matching_audit_logs[-1]

    return {
        "review_case_id": review_case_id,
        "review_case": review_case,
        "latest_decision": latest_decision,
        "decision_history": decision_history,
        "linked_audit_log": linked_audit_log,
    }


def write_human_review_decision(
    review_case_id: str,
    decision_request: HumanReviewDecisionRequest,
) -> dict:
    matching_cases = [
        review_case
        for review_case in read_jsonl(HUMAN_REVIEW_CASE_LOG_PATH)
        if review_case.get("review_case_id") == review_case_id
    ]
    if not matching_cases:
        raise HTTPException(
            status_code=404,
            detail=f"Human review case not found: {review_case_id}",
        )

    decision_entry = {
        "review_decision_id": str(uuid.uuid4()),
        "review_case_id": review_case_id,
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": decision_request.status,
        "review_decision": decision_request.review_decision,
        "reviewer": decision_request.reviewer,
        "notes": decision_request.notes,
    }
    append_jsonl(HUMAN_REVIEW_DECISION_LOG_PATH, decision_entry)
    return decision_entry


def generate_local_explanation(input_df, top_n=8):
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(input_df)
        shap_values_for_input = get_binary_shap_values(shap_values)[0]
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"SHAP explanation failed: {exc}",
        ) from exc

    shap_detail = pd.DataFrame({
        "feature": input_df.columns,
        "feature_value": input_df.iloc[0].values,
        "shap_value": shap_values_for_input,
    })
    shap_detail["value_status"] = shap_detail.apply(
        lambda row: get_value_status(row["feature"], row["feature_value"]),
        axis=1
    )

    positive_drivers = (
        shap_detail[shap_detail["shap_value"] > 0]
        .sort_values("shap_value", ascending=False)
        .head(top_n)
    )
    negative_drivers = (
        shap_detail[shap_detail["shap_value"] < 0]
        .sort_values("shap_value", ascending=True)
        .head(top_n)
    )

    return {
        "top_positive_risk_drivers": [
            build_shap_driver(row, "positive", rank)
            for rank, (_, row) in enumerate(positive_drivers.iterrows(), start=1)
        ],
        "top_negative_risk_drivers": [
            build_shap_driver(row, "negative", rank)
            for rank, (_, row) in enumerate(negative_drivers.iterrows(), start=1)
        ],
        "explanation_note": (
            "Positive SHAP values increase the model output toward higher "
            "predicted default risk. Negative SHAP values decrease the model "
            "output toward lower predicted default risk."
        ),
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "feature_count": len(feature_list),
        "threshold": THRESHOLD,
        "model_version": MODEL_VERSION,
    }


@app.post("/predict")
def predict(request: PredictionRequest):
    input_df, missing_features, unexpected_features = align_prediction_request(
        request
    )
    return score_aligned_input(input_df, missing_features, unexpected_features)


@app.post("/predict-with-explanation")
def predict_with_explanation(request: PredictionRequest):
    input_df, missing_features, unexpected_features = align_prediction_request(
        request
    )
    response = score_aligned_input(input_df, missing_features, unexpected_features)
    response.update(generate_local_explanation(input_df))
    response["human_review_recommendation"] = build_human_review_recommendation(
        response
    )
    try:
        response["audit_log_id"] = write_audit_log(
            response,
            endpoint_name="predict-with-explanation"
        )
    except Exception as exc:
        response["audit_log_id"] = None
        response["audit_log_error"] = f"Audit logging failed: {exc}"
    try:
        response["human_review_case"] = create_human_review_case(
            response,
            endpoint_name="predict-with-explanation"
        )
    except Exception as exc:
        response["human_review_case"] = None
        response["human_review_case_error"] = (
            f"Human review case creation failed: {exc}"
        )
    return response


@app.get("/human-review/queue")
def human_review_queue(status: str | None = None):
    cases = get_human_review_queue(status=status)
    return {
        "case_count": len(cases),
        "status_filter": status,
        "cases": cases,
    }


@app.get("/human-review/{review_case_id}")
def human_review_case_detail(review_case_id: str):
    return get_human_review_case_detail(review_case_id)


@app.post("/human-review/{review_case_id}/decision")
def human_review_decision(
    review_case_id: str,
    request: HumanReviewDecisionRequest,
):
    return write_human_review_decision(review_case_id, request)


# Run with:
# uvicorn src.api:app --reload
