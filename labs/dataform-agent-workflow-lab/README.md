# Dataform Agent Workflow Lab

This lab demonstrates a complex workflow architecture using Claude Code subagents, Claude Code Agent Teams, and a Claude Agent SDK service deployable to Cloud Run with a Next.js frontend trigger.

## Modes

```text
Mode A: Claude Code subagents mode
Mode B: Claude Code Agent Team mode
Mode C: Claude Agent SDK service on Cloud Run triggered by Next.js
```

## Workflow

```text
Tech Spec
  -> Orchestrator
      -> Tech Spec Code Generation Agent
      -> Code Review Agent
      -> Scenario Test Agent
```

## What the lab builds

The sample technical spec asks agents to build a Dataform pipeline that creates a daily customer revenue mart from raw order events.

Primary Dataform output:

```text
dataform/definitions/output/daily_customer_revenue.sqlx
```

The scenario test agent reads the tech spec, creates scenario coverage, generates mock data, optionally loads mock data to BigQuery, executes Dataform, compares actual results with expected results, and writes a scenario test report.

## Directory structure

```text
.claude/agents/                  Role agents
.claude/skills/                  Reusable skills
workflows/                       Subagents and Agent Team workflows
tech_specs/                      Source technical specs
dataform/                        Dataform project
tests/scenarios/                 Scenario definitions
tests/mock_data/                 Mock source CSVs
tests/expected/                  Expected output CSVs
tests/reports/                   Generated test reports
scripts/                         Local and BigQuery validation helpers
sdk-service/                     Claude Agent SDK HTTP service for Cloud Run
frontend-nextjs/                 Minimal Next.js trigger UI
outputs/                         Generated review and final status files
```

## Local dry-run validation

```bash
cd labs/dataform-agent-workflow-lab
pip install duckdb pandas tabulate
python scripts/local_duckdb_validate.py
```

## Full Dataform/BigQuery path

```bash
cd labs/dataform-agent-workflow-lab/dataform
npm install
cp workflow_settings.example.yaml workflow_settings.yaml
```

Set environment variables:

```bash
export GCP_PROJECT_ID="your-gcp-project-id"
export BQ_LOCATION="australia-southeast1"
export BQ_SOURCE_DATASET="agent_lab_raw"
export BQ_TARGET_DATASET="agent_lab_dataform"
export BQ_ASSERTION_DATASET="agent_lab_assertions"
```

Run:

```bash
cd labs/dataform-agent-workflow-lab
python scripts/generate_mock_data.py
python scripts/load_mock_data_to_bq.py
cd dataform && npx dataform run && cd ..
python scripts/compare_bigquery_results.py
```

## Claude Code subagents mode

Open Claude Code in this lab directory and prompt:

```text
Use workflows/dataform-lab-subagents.md.

Goal:
Implement the tech spec in tech_specs/order_revenue_mart.md as a Dataform pipeline.

Use the orchestrator agent.
Delegate to:
- tech-spec-codegen-agent
- code-review-agent
- scenario-test-agent

Required outputs:
- generated or updated Dataform SQLX files
- outputs/codegen-notes.md
- outputs/code-review.md
- tests/reports/scenario-test-report.md
- outputs/final-status.md

Ask before running any command that writes to BigQuery.
```

## Claude Code Agent Team mode

Open Claude Code in this lab directory and prompt:

```text
Use workflows/dataform-lab-agent-team.md.

Create an Agent Team with:
- lead: orchestrator
- teammate: tech-spec-codegen-agent
- teammate: code-review-agent
- teammate: scenario-test-agent

Goal:
Implement the tech spec in tech_specs/order_revenue_mart.md as a Dataform pipeline.

Rules:
- Code generation owns dataform/definitions/** and outputs/codegen-notes.md.
- Code review owns outputs/code-review.md.
- Scenario test owns tests/scenarios/**, tests/mock_data/**, tests/expected/**, and tests/reports/**.
- No teammate edits another teammate's owned files.
- The lead synthesizes final status.
- Ask before running any command that writes to BigQuery.
```

## Cloud Run + Claude Agent SDK + Next.js frontend

```text
frontend-nextjs
  -> HTTP POST /api/run-workflow
      -> Cloud Run sdk-service
          -> Claude Agent SDK query()
              -> .claude/agents
              -> .claude/skills
              -> workflows/dataform-lab-subagents.md
```

See:

```text
sdk-service/README.md
frontend-nextjs/README.md
```

## SDK correctness notes

The SDK implementation uses the current Claude Agent SDK package and docs pattern:

- Python package: `claude_agent_sdk`.
- Options class: `ClaudeAgentOptions`.
- Main runner: `query()`.
- Skills require `.claude/skills/*/SKILL.md`, `setting_sources=["user", "project"]`, and `allowed_tools` containing `"Skill"`.
- SDK subagents require `allowed_tools` containing `"Agent"`.
- Programmatic subagents use `AgentDefinition` and camelCase fields where applicable.

## Architecture point

```text
Skill = how to do something.
Agent = who is responsible for doing/reviewing something.
Workflow = when and in what order work happens.
Agent Team = multiple role agents working in parallel.
Agent SDK = programmable/event-driven/cloud-hosted execution.
```
