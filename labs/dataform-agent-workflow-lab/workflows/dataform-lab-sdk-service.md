# Dataform Lab Workflow - Claude Code SDK Service Mode

Use this workflow when the lab is run by the Cloud Run service in `sdk-service/`.

## Goal

Run the same high-level workflow as subagents mode through the Claude Code SDK.

## Service behavior

1. Receive a workflow request from HTTP.
2. Build a prompt containing:
   - workflow mode
   - tech spec path
   - requested validation mode
   - user notes
3. Run Claude Code SDK from this lab working directory.
4. Allow project subagents and skills to be discovered from `.claude/`.
5. Stream or collect the final SDK result.
6. Return structured JSON to the caller.

## Agent routing expectation

The orchestrator should delegate to project subagents:

- `tech-spec-codegen-agent`
- `code-review-agent`
- `scenario-test-agent`

## Safety

- Default validation mode is local only.
- BigQuery validation must be explicitly requested in the request payload.
- Production hardening should add authentication, durable run storage, and approval workflow.
