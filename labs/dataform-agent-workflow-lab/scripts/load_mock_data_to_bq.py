from __future__ import annotations

import os
from pathlib import Path

from google.cloud import bigquery

LAB_DIR = Path(__file__).resolve().parents[1]
MOCK_DATA = LAB_DIR / "tests" / "mock_data" / "raw_order_events.csv"

SCHEMA = [
    bigquery.SchemaField("order_id", "STRING"),
    bigquery.SchemaField("customer_id", "STRING"),
    bigquery.SchemaField("order_ts", "TIMESTAMP"),
    bigquery.SchemaField("status", "STRING"),
    bigquery.SchemaField("amount", "NUMERIC"),
    bigquery.SchemaField("discount_amount", "NUMERIC"),
    bigquery.SchemaField("currency", "STRING"),
    bigquery.SchemaField("updated_at", "TIMESTAMP"),
]


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def main() -> int:
    project_id = env("GCP_PROJECT_ID")
    source_dataset = env("BQ_SOURCE_DATASET")
    location = os.getenv("BQ_LOCATION", "australia-southeast1")

    client = bigquery.Client(project=project_id, location=location)
    dataset_ref = bigquery.Dataset(f"{project_id}.{source_dataset}")
    dataset_ref.location = location
    client.create_dataset(dataset_ref, exists_ok=True)

    table_id = f"{project_id}.{source_dataset}.raw_order_events"
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        schema=SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    with MOCK_DATA.open("rb") as fh:
        job = client.load_table_from_file(fh, table_id, job_config=job_config)
    job.result()
    table = client.get_table(table_id)
    print(f"Loaded {table.num_rows} rows into {table_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
