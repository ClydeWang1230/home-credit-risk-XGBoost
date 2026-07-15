import json
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _clean_json_value(value):
    if pd.isna(value):
        return -999

    if isinstance(value, (int, float, np.number)) and np.isinf(value):
        return -999

    if isinstance(value, np.generic):
        return value.item()

    return value


def _can_use_validation_index(X, validation_results):
    if validation_results is None or validation_results.empty:
        return False

    default_validation_index = pd.RangeIndex(len(validation_results))
    if validation_results.index.equals(default_validation_index):
        return len(X) == len(validation_results)

    return validation_results.index.isin(X.index).all()


def save_sample_predict_payload(
    X,
    validation_results=None,
    output_dir="outputs/api_samples"
):
    output_dir = PROJECT_ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "feature_count": int(len(X.columns)),
    }

    if _can_use_validation_index(X, validation_results):
        selected_validation_index = validation_results["risk_score"].idxmax()
        selected_row = X.loc[selected_validation_index]
        selected_validation_row = validation_results.loc[selected_validation_index]
        metadata.update({
            "selected_row_index": _clean_json_value(selected_validation_index),
            "SK_ID_CURR": _clean_json_value(selected_validation_row["SK_ID_CURR"]),
            "TARGET": _clean_json_value(selected_validation_row["TARGET"]),
            "risk_score": _clean_json_value(selected_validation_row["risk_score"]),
            "source_case": "highest_risk_validation_sample",
        })
    else:
        selected_row = X.iloc[0]
        metadata.update({
            "selected_row_index": _clean_json_value(X.index[0]),
            "SK_ID_CURR": None,
            "TARGET": None,
            "risk_score": None,
            "source_case": "fallback_first_feature_row",
        })

    features = {
        feature: _clean_json_value(value)
        for feature, value in selected_row.items()
    }
    payload = {
        "features": features,
        "strict": True,
    }

    payload_path = output_dir / "sample_predict_payload.json"
    metadata_path = output_dir / "sample_predict_payload_metadata.json"

    payload_path.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8"
    )
    metadata_path.write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8"
    )

    print("sample payload output path:", payload_path)
    print("metadata output path:", metadata_path)
    print("feature count in payload:", len(features))
