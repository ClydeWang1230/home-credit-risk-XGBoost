import json
import os
import pickle
import pandas as pd
from io import BytesIO

from src.config import ACCOUNT_NAME, ACCOUNT_KEY, CONTAINER_NAME
from src.data_ingestion import create_blob_client
from src.feature_engineering import (
    build_bureau_features,
    build_previous_application_features,
)
from src.model import train_model, predict


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
    model, auc, X = train_model(app_train)

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

    # 5. Predict risk score
    risk_scores = pd.DataFrame({
        "SK_ID_CURR": app_train["SK_ID_CURR"],
        "risk_score": predict(model, X)
    })

    risk_scores.to_csv("outputs/risk_scores.csv", index=False)

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
