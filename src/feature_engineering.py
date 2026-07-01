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

    # Business signal: total prior applications captures historical credit demand.
    application_counts = (
        previous_application
        .groupby("SK_ID_CURR")
        .size()
        .reset_index(name="n_prev_applications")
    )

    # Business signal: prior approvals indicate historical access to credit.
    approval_counts = (
        previous_application[
            previous_application["NAME_CONTRACT_STATUS"] == "Approved"
        ]
        .groupby("SK_ID_CURR")
        .size()
        .reset_index(name="n_prev_approved")
    )

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

    # Business signal: average prior credit amount reflects typical borrowing size.
    average_credit = (
        previous_application
        .groupby("SK_ID_CURR")["AMT_CREDIT"]
        .mean()
        .reset_index(name="avg_credit_prev")
    )

    # Business signal: maximum prior credit amount captures peak historical exposure.
    maximum_credit = (
        previous_application
        .groupby("SK_ID_CURR")["AMT_CREDIT"]
        .max()
        .reset_index(name="max_credit_prev")
    )

    # Business signal: average down payment may indicate borrower liquidity.
    average_down_payment = (
        previous_application
        .groupby("SK_ID_CURR")["AMT_DOWN_PAYMENT"]
        .mean()
        .reset_index(name="avg_down_payment_prev")
    )

    previous_application_features = (
        previous_application[["SK_ID_CURR"]]
        .drop_duplicates()
        .merge(application_counts, on="SK_ID_CURR", how="left")
        .merge(approval_counts, on="SK_ID_CURR", how="left")
        .merge(refusal_counts, on="SK_ID_CURR", how="left")
        .merge(average_annuity, on="SK_ID_CURR", how="left")
        .merge(average_credit, on="SK_ID_CURR", how="left")
        .merge(maximum_credit, on="SK_ID_CURR", how="left")
        .merge(average_down_payment, on="SK_ID_CURR", how="left")
    )
    previous_application_features["n_prev_applications"] = (
        previous_application_features["n_prev_applications"].fillna(0).astype(int)
    )
    previous_application_features["n_prev_approved"] = (
        previous_application_features["n_prev_approved"].fillna(0).astype(int)
    )
    previous_application_features["n_prev_refusals"] = (
        previous_application_features["n_prev_refusals"].fillna(0).astype(int)
    )
    previous_application_features["prev_approval_rate"] = (
        previous_application_features["n_prev_approved"]
        / previous_application_features["n_prev_applications"]
    ).fillna(0)
    previous_application_features["prev_refusal_rate"] = (
        previous_application_features["n_prev_refusals"]
        / previous_application_features["n_prev_applications"]
    ).fillna(0)
    previous_application_features[
        ["avg_credit_prev", "max_credit_prev", "avg_down_payment_prev"]
    ] = previous_application_features[
        ["avg_credit_prev", "max_credit_prev", "avg_down_payment_prev"]
    ].fillna(0)

    return previous_application_features
