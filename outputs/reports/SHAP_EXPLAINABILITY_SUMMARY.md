# SHAP Explainability Summary

## 1. Purpose

This document summarizes the SHAP explainability layer for the Home Credit Risk XGBoost project.

The goal of the SHAP layer is to explain how the trained model uses different credit risk signals to estimate default risk. Instead of only reporting predictive performance or feature importance, SHAP helps answer three business-facing questions:

1. Which features matter most globally?
2. How do key engineered features push predicted risk up or down?
3. Can individual applicant-level predictions be explained in a transparent way?

This supports the project goal of building a credit risk analytics pipeline that is not only predictive, but also interpretable for analysts, lenders, and future AI-assisted review workflows.

---

## 2. Generated SHAP Outputs

The current SHAP workflow generates the following outputs:

```text
outputs/reports/shap_global_importance.csv
outputs/plots/shap_summary_bar.png
outputs/plots/shap_summary_beeswarm.png
outputs/plots/shap_dependence_*.png
outputs/reports/local_shap_examples.csv
outputs/reports/local_shap_examples.md

The main outputs are:

shap_global_importance.csv: numerical global SHAP importance ranked by mean absolute SHAP value.
shap_summary_bar.png: bar chart version of global SHAP importance.
shap_summary_beeswarm.png: global feature impact plot showing both feature importance and directional effect.
SHAP dependence plots: feature-level plots showing how selected feature values affect model risk contribution.
local_shap_examples.csv and .md: applicant-level explanations for selected validation cases.
3. How to Read the SHAP Results

SHAP values explain how each feature contributes to the model output for predicted default risk.

In this project:

Positive SHAP value means the feature pushes the prediction toward higher default risk.
Negative SHAP value means the feature pushes the prediction toward lower default risk.
Larger absolute SHAP value means the feature has a stronger impact on the model output.

The global SHAP importance report uses mean_abs_shap, which measures the average absolute contribution of each feature across the sampled records. It ranks features by impact size, but does not show direction.

The beeswarm and dependence plots add directional interpretation.

4. Global SHAP Findings

The global SHAP results show that the strongest model drivers are:

EXT_SOURCE_3
EXT_SOURCE_2
EXT_SOURCE_1
credit_goods_ratio
credit_annuity_ratio
bureau_debt_credit_ratio
AMT_ANNUITY
DAYS_EMPLOYED
DAYS_BIRTH
avg_down_payment_prev
prev_refusal_rate

This indicates that the model relies on a combination of:

external credit source signals,
current loan structure,
repayment burden,
external bureau debt pressure,
demographic and employment-related variables,
previous application behavior,
historical down payment capacity.

This is a positive result for model interpretability because many of the top features align with credit risk intuition instead of being purely technical or opaque model artifacts.

5. External Source Features

EXT_SOURCE_1, EXT_SOURCE_2, and EXT_SOURCE_3 are the top-ranked global SHAP features.

Valid-range SHAP dependence plots were generated for these features using only values between 0 and 1, excluding sentinel missing values.

The plots show a clear downward relationship:

Lower external source values produce positive SHAP contributions and increase predicted default risk.
Higher external source values produce negative SHAP contributions and reduce predicted default risk.

This suggests that the model treats the external source variables as strong external credit quality signals.

However, the internal composition of these variables is not disclosed in the dataset. Therefore, they should be interpreted as opaque external credit score signals rather than decomposed into specific economic drivers.

A suitable business interpretation is:

External source features are strong predictors of default risk. Higher external source values generally reduce the model’s predicted default risk, while lower values increase risk. Since their internal definitions are not disclosed, they are interpreted only as external credit signal variables.

6. Engineered Feature SHAP Findings
6.1 credit_goods_ratio

credit_goods_ratio measures credit amount relative to goods price.

The SHAP dependence plot shows a clear non-linear positive risk pattern. When the ratio is close to or below normal financing levels, the SHAP contribution is generally limited or negative. As the ratio rises above roughly 1.1–1.2, the feature increasingly contributes positively to predicted default risk.

This supports the interpretation that higher financing coverage relative to goods price may indicate weaker borrower self-funding capacity and higher credit risk.

Business interpretation:

Higher credit_goods_ratio means the applicant is financing a larger share of the goods price. The model treats this as a risk-increasing signal when the ratio becomes elevated.

6.2 bureau_debt_credit_ratio

bureau_debt_credit_ratio measures external bureau debt burden relative to credit exposure.

The original dependence plot was affected by sentinel missing values such as -999 or -1000. After filtering to a valid business range, the relationship becomes much clearer.

The valid-range SHAP dependence plot shows a strong positive relationship:

Lower bureau debt-to-credit ratios generally have limited or negative SHAP contributions.
Higher ratios increasingly contribute positively to predicted default risk.

This supports the business interpretation that higher external debt burden is a meaningful credit risk signal.

Business interpretation:

Applicants with higher external bureau debt burden relative to credit exposure receive higher model risk contributions, suggesting greater repayment pressure and higher default risk.

6.3 prev_refusal_rate

prev_refusal_rate measures the share of previous applications that were refused.

The original dependence plot was distorted by sentinel missing values. After restricting the plot to the valid 0–1 range, the relationship becomes clear.

The valid-range SHAP dependence plot shows a strong positive relationship:

Low or zero previous refusal rate generally contributes little or negatively to risk.
Higher previous refusal rate contributes increasingly positively to predicted default risk.

This aligns strongly with credit risk intuition. A borrower who has been refused more often in previous applications may have a weaker historical credit profile.

Business interpretation:

Higher historical refusal rate increases the model’s predicted default risk contribution, validating prev_refusal_rate as an interpretable previous-application risk signal.

6.4 prev_approval_rate

prev_approval_rate measures the share of previous applications that were approved.

This feature shows the opposite pattern of prev_refusal_rate.

The SHAP dependence plot shows that:

Lower previous approval rates tend to increase predicted default risk.
Higher previous approval rates generally reduce predicted default risk.

This suggests that stronger historical lender acceptance is associated with lower modeled risk.

Business interpretation:

Applicants with higher historical approval rates are treated as lower risk by the model, while low approval rates act as a risk-increasing signal.

6.5 avg_down_payment_prev

avg_down_payment_prev measures historical average down payment in previous applications.

The full-range dependence plot was affected by a small number of very large values. These values were not treated as invalid because large down payments can be genuine business observations. Instead, an additional p99-clipped dependence plot was created for readability.

The p99-clipped plot shows a clear overall downward pattern:

Higher historical average down payment tends to receive more negative SHAP contributions.
Lower down payment levels show more variable and sometimes higher risk contributions.

This supports the interpretation that stronger historical down payment capacity may indicate better borrower liquidity or self-funding ability.

Business interpretation:

Higher historical average down payment generally reduces the model’s predicted default risk contribution, suggesting that prior self-funding capacity can act as a risk-mitigating signal.

The interaction color in this plot does not show a strong separable pattern, so the main takeaway is the standalone effect of avg_down_payment_prev rather than a strong interaction effect.

6.6 credit_annuity_ratio

credit_annuity_ratio measures credit amount relative to scheduled annuity payment. It can be interpreted as a rough repayment structure or repayment horizon signal.

The SHAP dependence plot shows a non-linear pattern rather than a simple monotonic relationship:

Lower values around the 8–10 range tend to contribute negatively.
Mid-range values around 11–20 tend to contribute positively.
Higher values above roughly 20 tend to contribute negatively again.

This shows that the model does not treat repayment structure as a simple “higher is always riskier” relationship. Instead, risk contribution varies across ranges.

Business interpretation:

credit_annuity_ratio affects model risk estimates in a non-linear way. This suggests that repayment structure should be interpreted together with affordability, loan size, annuity amount, and other applicant profile features.

This is one of the clearest examples of why SHAP is useful: it reveals non-linear model behavior that may not be obvious from simple Excel grouping or linear feature intuition.

7. Visualization Hygiene

Several engineered features contained sentinel missing values such as -999 or -1000. These values represent missing or unavailable information and should not be interpreted as real economic values.

For example:

prev_refusal_rate = -999 does not mean refusal rate is negative.
EXT_SOURCE_1 = -999 does not mean the external score is negative.
These values indicate missing information or no available historical record.

To improve interpretability, additional valid-range dependence plots were created for bounded ratio or score features:

prev_refusal_rate
prev_approval_rate
credit_goods_ratio
credit_annuity_ratio
bureau_debt_credit_ratio
EXT_SOURCE_1
EXT_SOURCE_2
EXT_SOURCE_3

For avg_down_payment_prev, the issue was not invalid values but long-tail distribution. Therefore, a p99-clipped plot was created for visualization clarity while preserving the original full-range plot.

This distinction is important:

Valid-range plots remove invalid sentinel values.
P99-clipped plots improve readability without treating extreme values as invalid.
8. Local SHAP Explanation

In addition to global and feature-level SHAP analysis, the project now generates local applicant-level SHAP explanations.

The current local explanation output includes three representative validation cases:

High-risk true default
High risk score
TARGET = 1
Used to explain a successful high-risk identification
Low-risk true non-default
Low risk score
TARGET = 0
Used to explain a successful low-risk classification
Borderline threshold case
Risk score close to the candidate 0.15 threshold
Useful for understanding cases that may require manual review

For each selected applicant, the local SHAP report outputs:

case_type
SK_ID_CURR
TARGET
risk_score
threshold
feature
feature_value
shap_value
contribution_direction
contribution_rank

Positive SHAP contributors are interpreted as risk drivers, while negative SHAP contributors are interpreted as risk mitigants or risk-reducing signals.

The local explanation layer is especially useful for future extensions such as:

FastAPI applicant-level scoring,
human review flagging,
audit logs,
RAG / Agent-based credit risk explanation.
9. Key Takeaways

The SHAP explainability layer supports several important conclusions:

The model is strongly driven by external source features, which act as opaque but powerful external credit score signals.
Several engineered features show business-consistent SHAP patterns:
Higher prev_refusal_rate increases risk.
Higher prev_approval_rate reduces risk.
Higher bureau_debt_credit_ratio increases risk.
Higher credit_goods_ratio tends to increase risk when financing coverage becomes elevated.
Higher avg_down_payment_prev tends to reduce risk.
credit_annuity_ratio shows a non-linear repayment structure effect.
SHAP adds value beyond standard feature importance because it shows both:
feature impact size,
feature impact direction,
non-linear behavior,
applicant-level contribution.
The explainability layer helps translate model outputs into business-facing credit risk interpretation.
The project is now better positioned for future AI-assisted analyst workflows, because SHAP outputs can be used as evidence for applicant-level explanations, review recommendations, and RAG/Agent responses.

### False Positive / False Negative Diagnostics

False positive and false negative local SHAP examples were added to support model error diagnostics.
The false positive case shows an applicant who was classified as high risk by the 0.15 threshold but did not default in the observed validation label. The model’s high-risk prediction was driven by multiple risk indicators, including low external source scores, many active bureau credits, elevated previous refusal rate, high credit-to-goods financing coverage, high credit-income ratio, and moderate external debt burden. This case supports using high-risk model flags as manual review triggers rather than automatic rejection decisions.
The false negative case shows an applicant who was classified as below the 0.15 high-risk threshold but defaulted in the observed validation label. The model assigned a very low risk score because strong risk-reducing signals were present, especially high external source scores, normal credit-to-goods financing coverage, historical down payment capacity, and other low-risk structural signals. This case highlights that low model risk does not mean zero risk, and that some defaults may come from hidden risk factors, post-application changes, or signals not captured by the current feature set.
The local SHAP diagnostic examples demonstrate how applicant-level explanations can be used not only to explain correct model decisions, but also to analyze model misses. This is important for future audit logs, human review workflows, and model monitoring.

10. Next Steps

Planned improvements:

1. Add applicant-level SHAP outputs to a future FastAPI scoring endpoint.
2. Use SHAP summaries and local explanations as source material for a future RAG / Agent analyst assistant.
3. Incorporate model explanation outputs into audit-friendly review logs.
4. Build a human review workflow using risk scores, thresholds, SHAP drivers and review recommendations.
5. Continue monitoring false-positve and false-negative cases as part of future model validation and error analysis.

