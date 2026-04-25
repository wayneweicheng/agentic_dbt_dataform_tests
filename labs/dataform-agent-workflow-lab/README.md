# Dataform Agent Workflow Lab

This lab demonstrates the architecture we discussed: a workflow orchestrator coordinates specialist agents that use skills to implement, review, and test a Dataform pipeline from a technical specification.

## Modes

- Claude Code subagents mode: one local lead session delegates to project subagents.
- Claude Code Agent Team mode: one local lead creates teammates for role-based collaboration.
- Claude Agent SDK service mode: a Cloud Run HTTP service runs the workflow programmatically and can be triggered from a Next.js frontend.

## Workflow

```text
Tech Spec
  -> Orchestrator
      -> Tech Spec Code Generation Agent
      -> Code Review Agent
      -> Scenario Test Agent
```

## Main folders

```text
.claude/agents/      role agents
.claude/skills/      reusable skill packages
workflows/           workflow templates
tech_specs/          source technical specs
dataform/            sample/generated Dataform project implementation
tests/               scenario, mock, expected, and report artifacts
scripts/             local and BigQuery helper scripts
sdk-service/         Claude Agent SDK service for Cloud Run
frontend-nextjs/     minimal Next.js trigger app
outputs/             generated notes and final status
```

## Skill package layout

Each skill is a package, not just a `SKILL.md` file:

```text
.claude/skills/<skill-name>/
  SKILL.md              main skill instructions and trigger metadata
  references/           checklists, design rules, and usage notes
  assets/               templates and reusable examples
  scripts/              deterministic helper scripts the skill can use
```

## Role of `dataform/definitions`

`dataform/definitions` is the lab Dataform project implementation area. It contains example SQLX files and the files that the code-generation agent may create or update.

It should not live under the `dataform-code-generation` skill because skills are reusable capability packages. The skill should contain reusable templates, references, and helper scripts. The project-level `dataform/definitions` folder contains concrete implementation output for this lab.

```text
Reusable capability:
  .claude/skills/dataform-code-generation/

Concrete lab implementation:
  dataform/definitions/
```

## Local validation

```bash
cd labs/dataform-agent-workflow-lab
pip install duckdb pandas tabulate
python scripts/local_duckdb_validate.py
```

## Dataform path

```bash
cd labs/dataform-agent-workflow-lab/dataform
npm install
cp workflow_settings.example.yaml workflow_settings.yaml
```

Set the lab environment variables before using the BigQuery helpers:

```bash
export GCP_PROJECT_ID="your-gcp-project-id"
export BQ_LOCATION="australia-southeast1"
export BQ_SOURCE_DATASET="agent_lab_raw"
export BQ_TARGET_DATASET="agent_lab_dataform"
export BQ_ASSERTION_DATASET="agent_lab_assertions"
```

## Run in Claude Code: subagents mode

```text
Use workflows/dataform-lab-subagents.md.

Goal:
Implement tech_specs/order_revenue_mart.md as a Dataform pipeline.

Use the orchestrator agent and delegate to:
- tech-spec-codegen-agent
- code-review-agent
- scenario-test-agent

Required outputs:
- dataform/definitions/output/daily_customer_revenue.sqlx
- outputs/codegen-notes.md
- outputs/code-review.md
- tests/reports/scenario-test-report.md
- outputs/final-status.md
```

## Run in Claude Code: Agent Team mode

```text
Use workflows/dataform-lab-agent-team.md.

Create an Agent Team with:
- lead: orchestrator
- teammate: tech-spec-codegen-agent
- teammate: code-review-agent
- teammate: scenario-test-agent

Respect the file ownership rules in the workflow template.
```

## Run as Cloud Run service

See:

```text
sdk-service/README.md
frontend-nextjs/README.md
```

The SDK service reuses the same filesystem agents under `.claude/agents` and the same filesystem skills under `.claude/skills`. This avoids duplicating agent definitions in Python.

## Architecture summary

```text
Skill = reusable capability package.
Agent = who is responsible for doing or reviewing something.
Workflow = when and in what order work happens.
Agent Team = multiple role agents working in parallel.
Agent SDK = programmable, triggerable, cloud-hosted execution.
```
