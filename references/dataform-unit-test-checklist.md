# Dataform Unit-Test Checklist

Use this checklist before returning Dataform test files.

1. Required inputs are present:
   - TECHSPEC path.
   - Dataform project path.
2. Dataform framework is confirmed (explicit user input or marker-based detection).
3. If target model file(s) are not provided, model discovery is performed from TECHSPEC and project files.
4. Any model mapping ambiguity is resolved with user clarification before test generation.
5. Testing mode is explicit:
   - Unit mode (`config { type: "test" }`), or
   - Integration mode (source mocks + `dataform run` + pytest + final table assertion).
6. If request is for final-model validation and unit mode is not explicitly requested, integration mode is used by default.
7. For integration mode, scaffold script is used (or equivalent structure is created):
   - `python examples/agent_skill_unit_tests/scripts/scaffold_pytest_integration.py --project-path <dataform_project_path> --pipeline-type dataform --model-name <model_name>`
8. Scenario matrix is derived from TECHSPEC business rules and edge cases.
9. Test business logic is sourced from TECHSPEC only.
10. Model SQL was used only for metadata (`dataset` name and `${ref(...)}` dependency names), not expected-output logic.
11. For unit mode, `config` block has:
    - `type: "test"`
    - `dataset` equal to model name under test.
    - Only supported keys for tests (`type`, `dataset`, optional `name`); no `description`.
12. For unit mode, direct `${ref(...)}` dependencies are mocked.
13. For integration mode, source-table schemas from TECHSPEC inputs are mocked.
14. For integration mode, pipeline execution step (`dataform run`) is included before assertions.
15. Mock data uses BigQuery Standard SQL and `UNION ALL` rows.
16. Expected output proves TECHSPEC business rules and scenario-matrix edge cases.
17. Unit test files are created under `<dataform_project_path>/definitions/tests/`.
18. Integration tests are pytest-based (not shell-script runners).
19. Integration test harness assets are created under:
    - `<dataform_project_path>/integration_tests/test_dataform_integration.py`
    - `<dataform_project_path>/integration_tests/models/<model_name>/mock_data.sql`
    - `<dataform_project_path>/integration_tests/models/<model_name>/expected.sql`
    - `<dataform_project_path>/integration_tests/models/<model_name>/assert.sql`
    - `<dataform_project_path>/integration_tests/models/<model_name>/config.json`
20. No live table references exist in the test.
21. Numeric/date/string literal types match TECHSPEC data model.
