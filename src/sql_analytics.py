from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def build_risk_analytics_base():
    risk_scores_path = PROJECT_ROOT / "outputs" / "risk_scores.csv"
    application_train_path = (
        PROJECT_ROOT / "data" / "raw" / "application_train.csv"
    )
    output_dir = PROJECT_ROOT / "outputs" / "sql_reports"
    output_path = output_dir / "risk_analytics_base.csv"

    application_columns = [
        "SK_ID_CURR",
        "TARGET",
        "AMT_INCOME_TOTAL",
        "AMT_CREDIT",
        "AMT_ANNUITY",
        "NAME_INCOME_TYPE",
        "NAME_CONTRACT_TYPE",
        "NAME_EDUCATION_TYPE",
        "REGION_RATING_CLIENT",
    ]

    print("risk_scores_path:", risk_scores_path)
    print("application_train_path:", application_train_path)
    print("output_path:", output_path)

    risk_scores = pd.read_csv(risk_scores_path)
    application_train = pd.read_csv(
        application_train_path,
        usecols=application_columns
    )

    print("risk_scores shape:", risk_scores.shape)
    print("selected application_train shape:", application_train.shape)

    risk_analytics_base = application_train.merge(
        risk_scores[["SK_ID_CURR", "risk_score", "risk_band"]],
        on="SK_ID_CURR",
        how="left"
    )
    risk_analytics_base["high_risk_flag_015"] = (
        risk_analytics_base["risk_score"] >= 0.15
    ).astype(int)

    output_columns = [
        "SK_ID_CURR",
        "TARGET",
        "risk_score",
        "risk_band",
        "high_risk_flag_015",
        "AMT_INCOME_TOTAL",
        "AMT_CREDIT",
        "AMT_ANNUITY",
        "NAME_INCOME_TYPE",
        "NAME_CONTRACT_TYPE",
        "NAME_EDUCATION_TYPE",
        "REGION_RATING_CLIENT",
    ]
    risk_analytics_base = risk_analytics_base[output_columns]

    print("merged output shape:", risk_analytics_base.shape)
    print(
        "duplicate SK_ID_CURR count in final output:",
        risk_analytics_base["SK_ID_CURR"].duplicated().sum()
    )
    print("missing risk_score count:", risk_analytics_base["risk_score"].isna().sum())

    if risk_analytics_base.shape[0] != application_train.shape[0]:
        print(
            "WARNING: merged output row count changed from application_train row count."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    risk_analytics_base.to_csv(output_path, index=False)
    print("output path:", output_path)


if __name__ == "__main__":
    build_risk_analytics_base()
