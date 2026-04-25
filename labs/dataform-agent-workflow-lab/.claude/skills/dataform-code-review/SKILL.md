---
name: dataform-code-review
description: Review Dataform SQLX against a technical specification and testing requirements.
---

# Dataform Code Review Skill

Use this skill to review Dataform SQLX implementation.

## Checklist

1. Business rules from the spec are covered.
2. Deduplication logic is deterministic.
3. Null and invalid-row handling is explicit.
4. Aggregation grain is correct.
5. Output columns match the target contract.
6. SQL is BigQuery-compatible.
7. Source references are suitable for lab datasets.
8. Scenario coverage is sufficient.

## Output format

- status
- blocking issues
- non-blocking issues
- missing test coverage
- suggested fixes
