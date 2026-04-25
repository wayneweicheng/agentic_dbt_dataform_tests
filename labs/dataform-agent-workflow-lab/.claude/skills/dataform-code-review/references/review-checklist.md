# Dataform Code Review Checklist

## Business correctness

- Every business rule in the tech spec is implemented or listed as unresolved.
- Filters do not accidentally remove valid rows.
- Deduplication ordering is deterministic.
- Null handling is explicit.
- Aggregation grain matches the target contract.

## Dataform quality

- Source declarations are separate from output models.
- Model names are readable and stable.
- Dependencies use Dataform references where practical.
- SQL is compatible with BigQuery.

## Testability

- Each acceptance criterion maps to at least one scenario.
- Mock data covers positive and negative cases.
- Expected output is at the same grain as the model.
