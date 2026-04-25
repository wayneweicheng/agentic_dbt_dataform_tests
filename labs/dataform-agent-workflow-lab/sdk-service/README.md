# Claude Agent SDK Service

This folder contains a FastAPI service that runs the Dataform lab workflow through the Claude Agent SDK.

## Verified SDK pattern

The current official docs say the Claude Code SDK has been renamed to the Claude Agent SDK. The Python examples use:

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition
```

For skills:

```python
ClaudeAgentOptions(
    cwd="/path/to/project",
    setting_sources=["user", "project"],
    allowed_tools=["Skill", "Read", "Write", "Edit", "Bash", "Agent"],
)
```

Key points:

- Skills are filesystem artifacts under `.claude/skills/*/SKILL.md`.
- Skills need `setting_sources` to include `project` or `user`.
- Skills need `allowed_tools` to include `Skill` when an allowlist is used.
- SDK subagents can be defined programmatically with `AgentDefinition`.
- SDK subagents are invoked through the `Agent` tool, so `allowed_tools` must include `Agent`.

## Local run

```bash
cd labs/dataform-agent-workflow-lab/sdk-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080
```

Then call:

```bash
curl -X POST http://localhost:8080/run-workflow \
  -H 'Content-Type: application/json' \
  -d '{"tech_spec_path":"tech_specs/order_revenue_mart.md","validation_mode":"local","user_notes":"Run the full lab workflow."}'
```

## Cloud Run deploy

```bash
gcloud run deploy dataform-agent-workflow-lab \
  --source . \
  --region australia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars LAB_PROJECT_DIR=/app/labs/dataform-agent-workflow-lab
```

For a real deployment, replace unauthenticated access with IAM or application authentication.
