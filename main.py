import os
import pandas as pd
from io import BytesIO

from src.config import ACCOUNT_NAME, ACCOUNT_KEY, CONTAINER_NAME
from src.data_ingestion import create_blob_client
from src.feature_engineering import build_bureau_features
from src.model import train_model, predict


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
    client = create_blob_client(ACCOUNT_NAME, ACCOUNT_KEY)

    # 1. Load data
    bureau = load_csv_from_blob(client, CONTAINER_NAME, "raw/bureau.csv")
    app_train = load_csv_from_blob(client, CONTAINER_NAME, "application_train.csv")

    print("bureau loaded:", bureau.shape)
    print("application_train loaded:", app_train.shape)

    # 2. Feature engineering
    bureau_features = build_bureau_features(bureau)
    print("bureau features built:", bureau_features.shape)

    os.makedirs("outputs", exist_ok=True)

    bureau_features.to_csv("outputs/bureau_features.csv", index=False)
    upload_file_to_blob(
        client,
        CONTAINER_NAME,
        "outputs/bureau_features.csv",
        "features/bureau_features.csv"
    )

    # 3. Merge
    df = app_train.merge(bureau_features, on="SK_ID_CURR", how="left")

    # 4. Train model
    model, auc, X = train_model(df)

    print(f"Validation AUC: {auc:.4f}")

    # 5. Predict risk score
    risk_scores = pd.DataFrame({
        "SK_ID_CURR": df["SK_ID_CURR"],
        "risk_score": predict(model, X)
    })

    risk_scores.to_csv("outputs/risk_scores.csv", index=False)

    # 6. Upload output
    upload_file_to_blob(
        client,
        CONTAINER_NAME,
        "outputs/risk_scores.csv",
        "outputs/risk_scores.csv"
    )


if __name__ == "__main__":
    main()