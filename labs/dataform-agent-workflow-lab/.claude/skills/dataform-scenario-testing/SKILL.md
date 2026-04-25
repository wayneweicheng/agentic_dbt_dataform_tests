---
name: dataform-scenario-testing
description: Compare Dataform model output with expected scenario results using local or BigQuery helpers.
---

# Dataform Scenario Testing Skill

Use this skill when validating a Dataform model against scenario data.

## Local path

1. Use CSV files under `tests/mock_data` and `tests/expected`.
2. Run `python scripts/local_duckdb_validate.py`.
3. Summarize row-level differences.

## BigQuery path

1. Confirm lab dataset environment variables are set.
2. Load mock data using `scripts/load_mock_data_to_bq.py`.
3. Run Dataform from the `dataform` folder.
4. Compare results with `scripts/compare_bigquery_results.py`.

## Report

Write `tests/reports/scenario-test-report.md` with scenario coverage and result status.
