from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap


def _get_binary_shap_values(shap_values):
    if isinstance(shap_values, list):
        if len(shap_values) > 1:
            return shap_values[1]
        return shap_values[0]

    shap_values_array = np.asarray(shap_values)
    if shap_values_array.ndim == 3:
        if shap_values_array.shape[2] > 1:
            return shap_values_array[:, :, 1]
        return shap_values_array[:, :, 0]

    return shap_values_array


def generate_shap_reports(
    model,
    X,
    output_report_dir="outputs/reports",
    output_plot_dir="outputs/plots",
    sample_size=5000,
    random_state=42,
    overwrite_plots=False
):
    output_report_dir = Path(output_report_dir)
    output_plot_dir = Path(output_plot_dir)
    output_report_dir.mkdir(parents=True, exist_ok=True)
    output_plot_dir.mkdir(parents=True, exist_ok=True)

    def should_save_plot(plot_path):
        if plot_path.exists() and not overwrite_plots:
            print("Skipping existing plot:", plot_path)
            return False
        return True

    if len(X) > sample_size:
        X_sample = X.sample(n=sample_size, random_state=random_state)
    else:
        X_sample = X.copy()

    print("SHAP sample shape:", X_sample.shape)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)
    shap_values_for_plot = _get_binary_shap_values(shap_values)

    shap_global_importance = pd.DataFrame({
        "feature": X_sample.columns,
        "mean_abs_shap": np.abs(shap_values_for_plot).mean(axis=0),
    }).sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)
    shap_global_importance["shap_rank"] = shap_global_importance.index + 1

    shap_importance_path = output_report_dir / "shap_global_importance.csv"
    shap_global_importance.to_csv(shap_importance_path, index=False)
    print("shap_global_importance.csv saved path:", shap_importance_path)

    summary_bar_path = output_plot_dir / "shap_summary_bar.png"
    if should_save_plot(summary_bar_path):
        shap.summary_plot(
            shap_values_for_plot,
            X_sample,
            plot_type="bar",
            show=False
        )
        plt.savefig(summary_bar_path, bbox_inches="tight")
        plt.close()
        print("SHAP plot saved path:", summary_bar_path)

    summary_beeswarm_path = output_plot_dir / "shap_summary_beeswarm.png"
    if should_save_plot(summary_beeswarm_path):
        shap.summary_plot(shap_values_for_plot, X_sample, show=False)
        plt.savefig(summary_beeswarm_path, bbox_inches="tight")
        plt.close()
        print("SHAP plot saved path:", summary_beeswarm_path)

    dependence_features = [
        "prev_refusal_rate",
        "avg_down_payment_prev",
        "credit_goods_ratio",
        "credit_annuity_ratio",
        "bureau_debt_credit_ratio",
    ]
    for feature in dependence_features:
        if feature not in X_sample.columns:
            continue

        dependence_path = output_plot_dir / f"shap_dependence_{feature}.png"
        if should_save_plot(dependence_path):
            shap.dependence_plot(
                feature,
                shap_values_for_plot,
                X_sample,
                show=False
            )
            plt.savefig(dependence_path, bbox_inches="tight")
            plt.close()
            print("SHAP plot saved path:", dependence_path)

    feature = "avg_down_payment_prev"
    if feature in X_sample.columns:
        p99_value = X_sample[feature].dropna().quantile(0.99)
        p99_mask = X_sample[feature].notna() & (X_sample[feature] <= p99_value)
        print(f"{feature} p99 threshold:", p99_value)
        print(f"{feature} p99 clipped rows kept:", int(p99_mask.sum()))

        if p99_mask.sum() > 0:
            p99_dependence_path = (
                output_plot_dir
                / "shap_dependence_avg_down_payment_prev_p99_clipped.png"
            )
            if should_save_plot(p99_dependence_path):
                X_sample_p99 = X_sample.loc[p99_mask]
                shap_values_p99 = shap_values_for_plot[p99_mask.to_numpy()]

                shap.dependence_plot(
                    feature,
                    shap_values_p99,
                    X_sample_p99,
                    show=False
                )
                plt.title("SHAP Dependence: avg_down_payment_prev (p99 clipped)")
                plt.savefig(p99_dependence_path, bbox_inches="tight")
                plt.close()
                print("SHAP p99 clipped plot saved path:", p99_dependence_path)

    filtered_dependence_features = [
        "prev_refusal_rate",
        "prev_approval_rate",
        "credit_goods_ratio",
        "credit_annuity_ratio",
        "bureau_debt_credit_ratio",
    ]
    for feature in filtered_dependence_features:
        if feature not in X_sample.columns:
            continue

        if feature in ["prev_refusal_rate", "prev_approval_rate"]:
            valid_range_mask = X_sample[feature].between(0, 1)
        else:
            valid_range_mask = X_sample[feature] >= 0

        print(f"{feature} original sample size:", len(X_sample))
        print(f"{feature} filtered sample size:", int(valid_range_mask.sum()))

        if valid_range_mask.sum() == 0:
            continue

        filtered_dependence_path = (
            output_plot_dir / f"shap_dependence_{feature}_valid_range.png"
        )
        if should_save_plot(filtered_dependence_path):
            X_sample_filtered = X_sample.loc[valid_range_mask]
            shap_values_filtered = shap_values_for_plot[valid_range_mask.to_numpy()]

            shap.dependence_plot(
                feature,
                shap_values_filtered,
                X_sample_filtered,
                show=False
            )
            plt.savefig(filtered_dependence_path, bbox_inches="tight")
            plt.close()
            print("SHAP valid-range plot saved path:", filtered_dependence_path)

    # EXT_SOURCE features are external credit score signals. These valid-range
    # plots exclude sentinel missing values for visualization clarity, but we
    # should not infer their internal economic composition.
    ext_source_features = ["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]
    for feature in ext_source_features:
        if feature not in X_sample.columns:
            continue

        valid_range_mask = X_sample[feature].notna() & X_sample[feature].between(0, 1)
        print(f"{feature} original sample size:", len(X_sample))
        print(
            f"{feature} filtered valid-range sample size:",
            int(valid_range_mask.sum())
        )

        if valid_range_mask.sum() == 0:
            continue

        ext_source_path = output_plot_dir / f"shap_dependence_{feature}_valid_range.png"
        if should_save_plot(ext_source_path):
            X_sample_filtered = X_sample.loc[valid_range_mask]
            shap_values_filtered = shap_values_for_plot[valid_range_mask.to_numpy()]

            shap.dependence_plot(
                feature,
                shap_values_filtered,
                X_sample_filtered,
                show=False
            )
            plt.title(f"SHAP Dependence: {feature} (valid range)")
            plt.savefig(ext_source_path, bbox_inches="tight")
            plt.close()
            print("SHAP EXT_SOURCE valid-range plot saved path:", ext_source_path)


def generate_local_shap_examples(
    model,
    X_val,
    validation_results,
    output_report_dir="outputs/reports",
    threshold=0.15,
    top_n=8
):
    output_report_dir = Path(output_report_dir)
    output_report_dir.mkdir(parents=True, exist_ok=True)

    selected_cases = []

    true_defaults = validation_results[validation_results["TARGET"] == 1]
    if not true_defaults.empty:
        selected_cases.append((
            "high_risk_true_default",
            true_defaults["risk_score"].idxmax(),
            "Highest-scored observed default in the validation set.",
        ))

    true_non_defaults = validation_results[validation_results["TARGET"] == 0]
    if not true_non_defaults.empty:
        selected_cases.append((
            "low_risk_true_non_default",
            true_non_defaults["risk_score"].idxmin(),
            "Lowest-scored observed non-default in the validation set.",
        ))

    borderline_index = (
        validation_results["risk_score"].sub(threshold).abs().idxmin()
    )
    selected_cases.append((
        "borderline_threshold_case",
        borderline_index,
        "Validation applicant closest to the candidate risk threshold.",
    ))

    false_positives = validation_results[
        (validation_results["TARGET"] == 0)
        & (validation_results["risk_score"] >= threshold)
    ]
    if not false_positives.empty:
        selected_cases.append((
            "false_positive_high_risk_non_default",
            false_positives["risk_score"].idxmax(),
            (
                "The model classified the applicant as high risk based on "
                "the 0.15 threshold, but the observed TARGET is 0."
            ),
        ))
    else:
        print("WARNING: No false positive case found for local SHAP examples.")

    false_negatives = validation_results[
        (validation_results["TARGET"] == 1)
        & (validation_results["risk_score"] < threshold)
    ]
    if not false_negatives.empty:
        selected_cases.append((
            "false_negative_low_risk_default",
            false_negatives["risk_score"].idxmin(),
            (
                "The model classified the applicant as below the 0.15 "
                "high-risk threshold, but the observed TARGET is 1."
            ),
        ))
    else:
        print("WARNING: No false negative case found for local SHAP examples.")

    selected_positions = [
        validation_results.index.get_loc(row_index)
        for _, row_index, _ in selected_cases
    ]
    X_selected = X_val.iloc[selected_positions]

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_selected)
    shap_values_for_selected = _get_binary_shap_values(shap_values)

    csv_rows = []
    markdown_lines = [
        "# Local SHAP Examples",
        "",
        (
            "Some feature values such as `-999` or `-1000` represent "
            "missing, unavailable, or no-history information rather than "
            "actual economic values. In addition, dataset-specific special "
            "encoded values such as `DAYS_EMPLOYED = 365243` should not be "
            "interpreted literally. Local SHAP contributors with these "
            "values should be interpreted as missing-value or "
            "special-encoding signals rather than direct business-value "
            "effects."
        ),
        "",
        "## Diagnostic Case Notes",
        "",
        (
            "- False positive: The model classified the applicant as high "
            "risk based on the 0.15 threshold, but the observed TARGET is 0."
        ),
        (
            "- False negative: The model classified the applicant as below "
            "the 0.15 high-risk threshold, but the observed TARGET is 1."
        ),
        "",
    ]

    for case_position, (case_type, row_index, interpretation) in enumerate(
        selected_cases
    ):
        result_row = validation_results.loc[row_index]
        applicant_id = result_row["SK_ID_CURR"]
        print(f"{case_type} selected SK_ID_CURR:", applicant_id)

        applicant_features = X_selected.iloc[case_position]
        applicant_shap_values = shap_values_for_selected[case_position]

        shap_detail = pd.DataFrame({
            "feature": X_selected.columns,
            "feature_value": applicant_features.values,
            "shap_value": applicant_shap_values,
        })
        shap_detail["value_status"] = np.select(
            [
                shap_detail["feature_value"].isin([-999, -1000]),
                (
                    (shap_detail["feature"] == "DAYS_EMPLOYED")
                    & (shap_detail["feature_value"] == 365243)
                ),
            ],
            ["sentinel_missing", "special_encoded_value"],
            default="actual_value"
        )
        positive_drivers = (
            shap_detail[shap_detail["shap_value"] > 0]
            .sort_values("shap_value", ascending=False)
            .head(top_n)
        )
        negative_drivers = (
            shap_detail[shap_detail["shap_value"] < 0]
            .sort_values("shap_value", ascending=True)
            .head(top_n)
        )

        markdown_lines.extend([
            f"## {case_type}",
            "",
            f"- SK_ID_CURR: {applicant_id}",
            f"- TARGET: {result_row['TARGET']}",
            f"- risk_score: {result_row['risk_score']:.6f}",
            f"- Interpretation: {interpretation}",
            "",
            "### Top Positive Risk Drivers",
            "",
        ])

        for rank, (_, driver_row) in enumerate(
            positive_drivers.iterrows(),
            start=1
        ):
            csv_rows.append({
                "case_type": case_type,
                "SK_ID_CURR": applicant_id,
                "TARGET": result_row["TARGET"],
                "risk_score": result_row["risk_score"],
                "threshold": threshold,
                "feature": driver_row["feature"],
                "feature_value": driver_row["feature_value"],
                "value_status": driver_row["value_status"],
                "shap_value": driver_row["shap_value"],
                "contribution_direction": "positive_risk_driver",
                "contribution_rank": rank,
            })
            if driver_row["value_status"] == "sentinel_missing":
                value_text = (
                    f"value=missing/sentinel, "
                    f"raw_value={driver_row['feature_value']}"
                )
            elif driver_row["value_status"] == "special_encoded_value":
                value_text = (
                    "value=special encoded value, "
                    f"raw_value={driver_row['feature_value']}"
                )
            else:
                value_text = f"value={driver_row['feature_value']}"
            markdown_lines.append(
                f"{rank}. `{driver_row['feature']}` "
                f"({value_text}, SHAP={driver_row['shap_value']:.6f})"
            )

        markdown_lines.extend(["", "### Top Negative Risk Drivers", ""])

        for rank, (_, driver_row) in enumerate(
            negative_drivers.iterrows(),
            start=1
        ):
            csv_rows.append({
                "case_type": case_type,
                "SK_ID_CURR": applicant_id,
                "TARGET": result_row["TARGET"],
                "risk_score": result_row["risk_score"],
                "threshold": threshold,
                "feature": driver_row["feature"],
                "feature_value": driver_row["feature_value"],
                "value_status": driver_row["value_status"],
                "shap_value": driver_row["shap_value"],
                "contribution_direction": "negative_risk_driver",
                "contribution_rank": rank,
            })
            if driver_row["value_status"] == "sentinel_missing":
                value_text = (
                    f"value=missing/sentinel, "
                    f"raw_value={driver_row['feature_value']}"
                )
            elif driver_row["value_status"] == "special_encoded_value":
                value_text = (
                    "value=special encoded value, "
                    f"raw_value={driver_row['feature_value']}"
                )
            else:
                value_text = f"value={driver_row['feature_value']}"
            markdown_lines.append(
                f"{rank}. `{driver_row['feature']}` "
                f"({value_text}, SHAP={driver_row['shap_value']:.6f})"
            )

        markdown_lines.append("")

    local_examples_path = output_report_dir / "local_shap_examples.csv"
    pd.DataFrame(csv_rows).to_csv(local_examples_path, index=False)
    print("Local SHAP examples CSV saved path:", local_examples_path)

    local_examples_markdown_path = output_report_dir / "local_shap_examples.md"
    local_examples_markdown_path.write_text(
        "\n".join(markdown_lines),
        encoding="utf-8"
    )
    print("Local SHAP examples Markdown saved path:", local_examples_markdown_path)
