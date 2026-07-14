# Local SHAP Examples

Some feature values such as `-999` or `-1000` represent missing, unavailable, or no-history information rather than actual economic values. In addition, dataset-specific special encoded values such as `DAYS_EMPLOYED = 365243` should not be interpreted literally. Local SHAP contributors with these values should be interpreted as missing-value or special-encoding signals rather than direct business-value effects.

## Diagnostic Case Notes

- False positive: The model classified the applicant as high risk based on the 0.15 threshold, but the observed TARGET is 0.
- False negative: The model classified the applicant as below the 0.15 high-risk threshold, but the observed TARGET is 1.

## high_risk_true_default

- SK_ID_CURR: 156227.0
- TARGET: 1.0
- risk_score: 0.700430
- Interpretation: Highest-scored observed default in the validation set.

### Top Positive Risk Drivers

1. `EXT_SOURCE_2` (value=1.1793951733999552e-05, SHAP=0.918471)
2. `EXT_SOURCE_3` (value=0.0371194125972502, SHAP=0.858204)
3. `total_overdue_amount` (value=131728.5, SHAP=0.365712)
4. `n_active_bureau_credits` (value=9.0, SHAP=0.251725)
5. `credit_goods_ratio` (value=1.2112, SHAP=0.164678)
6. `EXT_SOURCE_1` (value=missing/sentinel, raw_value=-999.0, SHAP=0.125758)
7. `AMT_GOODS_PRICE` (value=450000.0, SHAP=0.089100)
8. `credit_annuity_ratio` (value=19.59553470312247, SHAP=0.083841)

### Top Negative Risk Drivers

1. `bureau_debt_credit_ratio` (value=0.3197038327869822, SHAP=-0.092712)
2. `prev_refusal_rate` (value=missing/sentinel, raw_value=-999.0, SHAP=-0.062545)
3. `DAYS_BIRTH` (value=-8418.0, SHAP=-0.062294)
4. `FLAG_WORK_PHONE` (value=0.0, SHAP=-0.025317)
5. `max_credit_prev` (value=missing/sentinel, raw_value=-999.0, SHAP=-0.018911)
6. `DEF_30_CNT_SOCIAL_CIRCLE` (value=0.0, SHAP=-0.015314)
7. `days_decision_mean` (value=missing/sentinel, raw_value=-999.0, SHAP=-0.010856)
8. `REGION_RATING_CLIENT_W_CITY` (value=2.0, SHAP=-0.009897)

## low_risk_true_non_default

- SK_ID_CURR: 101372.0
- TARGET: 0.0
- risk_score: 0.004078
- Interpretation: Lowest-scored observed non-default in the validation set.

### Top Positive Risk Drivers

1. `DAYS_BIRTH` (value=-13418.0, SHAP=0.030438)
2. `avg_annuity_prev` (value=8423.369999999999, SHAP=0.020837)
3. `FLAG_DOCUMENT_3` (value=1.0, SHAP=0.012690)
4. `REGION_POPULATION_RELATIVE` (value=0.019101, SHAP=0.010376)
5. `AMT_GOODS_PRICE` (value=112500.0, SHAP=0.007724)
6. `FLAG_EMP_PHONE` (value=1.0, SHAP=0.007161)
7. `AMT_REQ_CREDIT_BUREAU_QRT` (value=0.0, SHAP=0.005633)
8. `avg_days_credit_update` (value=-359.8, SHAP=0.004224)

### Top Negative Risk Drivers

1. `EXT_SOURCE_2` (value=0.7335216416596809, SHAP=-0.589878)
2. `EXT_SOURCE_1` (value=0.7015658649637986, SHAP=-0.496868)
3. `credit_annuity_ratio` (value=10.007072135785007, SHAP=-0.413884)
4. `EXT_SOURCE_3` (value=0.6397075677637197, SHAP=-0.392683)
5. `DAYS_EMPLOYED` (value=-6589.0, SHAP=-0.259007)
6. `AMT_ANNUITY` (value=12726.0, SHAP=-0.151765)
7. `YEARS_BEGINEXPLUATATION_MODE` (value=0.9896, SHAP=-0.092395)
8. `avg_down_payment_prev` (value=11621.8125, SHAP=-0.090218)

## borderline_threshold_case

- SK_ID_CURR: 429642.0
- TARGET: 0.0
- risk_score: 0.149998
- Interpretation: Validation applicant closest to the candidate risk threshold.

### Top Positive Risk Drivers

