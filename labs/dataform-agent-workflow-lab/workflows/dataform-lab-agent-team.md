# Dataform Lab Workflow - Agent Team Mode

Use this workflow when running locally in Claude Code Agent Teams.

## Goal

Implement `tech_specs/order_revenue_mart.md` as a Dataform pipeline using a lead plus specialist teammates.

## Team

- Lead: `orchestrator`
- Teammate: `tech-spec-codegen-agent`
- Teammate: `code-review-agent`
- Teammate: `scenario-test-agent`

## File ownership

- Codegen teammate owns `dataform/definitions/**` and `outputs/codegen-notes.md`.
- Review teammate owns `outputs/code-review.md`.
- Scenario teammate owns `tests/scenarios/**`, `tests/mock_data/**`, `tests/expected/**`, and `tests/reports/**`.
- Lead owns `outputs/final-status.md`.

## Task dependencies

1. Code generation starts first.
2. Review depends on generated implementation.
3. Scenario testing depends on tech spec and implementation.
4. Final status depends on review and scenario report.

## Rules

- No teammate edits another teammate's owned files.
- If a teammate finds an issue in another owned area, message the lead and document the issue.
- Ask before running commands that write to BigQuery.
