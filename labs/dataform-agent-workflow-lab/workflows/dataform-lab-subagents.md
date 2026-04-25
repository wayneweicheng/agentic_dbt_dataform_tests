# Dataform Lab Workflow - Subagents Mode

Use this workflow when running locally in Claude Code with one lead session delegating to specialist subagents.

## Goal

Implement `tech_specs/order_revenue_mart.md` as a Dataform pipeline, review it, and validate it with scenario tests.

## Agents

- Lead: `orchestrator`
- Implementation: `tech-spec-codegen-agent`
- Review: `code-review-agent`
- Scenario testing: `scenario-test-agent`

## Sequence

1. Lead reads the tech spec and this workflow.
2. Lead delegates implementation to `tech-spec-codegen-agent`.
3. Codegen agent writes Dataform implementation and `outputs/codegen-notes.md`.
4. Lead delegates review to `code-review-agent`.
5. Review agent writes `outputs/code-review.md`.
6. Lead delegates scenario coverage and validation to `scenario-test-agent`.
7. Scenario agent writes test artifacts and `tests/reports/scenario-test-report.md`.
8. Lead writes `outputs/final-status.md`.

## Quality gates

- All business rules must be mapped to implementation or listed as unresolved.
- Review must return one of: `approved`, `approved_with_comments`, `requires_revision`, `blocked`.
- Scenario test report must list every required scenario from the tech spec.
- Commands that write to BigQuery require explicit user approval.