1. `EXT_SOURCE_3` (value=0.237916079507114, SHAP=0.432348)
2. `n_active_bureau_credits` (value=7.0, SHAP=0.229722)
3. `credit_goods_ratio` (value=1.396, SHAP=0.205410)
4. `bureau_debt_credit_ratio` (value=0.45461541319265697, SHAP=0.146956)
5. `EXT_SOURCE_1` (value=missing/sentinel, raw_value=-999.0, SHAP=0.106632)
6. `AMT_ANNUITY` (value=36864.0, SHAP=0.101706)
7. `DAYS_BIRTH` (value=-15065.0, SHAP=0.055803)
8. `DEF_30_CNT_SOCIAL_CIRCLE` (value=1.0, SHAP=0.042956)

### Top Negative Risk Drivers

1. `EXT_SOURCE_2` (value=0.5970969356289159, SHAP=-0.195103)
2. `credit_annuity_ratio` (value=34.08203125, SHAP=-0.123338)
3. `DAYS_EMPLOYED` (value=-3755.0, SHAP=-0.084831)
4. `AMT_GOODS_PRICE` (value=900000.0, SHAP=-0.068248)
5. `max_credit_prev` (value=225000.0, SHAP=-0.058033)
6. `avg_down_payment_prev` (value=5381.955, SHAP=-0.039345)
7. `AMT_REQ_CREDIT_BUREAU_QRT` (value=3.0, SHAP=-0.037282)
8. `n_prev_approved` (value=6.0, SHAP=-0.034884)

## false_positive_high_risk_non_default

- SK_ID_CURR: 280436.0
- TARGET: 0.0
- risk_score: 0.714646
- Interpretation: The model classified the applicant as high risk based on the 0.15 threshold, but the observed TARGET is 0.

### Top Positive Risk Drivers

1. `EXT_SOURCE_3` (value=0.0744606878956731, SHAP=0.891663)
2. `EXT_SOURCE_2` (value=0.0887619377448496, SHAP=0.768572)
3. `n_active_bureau_credits` (value=10.0, SHAP=0.467122)
4. `prev_refusal_rate` (value=0.6666666666666666, SHAP=0.329135)
5. `credit_goods_ratio` (value=1.2112, SHAP=0.151697)
6. `credit_annuity_ratio` (value=21.45235565001771, SHAP=0.137280)
7. `credit_income_ratio` (value=17.302857142857142, SHAP=0.103487)
8. `bureau_debt_credit_ratio` (value=0.5313791882884868, SHAP=0.090961)

### Top Negative Risk Drivers

1. `DAYS_BIRTH` (value=-21824.0, SHAP=-0.174475)
2. `DAYS_ID_PUBLISH` (value=-4819.0, SHAP=-0.028615)
3. `max_credit_prev` (value=72387.0, SHAP=-0.026693)
4. `FLAG_WORK_PHONE` (value=0.0, SHAP=-0.022850)
5. `avg_credit_prev` (value=24129.0, SHAP=-0.022489)
6. `avg_credit_sum` (value=125134.00714285715, SHAP=-0.011366)
7. `HOUR_APPR_PROCESS_START` (value=7.0, SHAP=-0.010841)
8. `REG_CITY_NOT_LIVE_CITY` (value=0.0, SHAP=-0.010007)

## false_negative_low_risk_default

- SK_ID_CURR: 283795.0
- TARGET: 1.0
- risk_score: 0.009491
- Interpretation: The model classified the applicant as below the 0.15 high-risk threshold, but the observed TARGET is 1.

### Top Positive Risk Drivers

1. `DAYS_EMPLOYED` (value=special encoded value, raw_value=365243.0, SHAP=0.065478)
2. `AMT_CREDIT` (value=679500.0, SHAP=0.016835)
3. `FLAG_DOCUMENT_3` (value=1.0, SHAP=0.011427)
4. `REGION_POPULATION_RELATIVE` (value=0.026392, SHAP=0.007736)
5. `credit_income_ratio` (value=4.314285714285714, SHAP=0.006743)
6. `YEARS_BEGINEXPLUATATION_MODE` (value=0.9871, SHAP=0.005744)
7. `avg_annuity_prev` (value=9196.065, SHAP=0.004365)
8. `income_per_family_member` (value=78750.0, SHAP=0.001599)

### Top Negative Risk Drivers

1. `EXT_SOURCE_1` (value=0.8640769612906921, SHAP=-0.498836)
2. `EXT_SOURCE_3` (value=0.6075573001388961, SHAP=-0.369110)
3. `EXT_SOURCE_2` (value=0.6660534511073483, SHAP=-0.360819)
4. `avg_down_payment_prev` (value=16791.704999999998, SHAP=-0.159540)
5. `credit_goods_ratio` (value=1.0, SHAP=-0.118710)
6. `AMT_GOODS_PRICE` (value=679500.0, SHAP=-0.095853)
7. `OWN_CAR_AGE` (value=8.0, SHAP=-0.079992)
8. `credit_annuity_ratio` (value=33.986045464776055, SHAP=-0.073421)
