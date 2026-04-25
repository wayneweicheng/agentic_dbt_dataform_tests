"""Cloud Run HTTP service for the Dataform Agent Workflow Lab.

This service demonstrates how to run the same skills + role-agent workflow from a
front end or other event source using the Claude Agent SDK.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions, ResultMessage, query
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


DEFAULT_LAB_DIR = Path(__file__).resolve().parents[1]


class WorkflowRequest(BaseModel):
    tech_spec_path: str = Field(default="tech_specs/order_revenue_mart.md")
    validation_mode: Literal["local", "bigquery"] = Field(default="local")
    user_notes: str = Field(default="Run the full Dataform workflow.")
    max_turns: int = Field(default=20, ge=1, le=80)


class WorkflowResponse(BaseModel):
    status: str
    result: str
    lab_dir: str


app = FastAPI(title="Dataform Agent Workflow Lab SDK Service")


def build_prompt(request: WorkflowRequest) -> str:
    return f"""
Use workflows/dataform-lab-sdk-service.md.

Goal:
Implement and validate the Dataform lab from this technical specification:
{request.tech_spec_path}

Validation mode: {request.validation_mode}

User notes:
{request.user_notes}

Required behavior:
1. Use the orchestrator role.
2. Delegate code generation to tech-spec-codegen-agent.
3. Delegate independent review to code-review-agent.
4. Delegate scenario coverage and validation to scenario-test-agent.
5. Write final status to outputs/final-status.md.
6. Keep file ownership boundaries from the workflow.
7. For validation_mode=local, use local helper scripts only.
8. For validation_mode=bigquery, use the configured lab datasets and document every command.
""".strip()


def build_options(lab_dir: Path, max_turns: int) -> ClaudeAgentOptions:
    """Build SDK options aligned with current Claude Agent SDK docs.

    Key points:
    - setting_sources includes project so .claude/skills and CLAUDE.md are loaded.
    - allowed_tools includes Skill so filesystem skills are available.
    - allowed_tools includes Agent so programmatic subagents can be invoked.
    - programmatic AgentDefinition is used for SDK subagents.
    """

    return ClaudeAgentOptions(
        cwd=str(lab_dir),
        max_turns=max_turns,
        setting_sources=["user", "project"],
        allowed_tools=[
            "Read",
            "Write",
            "Edit",
            "Bash",
            "Glob",
            "Grep",
            "Skill",
            "Agent",
        ],
        agents={
            "tech-spec-codegen-agent": AgentDefinition(
                description="Generates Dataform SQLX implementation from the technical specification.",
                prompt=(
                    "You generate Dataform SQLX from the tech spec. "
                    "Use project skills when relevant. Own dataform/definitions/** "
                    "and outputs/codegen-notes.md. Do not edit review or test report files."
                ),
                tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep", "Skill"],
            ),
            "code-review-agent": AgentDefinition(
                description="Reviews generated Dataform SQLX for correctness and testability.",
                prompt=(
                    "You independently review the generated Dataform implementation. "
                    "Own outputs/code-review.md. Do not edit implementation files."
                ),
                tools=["Read", "Write", "Glob", "Grep", "Skill"],
            ),
            "scenario-test-agent": AgentDefinition(
                description="Creates scenario tests, mock data, expected results, and validation reports.",
                prompt=(
                    "You create scenario coverage and validation artifacts from the tech spec. "
                    "Own tests/scenarios/**, tests/mock_data/**, tests/expected/**, and tests/reports/**."
                ),
                tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep", "Skill"],
            ),
        },
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/run-workflow", response_model=WorkflowResponse)
async def run_workflow(request: WorkflowRequest) -> WorkflowResponse:
    lab_dir = Path(os.getenv("LAB_PROJECT_DIR", str(DEFAULT_LAB_DIR))).resolve()
    if not lab_dir.exists():
        raise HTTPException(status_code=500, detail=f"LAB_PROJECT_DIR does not exist: {lab_dir}")

    prompt = build_prompt(request)
    options = build_options(lab_dir, request.max_turns)

    final_result = ""
    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, ResultMessage):
                final_result = message.result or ""
    except Exception as exc:  # pragma: no cover - surfaced to HTTP caller
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return WorkflowResponse(status="completed", result=final_result, lab_dir=str(lab_dir))
