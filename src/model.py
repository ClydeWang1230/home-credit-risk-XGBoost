from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
import pandas as pd


def prepare_features(df, target_col="TARGET"):
    X = df.drop(columns=[target_col, "SK_ID_CURR"], errors="ignore")
    y = df[target_col]

    X = X.select_dtypes(include=["int64", "float64", "bool"])
    X = X.fillna(-999)

    return X, y


def train_model(df, target_col="TARGET"):
    X, y = prepare_features(df, target_col)

    X_train, X_val, y_train, y_val = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model = XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        eval_metric="auc",
        random_state=42
    )

    model.fit(X_train, y_train)

    y_pred = model.predict_proba(X_val)[:, 1]
    auc = roc_auc_score(y_val, y_pred)

    validation_results = pd.DataFrame({
        "SK_ID_CURR": df.loc[X_val.index, "SK_ID_CURR"].values,
        "TARGET": y_val.values,
        "risk_score": y_pred,
    })

    threshold = 0.5
    y_pred_label = (y_pred >= threshold).astype(int)
    evaluation_metrics = {
        "validation_auc": float(auc),
        "threshold": threshold,
        "precision": float(precision_score(y_val, y_pred_label, zero_division=0)),
        "recall": float(recall_score(y_val, y_pred_label, zero_division=0)),
        "f1_score": float(f1_score(y_val, y_pred_label, zero_division=0)),
        "confusion_matrix": confusion_matrix(y_val, y_pred_label).tolist(),
        "validation_sample_size": int(len(y_val)),
    }

    return model, auc, X, validation_results, evaluation_metrics


def predict(model, X):
    return model.predict_proba(X)[:, 1]
