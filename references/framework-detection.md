# Framework Detection Guide (dbt vs Dataform)

Use this guide before generating any tests.

## 1) Detection precedence

1. Explicit user statement wins:
   - If user says "dbt project", use dbt flow.
   - If user says "Dataform project", use Dataform flow.
2. Otherwise detect from project path markers.
3. If still ambiguous, ask one clarification question and stop.

## 2) Project marker rules

Treat as **Dataform** when project path includes:
- `workflow_settings.yaml`, and
- `definitions/` (typically `.sqlx` files).

Treat as **dbt** when project path includes:
- `dbt_project.yml`, and
- `models/` (typically `.sql` + `.yml` files).

If both marker sets exist:
- Ask user which framework to target.
- Do not guess.

If neither marker set exists:
- Ask for a corrected project path.
- Do not generate tests.

## 3) Mode routing

After framework detection, apply framework-specific instructions:
- Dataform: `references/dataform-unit-test-checklist.md`
- dbt: `references/dbt-unit-test-checklist.md`
