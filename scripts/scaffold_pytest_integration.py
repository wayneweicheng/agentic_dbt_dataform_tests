#!/usr/bin/env python3
"""Scaffold pytest integration tests for Dataform or dbt final models.

Creates/updates:
- <project>/integration_tests/conftest.py
- <project>/integration_tests/test_<framework>_integration.py
- <project>/integration_tests/models/<model_name>/{config.json,mock_data.sql,expected.sql,assert.sql}

By default, existing files are preserved. Use --overwrite to replace them.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PIPELINE_TYPE_AUTO = "auto"
PIPELINE_TYPE_DATAFORM = "dataform"
PIPELINE_TYPE_DBT = "dbt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold pytest integration test harness for Dataform or dbt final models."
    )
    parser.add_argument(
        "--project-path",
        required=True,
        help="Path to pipeline project root.",
    )
    parser.add_argument(
        "--pipeline-type",
        default=PIPELINE_TYPE_AUTO,
        choices=[PIPELINE_TYPE_AUTO, PIPELINE_TYPE_DATAFORM, PIPELINE_TYPE_DBT],
        help=(
            "Pipeline framework. Defaults to auto-detection from project markers "
            "(workflow_settings.yaml/definitions for Dataform, dbt_project.yml/models for dbt)."
        ),
    )
    parser.add_argument(
        "--model-name",
        action="append",
        required=True,
        help="Final model name to scaffold (repeatable).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing scaffolded files.",
    )
    return parser.parse_args()


def load_template(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Template file not found: {path}")
    return path.read_text(encoding="utf-8")


def write_from_template(
    src_template: Path,
    dst: Path,
    replacements: dict[str, str],
    overwrite: bool,
) -> None:
    if dst.exists() and not overwrite:
        print(f"SKIP   {dst} (already exists)")
        return

    text = load_template(src_template)
    for key, value in replacements.items():
        text = text.replace(key, value)

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")
    print(f"WRITE  {dst}")


def _looks_like_dataform(project_path: Path) -> bool:
    if (project_path / "workflow_settings.yaml").exists():
        return True
    definitions_dir = project_path / "definitions"
    if definitions_dir.exists() and definitions_dir.is_dir():
        if any(definitions_dir.rglob("*.sqlx")):
            return True
    return False


def _looks_like_dbt(project_path: Path) -> bool:
    if (project_path / "dbt_project.yml").exists():
        return True
    models_dir = project_path / "models"
    if models_dir.exists() and models_dir.is_dir():
        if any(models_dir.rglob("*.sql")):
            return True
    return False


def detect_pipeline_type(project_path: Path) -> str:
    looks_dataform = _looks_like_dataform(project_path)
    looks_dbt = _looks_like_dbt(project_path)

    if looks_dataform and looks_dbt:
        raise ValueError(
            "Unable to auto-detect pipeline type: project contains both Dataform and dbt markers. "
            "Re-run with --pipeline-type dataform or --pipeline-type dbt."
        )
    if looks_dataform:
        return PIPELINE_TYPE_DATAFORM
    if looks_dbt:
        return PIPELINE_TYPE_DBT

    raise FileNotFoundError(
        "Unable to auto-detect pipeline type. Expected one of:\n"
        "- Dataform markers: workflow_settings.yaml and definitions/\n"
        "- dbt markers: dbt_project.yml and models/"
    )


def validate_dataform_project_path(project_path: Path) -> None:
    if not project_path.exists():
        raise FileNotFoundError(f"Project path does not exist: {project_path}")
    if not project_path.is_dir():
        raise NotADirectoryError(f"Project path is not a directory: {project_path}")

    required = [project_path / "definitions", project_path / "workflow_settings.yaml"]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "Project path does not look like a Dataform project. Missing: " + ", ".join(missing)
        )


def validate_dbt_project_path(project_path: Path) -> None:
    if not project_path.exists():
        raise FileNotFoundError(f"Project path does not exist: {project_path}")
    if not project_path.is_dir():
        raise NotADirectoryError(f"Project path is not a directory: {project_path}")

    required = [project_path / "models", project_path / "dbt_project.yml"]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "Project path does not look like a dbt project. Missing: " + ", ".join(missing)
        )


def validate_project_path(project_path: Path, pipeline_type: str) -> None:
    if pipeline_type == PIPELINE_TYPE_DATAFORM:
        validate_dataform_project_path(project_path)
        return
    if pipeline_type == PIPELINE_TYPE_DBT:
        validate_dbt_project_path(project_path)
        return
    raise ValueError(f"Unsupported pipeline type: {pipeline_type}")


def pipeline_layout(pipeline_type: str) -> dict[str, str]:
    if pipeline_type == PIPELINE_TYPE_DATAFORM:
        return {
            "template_dir_name": "pytest_integration",
            "harness_test_file": "test_dataform_integration.py",
        }
    if pipeline_type == PIPELINE_TYPE_DBT:
        return {
            "template_dir_name": "pytest_integration_dbt",
            "harness_test_file": "test_dbt_integration.py",
        }
    raise ValueError(f"Unsupported pipeline type: {pipeline_type}")


def main() -> int:
    args = parse_args()

    skill_dir = Path(__file__).resolve().parents[1]

    project_path = Path(args.project_path).expanduser().resolve()
    pipeline_type = args.pipeline_type
    if pipeline_type == PIPELINE_TYPE_AUTO:
        pipeline_type = detect_pipeline_type(project_path)
    validate_project_path(project_path, pipeline_type)

    layout = pipeline_layout(pipeline_type)
    template_dir = skill_dir / "assets" / layout["template_dir_name"]

    integration_tests_dir = project_path / "integration_tests"

    # Shared harness files.
    harness_files = {
        "conftest.py": integration_tests_dir / "conftest.py",
        layout["harness_test_file"]: integration_tests_dir / layout["harness_test_file"],
    }

    for template_name, dst in harness_files.items():
        write_from_template(
            template_dir / template_name,
            dst,
            replacements={},
            overwrite=args.overwrite,
        )

    # Per-model files.
    model_names = []
    seen = set()
    for raw in args.model_name:
        model = raw.strip()
        if not model:
            continue
        if model in seen:
            continue
        seen.add(model)
        model_names.append(model)

    if not model_names:
        raise ValueError("At least one non-empty --model-name is required.")

    for model_name in model_names:
        model_dir = integration_tests_dir / "models" / model_name
        replacements = {"__MODEL_NAME__": model_name}

        for template_name in ("config.json", "mock_data.sql", "expected.sql", "assert.sql"):
            write_from_template(
                template_dir / template_name,
                model_dir / template_name,
                replacements=replacements,
                overwrite=args.overwrite,
            )

    print(f"DONE   pytest integration scaffold generated ({pipeline_type}).")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR  {exc}", file=sys.stderr)
        raise
