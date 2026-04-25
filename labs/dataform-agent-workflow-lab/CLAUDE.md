# Claude Project Instructions

This lab demonstrates a complex Dataform workflow using skills, role agents, workflows, and a production-style Claude Agent SDK service.

## Default behavior

- Treat `tech_specs/order_revenue_mart.md` as the source of truth.
- Prefer deterministic scripts for validation and data comparison.
- Do not run commands that write to BigQuery unless explicitly approved by the user.
- Keep generated artifacts in the existing lab folders.
- Preserve role boundaries:
  - code generation owns Dataform implementation and codegen notes
  - code review owns review findings
  - scenario testing owns test scenarios, mock data, expected outputs, and test reports
  - orchestrator owns final status and workflow coordination

## Available workflows

- `workflows/dataform-lab-subagents.md`
- `workflows/dataform-lab-agent-team.md`
- `workflows/dataform-lab-sdk-service.md`

## Safety

Never drop, truncate, or overwrite non-lab BigQuery datasets or tables. Use only datasets supplied through environment variables and prefixed for lab use.
