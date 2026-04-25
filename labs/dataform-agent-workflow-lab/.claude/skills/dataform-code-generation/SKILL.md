---
name: dataform-code-generation
description: Generate Dataform SQLX models from a structured technical specification.
---

# Dataform Code Generation Skill

Use this skill when implementing a Dataform pipeline from a tech spec.

## Output expectations

- SQLX files under `dataform/definitions/`.
- Notes under `outputs/codegen-notes.md`.

## Dataform conventions

1. Prefer one clear output model per target table.
2. Use CTEs for deduplication, business-rule filtering, and aggregation.
3. Use `${ref("source_or_model")}` for Dataform dependencies where possible.
4. Use BigQuery-compatible SQL.
5. Keep target grain explicit in comments.
6. Do not create destructive operations.

## Review checklist before finishing

- All business rules from the spec are covered.
- Deduplication logic is deterministic.
- Null handling is explicit.
- Output columns match the target contract.
- Scenario tests can map to the implementation.
