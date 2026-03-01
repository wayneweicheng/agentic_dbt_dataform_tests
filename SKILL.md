---
name: data-pipeline-bigquery-unit-testing
description: Generate and maintain BigQuery tests from TECHSPEC requirements for either Dataform or dbt projects with a final-output-first strategy. Use when a user provides (1) TECHSPEC.md path and (2) data pipeline project path and asks for unit tests or pytest integration tests for final models.
---

# Data Pipeline BigQuery Unit-Testing Skill

Follow these rules exactly.

1. Required inputs (must be provided before writing tests):
   - `TECHSPEC.md` path.
   - Data pipeline project path (Dataform or dbt).
   - Target model file(s) to test is optional.
   - If either required input is missing, ask for it and stop.

2. Framework detection (must happen before model discovery):
   - Read `references/framework-detection.md`.
   - Determine framework from explicit user input first, then path markers.
   - If ambiguous, ask one clarification question and stop.
   - Do not generate tests before framework is explicit.

3. Target model discovery (when target model file(s) are not provided):
   - Infer models to test from TECHSPEC first (target table/model names, data model sections, business requirement scope).
   - Resolve inferred model candidates from framework project files:
     - Dataform: `<project_path>/definitions/**/*.sqlx`
     - dbt: `<project_path>/models/**/*.sql`
   - If multiple candidates remain or mapping is ambiguous, ask a clarification question before generating tests.
   - Do not skip model discovery; do not guess silently.

4. Test mode selection policy (strict):
   - If the user asks to test **final models** and does not explicitly request framework-native unit tests, default to **integration test mode**.
   - If the user asks for source-only mocks and full-pipeline validation, use **integration test mode**:
     - Generate **pytest-based** integration tests (not shell scripts).
     - Seed source-table mocks.
     - Run framework pipeline for target final model with dependencies:
       - Dataform: `dataform run`
       - dbt: default `dbt run` (can use `dbt build` when explicitly needed)
     - Assert final output table contents with SQL diffs and per-scenario pytest cases.
   - If user asks for framework-native unit tests, use **unit test mode**:
     - Dataform: `config { type: "test" }`
     - dbt: `unit_tests:` YAML
   - Framework-native unit tests do not replace full source-mock DAG validation.

5. Integration harness bootstrap (for pytest integration mode):
   - Use the scaffold script before writing model-specific fixtures:
     - `python examples/agent_skill_unit_tests/scripts/scaffold_pytest_integration.py --project-path <project_path> --pipeline-type auto --model-name <model_name>`
   - The script auto-detects framework (or accepts explicit `--pipeline-type`).
   - Fill generated placeholders with TECHSPEC-derived values.
   - For dbt integration harness defaults:
     - `dbt_command` defaults to `run`
     - override per model config or `DBT_COMMAND=build` when required.

6. Source of truth policy (strict):
   - Use TECHSPEC as the only source of business logic and expected behavior.
   - Do **not** derive test assertions from SQL logic in the model under test.
   - Do **not** reverse-engineer filters/joins/aggregations from model SQL to invent expected outputs.
   - Do **not** use existing tests, compiled graph artifacts, or previous outputs as the source of expected logic.
   - If TECHSPEC lacks needed details, ask user to update TECHSPEC; do not fill gaps from model logic.

7. Allowed use of model files:
   - You may read model SQL only to identify technical metadata:
     - model name / output relation name
     - upstream dependency references (`${ref(...)}` or `ref(...)` / `source(...)`)
     - target test file name/location
   - You must not use model SQL semantics as the basis for expected output logic.

8. Unit testing syntax (when unit mode is requested):
   - Dataform unit mode:
     - Use `config { type: "test" }`.
     - Set `dataset` to exactly the model name being tested.
     - Allowed test config keys are only: `type`, `dataset`, optional `name`.
     - Do not include `description` in test config.
     - Use `assets/test_template.sqlx` when a scaffold template helps.
   - dbt unit mode:
     - Use dbt `unit_tests:` YAML format.
     - Set `model` to exactly the model under test.
     - Provide dependency inputs via `given` (`ref(...)`, `source(...)`, and other valid unit-test inputs).
     - Use `assets/test_template_dbt.yml` when a scaffold template helps.

9. Mocking strategy:
   - Integration mode:
     - Mock only guaranteed source schemas listed in TECHSPEC input sections and source declarations.
   - Unit mode (both frameworks):
     - Mock only direct dependencies required for isolated logic validation.
     - Do not expect full DAG execution from framework-native unit tests.
   - Build mock rows with BigQuery Standard SQL `SELECT ... UNION ALL`.
   - Cast explicit data types when needed, for example `CAST('2026-02-28' AS DATE)`.

10. Validation strategy:
   - Build expected rows from a scenario matrix derived from TECHSPEC requirements only.
   - For Dataform unit mode, end the `.sqlx` test with expected output `SELECT ... UNION ALL`.
   - For dbt unit mode, define `expect.rows` values in YAML from TECHSPEC scenarios.
   - For integration mode, create per-model SQL assets:
     - `mock_data.sql` for source seeds
     - `expected.sql` for expected final rows
     - `assert.sql` for expected-vs-actual diff query
   - Integration assertions must be executed by pytest.

11. Output location and naming:
   - Dataform unit mode:
     - Write tests under `<dataform_project_path>/definitions/tests/`.
   - dbt unit mode:
     - Write unit-test YAML under `<dbt_project_path>/models/tests/` unless user requests another valid dbt path.
   - Dataform integration mode:
     - Create or update shared pytest runner:
       `<dataform_project_path>/integration_tests/test_dataform_integration.py`
     - Create model SQL assets directory:
       `<dataform_project_path>/integration_tests/models/<model_name>/`
   - dbt integration mode:
     - Create or update shared pytest runner:
       `<dbt_project_path>/integration_tests/test_dbt_integration.py`
     - Create model SQL assets directory:
       `<dbt_project_path>/integration_tests/models/<model_name>/`
   - Integration model directory contains:
     - `mock_data.sql`
     - `expected.sql`
     - `assert.sql`
     - `config.json`
   - Do not generate shell-script runners for integration tests.

12. Cost and correctness guardrails:
   - Do not reference live production tables in tests.
   - Do not use placeholders in final test SQL.
   - Match final target output column names and types described in TECHSPEC.
   - Prefer minimal mock data that still proves the business rule.

13. Framework-specific completion checklist:
   - Read `references/unit-test-checklist.md`.
   - Then read and apply exactly one checklist:
     - Dataform: `references/dataform-unit-test-checklist.md`
     - dbt: `references/dbt-unit-test-checklist.md`

## Prompt Templates (Copy/Paste)

Use this template when asking the agent to generate a test:

```text
Please create pytest integration tests for final models, use `examples/agent_skill_unit_tests/SKILL.md` as the governing rules.

Required inputs:
1) TECHSPEC path: <path_to_TECHSPEC.md>
2) Data pipeline project path: <path_to_pipeline_project>
```

Optional explicit framework version:

```text
Please create <dbt|Dataform> tests for final models using `examples/agent_skill_unit_tests/SKILL.md`.
Required inputs:
1) TECHSPEC path: <path_to_TECHSPEC.md>
2) Project path: <path_to_pipeline_project>
```
