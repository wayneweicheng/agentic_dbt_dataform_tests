# dbt Unit-Test Checklist

Use this checklist before returning dbt test files.

1. Required inputs are present:
   - TECHSPEC path.
   - dbt project path.
2. dbt framework is confirmed (explicit user input or marker-based detection).
3. If target model file(s) are not provided, model discovery is performed from TECHSPEC and `models/` SQL files.
4. Any model mapping ambiguity is resolved with user clarification before test generation.
5. Testing mode is explicit:
   - Unit mode (dbt `unit_tests:` YAML), or
   - Integration mode (source mocks + `dbt run/build` + pytest + final table assertion).
6. If request is for final-model validation and unit mode is not explicitly requested, integration mode is used by default.
7. For integration mode, scaffold script is used (or equivalent structure is created):
   - `python examples/agent_skill_unit_tests/scripts/scaffold_pytest_integration.py --project-path <dbt_project_path> --pipeline-type dbt --model-name <model_name>`
8. Scenario matrix is derived from TECHSPEC business rules and edge cases.
9. Test business logic is sourced from TECHSPEC only.
10. Model SQL was used only for technical metadata (model name, dependencies, source/ref names), not expected-output logic.
11. For unit mode:
    - Use dbt `unit_tests:` YAML format.
    - Set `model` to the model under test.
    - Mock referenced dependencies via `given` inputs (`ref(...)`, `source(...)`, etc.).
12. For integration mode:
    - Mock source schemas from TECHSPEC input entities.
    - Execute dbt pipeline for target final model.
    - Default integration command is `dbt run`; use `dbt build` only when explicitly needed.
13. Mock data uses BigQuery Standard SQL and explicit casts where needed.
14. Expected output proves TECHSPEC business rules and scenario-matrix edge cases.
15. Unit-test YAML is written under `<dbt_project_path>/models/tests/` unless user asks for another valid path.
16. Integration tests are pytest-based (not shell-script runners).
17. Integration test harness assets are created under:
    - `<dbt_project_path>/integration_tests/test_dbt_integration.py`
    - `<dbt_project_path>/integration_tests/models/<model_name>/mock_data.sql`
    - `<dbt_project_path>/integration_tests/models/<model_name>/expected.sql`
    - `<dbt_project_path>/integration_tests/models/<model_name>/assert.sql`
    - `<dbt_project_path>/integration_tests/models/<model_name>/config.json`
18. dbt integration config includes:
    - `target_table`
    - `dbt_command` (`run` or `build`, default `run`)
    - valid dbt execution settings (`dbt_select`, vars, target/profile overrides as needed)
19. No live production tables are referenced in tests.
20. Numeric/date/string literal types match TECHSPEC data model.
