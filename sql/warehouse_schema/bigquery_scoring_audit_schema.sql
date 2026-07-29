-- BigQuery warehouse schema sketch for future migration planning.
-- This file is documentation-oriented and is not used by the local pipeline.
-- Replace `project_id.credit_risk_dw` with the target project and dataset before use.

CREATE TABLE IF NOT EXISTS `project_id.credit_risk_dw.scoring_events` (
  audit_log_id STRING NOT NULL,
  timestamp_utc TIMESTAMP,
  endpoint_name STRING,
  model_version STRING,
  risk_score FLOAT64,
  risk_band STRING,
  threshold_used FLOAT64,
  high_risk_flag_015 INT64,
  missing_feature_count INT64,
  unexpected_feature_count INT64,
  scoring_response_source STRING
);

CREATE TABLE IF NOT EXISTS `project_id.credit_risk_dw.shap_driver_events` (
  shap_driver_id STRING NOT NULL,
  audit_log_id STRING NOT NULL,
  feature STRING,
  feature_value FLOAT64,
  value_status STRING,
  shap_value FLOAT64,
  contribution_direction STRING,
  contribution_rank INT64
);

CREATE TABLE IF NOT EXISTS `project_id.credit_risk_dw.human_review_cases` (
  review_case_id STRING NOT NULL,
  audit_log_id STRING,
  created_at_utc TIMESTAMP,
  status STRING,
  review_priority STRING,
  review_reasons STRING,
  endpoint_name STRING,
  model_version STRING,
  risk_score FLOAT64,
  risk_band STRING
);

CREATE TABLE IF NOT EXISTS `project_id.credit_risk_dw.human_review_decisions` (
  review_decision_id STRING NOT NULL,
  review_case_id STRING NOT NULL,
  updated_at_utc TIMESTAMP,
  reviewer STRING,
  review_status STRING,
  analyst_decision STRING,
  analyst_comment STRING
);

CREATE TABLE IF NOT EXISTS `project_id.credit_risk_dw.analyst_qa_events` (
  qa_event_id STRING NOT NULL,
  timestamp_utc TIMESTAMP,
  question STRING,
  detected_intent STRING,
  answer_mode STRING,
  llm_enabled BOOL,
  llm_model STRING,
  review_case_id STRING,
  audit_log_id STRING,
  retrieved_context_count INT64,
  warnings_count INT64
);
