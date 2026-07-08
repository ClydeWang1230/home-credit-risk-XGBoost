from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_sql_reports():
    base_table_path = PROJECT_ROOT / "outputs" / "sql_reports" / "risk_analytics_base.csv"
    sql_dir = PROJECT_ROOT / "sql_queries"
    output_dir = PROJECT_ROOT / "outputs" / "sql_reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("input base table path:", base_table_path)

    sql_reports = [
        (
            sql_dir / "01_risk_band_portfolio_summary.sql",
            output_dir / "01_risk_band_portfolio_summary.csv",
        ),
        (
            sql_dir / "02_income_type_risk_summary.sql",
            output_dir / "02_income_type_risk_summary.csv",
        ),
        (
            sql_dir / "03_high_risk_flag_summary.sql",
            output_dir / "03_high_risk_flag_summary.csv",
        ),
    ]

    base_table_sql_path = str(base_table_path).replace("\\", "/").replace("'", "''")

    with duckdb.connect() as connection:
        connection.execute(
            f"""
            CREATE OR REPLACE TABLE risk_analytics_base AS
            SELECT *
            FROM read_csv_auto('{base_table_sql_path}')
            """
        )

        for sql_path, output_path in sql_reports:
            print("executing SQL file:", sql_path)
            sql = sql_path.read_text(encoding="utf-8")
            report_df = connection.execute(sql).fetchdf()
            report_df.to_csv(output_path, index=False)
            print("output CSV path:", output_path)
            print("output dataframe shape:", report_df.shape)


if __name__ == "__main__":
    run_sql_reports()
