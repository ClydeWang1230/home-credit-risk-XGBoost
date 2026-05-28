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


def build_previous_application_features(previous_application):
    previous_application_clean = previous_application.copy()

    annuity_cap = previous_application_clean["AMT_ANNUITY"].quantile(0.999)
    previous_application_clean = previous_application_clean[
        (previous_application_clean["AMT_ANNUITY"] > 0)
        & (previous_application_clean["AMT_ANNUITY"] <= annuity_cap)
    ]

    # Business signal: applicants with prior refusals may carry higher credit risk.
    refusal_counts = (
        previous_application[
            previous_application["NAME_CONTRACT_STATUS"] == "Refused"
        ]
        .groupby("SK_ID_CURR")
        .size()
        .reset_index(name="n_prev_refusals")
    )

    # Business signal: previous annuity size approximates prior repayment burden.
    average_annuity = (
        previous_application_clean
        .groupby("SK_ID_CURR")["AMT_ANNUITY"]
        .mean()
        .reset_index(name="avg_annuity_prev")
    )

    previous_application_features = (
        previous_application[["SK_ID_CURR"]]
        .drop_duplicates()
        .merge(refusal_counts, on="SK_ID_CURR", how="left")
        .merge(average_annuity, on="SK_ID_CURR", how="left")
    )
    previous_application_features["n_prev_refusals"] = (
        previous_application_features["n_prev_refusals"].fillna(0).astype(int)
    )

    return previous_application_features
