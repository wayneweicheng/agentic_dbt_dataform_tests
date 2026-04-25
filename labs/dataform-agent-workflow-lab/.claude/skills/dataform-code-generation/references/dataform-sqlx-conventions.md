# Dataform SQLX Conventions

## Role of this skill

This skill provides reusable procedures, templates, and helper scripts for generating Dataform SQLX.

It does not own the project implementation files. Actual generated or example Dataform models live under the project-level `dataform/definitions/` folder.

## SQLX conventions

- Use `config { type: "table" }` for materialized target marts.
- Use `config { type: "declaration" }` for external/source tables.
- Use `${ref("model_name")}` for dependencies.
- Prefer named CTEs for each business-rule stage.
- Keep output grain explicit in the SQL comments or codegen notes.
- Keep target schema and source dataset configurable via Dataform settings or vars.

## Recommended CTE order

1. source selection
2. deduplication
3. filtering and validity rules
4. business transformations
5. aggregation
6. final projection
