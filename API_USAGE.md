# FastAPI Scoring API Usage

## Purpose

This API exposes the trained Home Credit XGBoost credit risk model through a local FastAPI scoring endpoint.

FastAPI v2 supports model scoring and local applicant-level SHAP explanations. Audit logs and human review workflows will be added in later versions.

## How to Start the API

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

## Endpoints

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

`features` is a dictionary of model feature names and values.

`strict=false` fills missing model features with `-999`.

`strict=true` requires all 131 model features.

For realistic testing, use the generated complete sample payload.

### `POST /predict-with-explanation`

Accepts the same request body as `/predict`, returns the same scoring fields, and adds local applicant-level SHAP explanation drivers.

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

The explanation section includes:

- `top_positive_risk_drivers`: features pushing the prediction toward higher default risk
- `top_negative_risk_drivers`: features pushing the prediction toward lower default risk
- `explanation_note`: short explanation of positive and negative SHAP values

Each SHAP driver includes:

```json
{
  "feature": "EXT_SOURCE_3",
  "feature_value": 0.12,
  "value_status": "actual_value",
  "shap_value": 0.41,
  "contribution_direction": "positive_risk_drive",
  "contribution_rank": 1
}
```

Positive SHAP values increase the model output toward higher predicted default risk. Negative SHAP values decrease the model output toward lower predicted default risk.

## Complete Sample Payload

Sample payload:

```text
outputs/api_samples/sample_predict_payload.json
```

Sample metadata:

```text
outputs/api_samples/sample_predict_payload_metadata.json
```

The sample payload contains a complete real applicant feature row with all 131 model features.

## Testing in Swagger UI

Open:

```text
http://127.0.0.1:8000/docs
```

Then:

1. Expand `POST /predict`
2. Click `Try it out`
3. Paste the full content of `outputs/api_samples/sample_predict_payload.json`
4. Click `Execute`
5. Confirm that `missing_feature_count = 0` and `unexpected_feature_count = 0`

The same sample payload can also be used with `POST /predict-with-explanation` to test local SHAP explanations.

Example successful response:

```json
{
  "risk_score": 0.7146458029747009,
  "risk_band": "Band 5 - Highest Risk",
  "high_risk_flag_015": 1,
  "threshold_used": 0.15,
  "model_version": "xgboost_v1",
  "missing_feature_count": 0,
  "missing_features_preview": [],
  "unexpected_feature_count": 0,
  "unexpected_features_preview": []
}
```
The response fields can be interpreted as follows:

- `risk_score` is the model-predicted default risk score for the submitted applicant.
- `risk_band` translates the numeric score into a business-facing portfolio risk segment.
- `high_risk_flag_015` indicates whether the applicant is above the candidate high-risk threshold of 0.15.
- `threshold_used` records the decision threshold used in this API version for traceability.
- `missing_feature_count` and `unexpected_feature_count` help validate API input quality before using the prediction for analysis or review.
- 
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

Prediction request with local SHAP explanation:

```bash
curl -X POST "http://127.0.0.1:8000/predict-with-explanation" \
  -H "Content-Type: application/json" \
  -d '{"features":{"AMT_CREDIT":500000,"AMT_ANNUITY":25000},"strict":false}'
```

On Windows PowerShell, `curl.exe` may be safer than `curl` because `curl` can be aliased to `Invoke-WebRequest`.

## Current Limitations

- FastAPI v1 expects model-ready engineered features.
- It does not yet transform raw application, bureau, or previous application tables into model features.
- It does not yet write audit logs.
- It does not yet include a human review workflow.
- The sample payload is for developer testing, not final end-user interaction.

## Next Steps

- Add audit-friendly scoring logs.
- Add human review recommendation logic.
- Later support more user-friendly input formats or batch scoring.
