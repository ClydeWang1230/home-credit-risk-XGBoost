import json
import os
import pickle
import pandas as pd
from io import BytesIO

from src.config import ACCOUNT_NAME, ACCOUNT_KEY, CONTAINER_NAME
from src.data_ingestion import create_blob_client
from src.feature_engineering import (
    add_application_train_ratio_features,
    build_bureau_features,
    build_previous_application_features,
)
from src.model import train_model, predict
from src.api_sample_payload import save_sample_predict_payload
from src.shap_analysis import generate_local_shap_examples, generate_shap_reports


DATA_SOURCE = os.getenv("DATA_SOURCE", "local").lower()

def load_csv_from_blob(client, container_name, blob_name):
    blob_client = client.get_blob_client(
        container=container_name,
        blob=blob_name
    )
    data = blob_client.download_blob().readall()
    return pd.read_csv(BytesIO(data))

def upload_file_to_blob(client, container_name, local_file_path, blob_name):
    container_client = client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)

    with open(local_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True, timeout=300)

    print(f"Uploaded {local_file_path} to Azure Blob as {blob_name}")


def get_business_category(feature):
    feature_upper = feature.upper()
    feature_lower = feature.lower()
    bureau_features = {
        "bureau_debt_credit_ratio",
        "n_active_bureau_credits",
        "n_closed_bureau_credits",
        "active_credit_ratio",
        "total_bureau_debt",
        "max_credit_day_overdue",
        "n_overdue_bureau_records",
    }

    if "EXT_SOURCE" in feature_upper:
        return "external_credit_score"
    if feature in bureau_features:
        return "external_bureau_history"
    if any(
        keyword in feature_upper
        for keyword in ["AMT_CREDIT", "AMT_ANNUITY", "AMT_INCOME", "AMT_GOODS"]
    ):
        return "affordability_and_exposure"
    if feature == "income_per_family_member":
        return "affordability_and_exposure"
    if "ratio" in feature_lower and any(
        keyword in feature_lower
        for keyword in ["credit", "annuity", "goods", "income", "family"]
    ):
        return "affordability_and_exposure"
    if any(
        keyword in feature_lower
        for keyword in [
            "prev",
            "application",
            "approval",
            "refusal",
            "down_payment",
            "days_decision",
        ]
    ):
        return "previous_application_behavior"
    if "bureau" in feature_lower or "credit_active" in feature_lower:
        return "external_bureau_history"
    if "DAYS_BIRTH" in feature_upper or "DAYS_EMPLOYED" in feature_upper:
        return "demographic_and_employment"
    return "other"


def get_business_interpretation(feature, business_category):
    custom_interpretations = {
        "avg_credit_prev": "Average previous credit amount, reflecting typical historical borrowing size.",
        "max_credit_prev": "Maximum previous credit amount, capturing peak historical credit exposure.",
        "avg_down_payment_prev": "Average previous down payment, a proxy for borrower liquidity in prior applications.",
        "days_decision_mean": "Average timing of prior application decisions, summarizing historical application recency.",
        "last_application_days": "Most recent previous application timing; values closer to 0 indicate more recent credit seeking.",
        "n_prev_applications": "Total number of previous applications, capturing historical credit demand.",
        "n_prev_approved": "Number of previously approved applications, indicating past access to credit.",
        "n_prev_refusals": "Number of previously refused applications, a direct signal of historical credit rejection.",
        "prev_approval_rate": "Share of previous applications approved, summarizing historical lender acceptance.",
        "prev_refusal_rate": "Share of previous applications refused, summarizing historical rejection frequency.",
        "avg_annuity_prev": "Average previous annuity amount, approximating prior repayment burden.",
        "credit_income_ratio": "Credit amount relative to borrower income, capturing loan-to-income pressure.",
        "annuity_income_ratio": "Scheduled repayment amount relative to borrower income, capturing repayment burden.",
        "credit_annuity_ratio": "Credit amount relative to scheduled repayment amount, approximating repayment horizon or amortization pressure.",
        "credit_goods_ratio": "Credit amount relative to goods price, approximating financing coverage and borrower self-funding capacity.",
        "income_per_family_member": "Borrower income adjusted by family size, capturing household income capacity.",
        "bureau_debt_credit_ratio": "External bureau debt relative to external credit amount, capturing external debt burden and credit utilization pressure.",
        "n_active_bureau_credits": "Number of active external bureau credit records, capturing current external credit activity.",
        "n_closed_bureau_credits": "Number of closed external bureau credit records, capturing historical completed external credit relationships.",
        "active_credit_ratio": "Share of active bureau credit records, capturing the degree of active external credit exposure.",
        "total_bureau_debt": "Total external bureau debt amount, capturing external debt burden.",
        "max_credit_day_overdue": "Maximum overdue days across bureau records, capturing severe external delinquency history.",
        "n_overdue_bureau_records": "Number of bureau records with overdue days greater than zero, capturing frequency of external overdue behavior.",
    }
    if feature in custom_interpretations:
        return custom_interpretations[feature]

    generic_interpretations = {
        "external_credit_score": "External source score feature that may summarize third-party credit risk signals.",
        "affordability_and_exposure": "Amount-based feature related to borrower affordability, income, credit size, or exposure.",
        "previous_application_behavior": "Historical application behavior feature derived from prior credit applications.",
        "external_bureau_history": "External bureau history feature summarizing prior or active credit records.",
        "demographic_and_employment": "Demographic or employment timing feature used as a borrower profile signal.",
        "other": "Model input feature retained for predictive ranking and reviewed through feature importance.",
    }
    return generic_interpretations[business_category]


