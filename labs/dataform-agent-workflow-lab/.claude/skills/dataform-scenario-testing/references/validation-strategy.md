# Dataform Scenario Validation Strategy

## Local validation

Use local validation for fast feedback. The lab uses DuckDB to mirror the Dataform SQL logic against CSV mock data.

## BigQuery validation

Use BigQuery validation when you need to test the actual Dataform execution path.

## Recommended sequence

1. Create mock source data.
2. Create expected target data.
3. Run local validator.
4. Review row differences.
5. Only then use the BigQuery path when needed.

## Report expectations

A validation report should include:

- status
- scenarios covered
- actual row count
- expected row count
- differences or manual review notes
