from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score


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

    return model, auc, X


def predict(model, X):
    return model.predict_proba(X)[:, 1]
