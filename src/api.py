import json
import pickle
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "outputs" / "models" / "model.pkl"
FEATURE_LIST_PATH = PROJECT_ROOT / "outputs" / "models" / "feature_list.json"
RISK_BAND_SUMMARY_PATH = (
    PROJECT_ROOT / "outputs" / "reports" / "risk_band_summary.csv"
)
THRESHOLD = 0.15
MODEL_VERSION = "xgboost_v1"


class PredictionRequest(BaseModel):
    features: dict[str, Any]
    strict: bool = False


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

    try:
        risk_score = float(model.predict_proba(input_df)[:, 1][0])
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {exc}",
        ) from exc

    risk_band = assign_risk_band(risk_score)

    return {
        "risk_score": risk_score,
        "risk_band": risk_band,
        "high_risk_flag_015": int(risk_score >= THRESHOLD),
        "threshold_used": THRESHOLD,
        "model_version": MODEL_VERSION,
        "missing_feature_count": len(missing_features),
        "missing_features_preview": missing_features[:10],
        "unexpected_feature_count": len(unexpected_features),
        "unexpected_features_preview": unexpected_features[:10],
    }


# Run with:
# uvicorn src.api:app --reload
