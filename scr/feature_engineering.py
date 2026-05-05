def build_bureau_features(bureau):
    bureau_features = bureau.groupby("SK_ID_CURR").agg({
        "SK_ID_BUREAU": "count",
        "AMT_CREDIT_SUM": "mean",
        "AMT_CREDIT_SUM_OVERDUE": "sum",
        "DAYS_CREDIT_UPDATE": "mean"
    }).reset_index()

    bureau_features.rename(columns={
        "SK_ID_BUREAU": "bureau_record_count",
        "AMT_CREDIT_SUM": "avg_credit_sum",
        "AMT_CREDIT_SUM_OVERDUE": "total_overdue_amount",
        "DAYS_CREDIT_UPDATE": "avg_days_credit_update"
    }, inplace=True)

    return bureau_features