def main():
    # 1. Load data
    if DATA_SOURCE == "local":
        client = None
        print("Loading data from local data/raw/")
        app_train = pd.read_csv("data/raw/application_train.csv")
        bureau = pd.read_csv("data/raw/bureau.csv")
        previous_application = pd.read_csv("data/raw/previous_application.csv")
    elif DATA_SOURCE == "azure":
        client = create_blob_client(ACCOUNT_NAME, ACCOUNT_KEY)
        print("Loading data from Azure Blob Storage")
        bureau = load_csv_from_blob(client, CONTAINER_NAME, "raw/bureau.csv")
        previous_application = load_csv_from_blob(
            client,
            CONTAINER_NAME,
            "previous_application.csv"  # Adjust to "raw/previous_application.csv" if blob layout changes.
        )
        app_train = load_csv_from_blob(client, CONTAINER_NAME, "application_train.csv")
    else:
        raise ValueError(
            f"Unsupported DATA_SOURCE: {DATA_SOURCE}. Use 'local' or 'azure'."
        )

    print("Loaded application_train shape:", app_train.shape)
    print("Loaded bureau shape:", bureau.shape)
    print("Loaded previous_application shape:", previous_application.shape)
    print("app_train shape before ratio features:", app_train.shape)
    app_train = add_application_train_ratio_features(app_train)
    print("app_train shape after ratio features:", app_train.shape)
    application_train_shape = app_train.shape
    bureau_shape = bureau.shape
    previous_application_shape = previous_application.shape

    # 2. Feature engineering
    bureau_features = build_bureau_features(bureau)
    previous_application_features = build_previous_application_features(
        previous_application
    )
    bureau_features_shape = bureau_features.shape
    previous_application_features_shape = previous_application_features.shape
    duplicate_sk_id_curr_previous_application = (
        previous_application_features["SK_ID_CURR"].duplicated().sum()
    )

    print("bureau features built:", bureau_features.shape)
    print(
        "previous_application features built:",
        previous_application_features.shape
    )
    print(
        "previous_application feature duplicate SK_ID_CURR count:",
        duplicate_sk_id_curr_previous_application
    )

    os.makedirs("outputs", exist_ok=True)
    os.makedirs("outputs/metrics", exist_ok=True)
    os.makedirs("outputs/models", exist_ok=True)
    os.makedirs("outputs/reports", exist_ok=True)

    bureau_features.to_csv("outputs/bureau_features.csv", index=False)
    if client is not None:
        upload_file_to_blob(
            client,
            CONTAINER_NAME,
            "outputs/bureau_features.csv",
            "features/bureau_features.csv"
        )

    previous_application_features.to_csv(
        "outputs/previous_application_features.csv",
        index=False
    )
    if client is not None:
        upload_file_to_blob(
            client,
            CONTAINER_NAME,
            "outputs/previous_application_features.csv",
            "features/previous_application_features.csv"
        )

    # 3. Merge
    rows_before_merge = app_train.shape[0]
    app_train = app_train.merge(bureau_features, on="SK_ID_CURR", how="left")

    app_train_rows_before_previous_features = app_train.shape[0]
    app_train = app_train.merge(
        previous_application_features,
        on="SK_ID_CURR",
        how="left"
    )
    rows_after_merge = app_train.shape[0]
    print(
        "app_train rows before previous_application feature merge:",
        app_train_rows_before_previous_features
    )
    print(
        "app_train rows after previous_application feature merge:",
        rows_after_merge
    )

    # 4. Train model
    model, auc, X, validation_results, evaluation_metrics, X_val = train_model(
        app_train
    )

    print(f"Validation AUC: {auc:.4f}")

    metrics = {
        "model_name": model.__class__.__name__,
        "validation_auc": float(auc),
        "data_source": DATA_SOURCE,
        "application_train_shape": list(application_train_shape),
        "bureau_shape": list(bureau_shape),
        "previous_application_shape": list(previous_application_shape),
        "bureau_features_shape": list(bureau_features_shape),
        "previous_application_features_shape": list(
            previous_application_features_shape
        ),
        "duplicate_sk_id_curr_previous_application": int(
            duplicate_sk_id_curr_previous_application
        ),
        "rows_before_merge": int(rows_before_merge),
        "rows_after_merge": int(rows_after_merge),
    }
    with open("outputs/metrics/metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    with open("outputs/models/model.pkl", "wb") as f:
        pickle.dump(model, f)

    with open("outputs/models/feature_list.json", "w", encoding="utf-8") as f:
        json.dump(list(X.columns), f, indent=2)

    save_sample_predict_payload(X, validation_results)

    feature_importance = pd.DataFrame({
        "feature": X.columns,
        "importance": model.feature_importances_,
    }).sort_values("importance", ascending=False).reset_index(drop=True)
    feature_importance["importance_rank"] = feature_importance.index + 1
    feature_importance["business_category"] = feature_importance["feature"].apply(
        get_business_category
    )
    feature_importance["business_interpretation"] = feature_importance.apply(
        lambda row: get_business_interpretation(
            row["feature"],
            row["business_category"]
        ),
        axis=1
    )
    feature_importance.to_csv(
        "outputs/reports/feature_importance.csv",
        index=False
    )

    risk_band_labels = [
        "Band 1 - Lowest Risk",
        "Band 2",
        "Band 3",
        "Band 4",
        "Band 5 - Highest Risk",
    ]

    validation_results_with_bands = validation_results.copy()
    validation_results_with_bands["risk_band"] = pd.qcut(
        validation_results_with_bands["risk_score"].rank(method="first"),
        q=5,
        labels=risk_band_labels
    )
    validation_results_with_bands["high_risk_flag_015"] = (
        validation_results_with_bands["risk_score"] >= 0.15
    ).astype(int)
    validation_result_columns = [
        column
        for column in [
            "SK_ID_CURR",
            "TARGET",
            "risk_score",
            "risk_band",
            "high_risk_flag_015",
        ]
        if column in validation_results_with_bands.columns
    ]
    validation_results_with_bands[validation_result_columns].to_csv(
        "outputs/reports/validation_results.csv",
        index=False
    )
    print("Validation results saved to outputs/reports/validation_results.csv")

    validation_risk_band_summary = (
        validation_results_with_bands
        .groupby("risk_band", observed=True)
        .agg(
            applicant_count=("SK_ID_CURR", "count"),
            avg_predicted_risk=("risk_score", "mean"),
            observed_default_rate=("TARGET", "mean"),
            min_predicted_risk=("risk_score", "min"),
            max_predicted_risk=("risk_score", "max"),
        )
        .reset_index()
    )
    validation_risk_band_summary.to_csv(
        "outputs/reports/validation_risk_band_summary.csv",
        index=False
    )
    print(
        "Validation risk band summary saved to "
        "outputs/reports/validation_risk_band_summary.csv"
    )

    with open("outputs/reports/model_evaluation.json", "w", encoding="utf-8") as f:
        json.dump(evaluation_metrics, f, indent=2)
    print("Model evaluation saved to outputs/reports/model_evaluation.json")

    generate_shap_reports(model, X)
    generate_local_shap_examples(model, X_val, validation_results)

    threshold_rows = []
    for threshold in [0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.50]:
        y_true = validation_results["TARGET"]
        y_pred_label = validation_results["risk_score"] >= threshold

        true_positive = int(((y_true == 1) & y_pred_label).sum())
        false_positive = int(((y_true == 0) & y_pred_label).sum())
        false_negative = int(((y_true == 1) & ~y_pred_label).sum())
        true_negative = int(((y_true == 0) & ~y_pred_label).sum())

        precision_denominator = true_positive + false_positive
        recall_denominator = true_positive + false_negative
        precision = (
            true_positive / precision_denominator
            if precision_denominator > 0
            else 0
        )
        recall = (
            true_positive / recall_denominator
            if recall_denominator > 0
            else 0
        )
        f1_denominator = precision + recall
        f1 = 2 * precision * recall / f1_denominator if f1_denominator > 0 else 0

        predicted_positive_count = int(y_pred_label.sum())
        threshold_rows.append({
            "threshold": threshold,
            "predicted_positive_count": predicted_positive_count,
            "predicted_positive_rate": predicted_positive_count / len(y_true),
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "true_negative": true_negative,
            "false_positive": false_positive,
            "false_negative": false_negative,
            "true_positive": true_positive,
        })

    threshold_analysis = pd.DataFrame(threshold_rows)
    threshold_analysis.to_csv(
        "outputs/reports/threshold_analysis.csv",
        index=False
    )
    print("Threshold analysis saved to outputs/reports/threshold_analysis.csv")

    # 5. Predict risk score
    risk_scores = pd.DataFrame({
        "SK_ID_CURR": app_train["SK_ID_CURR"],
        "risk_score": predict(model, X)
    })

    risk_scores["risk_band"] = pd.qcut(
        risk_scores["risk_score"].rank(method="first"),
        q=5,
        labels=risk_band_labels
    )

    risk_scores_for_summary = risk_scores.copy()
    if "TARGET" in app_train.columns:
        risk_scores_for_summary["TARGET"] = app_train["TARGET"].values

    risk_band_summary = (
        risk_scores_for_summary
        .groupby("risk_band", observed=True)
        .agg(
            applicant_count=("SK_ID_CURR", "count"),
            avg_predicted_risk=("risk_score", "mean"),
            min_predicted_risk=("risk_score", "min"),
            max_predicted_risk=("risk_score", "max"),
        )
        .reset_index()
    )
    if "TARGET" in risk_scores_for_summary.columns:
        observed_default_rate = (
            risk_scores_for_summary
            .groupby("risk_band", observed=True)["TARGET"]
            .mean()
            .reset_index(name="observed_default_rate")
        )
        risk_band_summary = risk_band_summary.merge(
            observed_default_rate,
            on="risk_band",
            how="left"
        )
    else:
        risk_band_summary["observed_default_rate"] = pd.NA

    risk_band_summary = risk_band_summary[
        [
            "risk_band",
            "applicant_count",
            "avg_predicted_risk",
            "observed_default_rate",
            "min_predicted_risk",
            "max_predicted_risk",
        ]
    ]
    risk_band_summary.to_csv(
        "outputs/reports/risk_band_summary.csv",
        index=False
    )
    print("Risk band summary saved to outputs/reports/risk_band_summary.csv")

    risk_scores.to_csv("outputs/risk_scores.csv", index=False)
    print("Risk scores saved to outputs/risk_scores.csv")

    # 6. Upload output
    if client is not None:
        upload_file_to_blob(
            client,
            CONTAINER_NAME,
            "outputs/risk_scores.csv",
            "outputs/risk_scores.csv"
        )


if __name__ == "__main__":
    main()
