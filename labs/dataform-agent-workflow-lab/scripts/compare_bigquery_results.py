from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from google.cloud import bigquery

LAB_DIR = Path(__file__).resolve().parents[1]
EXPECTED = LAB_DIR / "tests" / "expected" / "daily_customer_revenue_expected.csv"
REPORT = LAB_DIR / "tests" / "reports" / "bigquery-comparison-report.md"


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def main() -> int:
    project_id = require_env("GCP_PROJECT_ID")
    target_dataset = require_env("BQ_TARGET_DATASET")
    location = os.getenv("BQ_LOCATION", "australia-southeast1")
    table_id = f"{project_id}.{target_dataset}.daily_customer_revenue"

    client = bigquery.Client(project=project_id, location=location)
    actual = client.query(f"SELECT * FROM `{table_id}`").to_dataframe()
    expected = pd.read_csv(EXPECTED)

    actual = actual.sort_values(["order_date", "customer_id"]).reset_index(drop=True)
    expected = expected.sort_values(["order_date", "customer_id"]).reset_index(drop=True)
    passed = len(actual) == len(expected)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        f"# BigQuery Comparison Report\n\nStatus: {'passed' if passed else 'needs_manual_review'}\n\nCompared table: `{table_id}`\n\nActual rows: {len(actual)}\n\nExpected rows: {len(expected)}\n",
        encoding="utf-8",
    )
    print(f"Wrote {REPORT}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
