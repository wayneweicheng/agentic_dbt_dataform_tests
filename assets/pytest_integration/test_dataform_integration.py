from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import uuid
from decimal import Decimal
from pathlib import Path

import pytest

from conftest import PROJECT_DIR

_PIPELINE_CACHE: dict[tuple, dict] = {}
_EXPECTED_CACHE: dict[tuple, dict] = {}
_ACTUAL_CACHE: dict[tuple, dict] = {}
_ASSERT_CACHE: dict[tuple, list[dict]] = {}
_CLEANUP_CONTEXTS: dict[tuple, dict] = {}
_MODEL_CONTEXT_CACHE: dict[tuple, dict] = {}
_MODEL_DEFAULT_RUN_ID: dict[str, str] = {}


def _run_command(
    cmd: list[str],
    *,
    cwd=None,
    input_text: str | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        input=input_text,
        text=True,
        capture_output=True,
    )
    if check and proc.returncode != 0:
        cmd_str = " ".join(cmd)
        raise RuntimeError(
            f"Command failed ({cmd_str})\n"
            f"STDOUT:\n{proc.stdout}\n"
            f"STDERR:\n{proc.stderr}"
        )
    return proc


def _run_bq_query(
    project_id: str,
    location: str,
    sql: str,
    *,
    output_format: str | None = None,
) -> str:
    cmd = [
        "bq",
        f"--project_id={project_id}",
        f"--location={location}",
        "query",
        "--quiet",
        "--use_legacy_sql=false",
    ]
    if output_format:
        cmd.append(f"--format={output_format}")
    result = _run_command(cmd, input_text=sql)
    return result.stdout


def _parse_json_rows(raw_json: str) -> list[dict]:
    text = raw_json.strip()
    if not text:
        return []
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Unable to parse bq JSON output:\n{text}") from exc


def _normalize_value(value, value_type: str):
    if value is None:
        return None

    if value_type == "int":
        return int(value)
    if value_type == "numeric":
        return Decimal(str(value))
    if value_type == "bool":
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() == "true"
        return bool(value)
    if value_type in {"date", "string"}:
        return str(value)

    raise ValueError(f"Unsupported column type: {value_type}")


def _normalize_row(row: dict, columns: list[str], column_types: dict[str, str]) -> dict:
    normalized = {}
    for col in columns:
        col_type = column_types.get(col, "string")
        normalized[col] = _normalize_value(row.get(col), col_type)
    return normalized


def _sanitize_token(value: str) -> str:
    return re.sub(r"[^0-9A-Za-z_]+", "_", value)


def _row_key(row: dict, key_columns: list[str]) -> tuple:
    return tuple(row[col] for col in key_columns)


def _row_diff(expected: dict, actual: dict, columns: list[str]) -> dict:
    return {col: (expected[col], actual[col]) for col in columns if expected[col] != actual[col]}


def _load_workflow_setting(setting_key: str) -> str | None:
    workflow_path = PROJECT_DIR / "workflow_settings.yaml"
    if not workflow_path.exists():
        return None

    pattern = re.compile(rf"^\s*{re.escape(setting_key)}\s*:\s*[\"']?([^\"'#\n]+)")
    for line in workflow_path.read_text().splitlines():
        match = pattern.search(line)
        if match:
            return match.group(1).strip()
    return None


def _context_key(context: dict) -> tuple:
    return (
        context["model_name"],
        context["project_id"],
        context["location"],
        context["source_dataset"],
        context["schema_suffix"],
        context["assertion_schema"],
        context["action_name"],
    )


def _cleanup_context_datasets(context: dict) -> None:
    project_id = context["project_id"]
    location = context["location"]
    source_dataset = context["source_dataset"]
    schema_suffix = context["schema_suffix"]
    assertion_schema = context["assertion_schema"]
    datasets = [
        source_dataset,
        f"retail_staging_{schema_suffix}",
        f"retail_intermediate_{schema_suffix}",
        f"retail_mart_{schema_suffix}",
        assertion_schema,
    ]
    for dataset in datasets:
        _run_command(
            [
                "bq",
                f"--project_id={project_id}",
                f"--location={location}",
                "rm",
                "-r",
                "-f",
                "-d",
                f"{project_id}:{dataset}",
            ],
            check=False,
        )


@pytest.fixture(scope="session", autouse=True)
def cleanup_after_session():
    yield
    for context in _CLEANUP_CONTEXTS.values():
        _cleanup_context_datasets(context)


@pytest.fixture
def model_run_context(model_name: str, model_config: dict, model_sql_paths: dict):
    for command in ("bq", "dataform"):
        if shutil.which(command) is None:
            pytest.fail(f"Missing required command: {command}")

    creds_path = PROJECT_DIR / ".df-credentials.json"
    if not creds_path.exists():
        pytest.fail(f"Missing credentials file: {creds_path}")

    project_id = (
        os.getenv("PROJECT_ID")
        or os.getenv("GOOGLE_CLOUD_PROJECT")
        or _load_workflow_setting("defaultProject")
    )
    if not project_id:
        pytest.fail(
            "Project ID not found. Set PROJECT_ID (or GOOGLE_CLOUD_PROJECT), "
            "or define defaultProject in workflow_settings.yaml."
        )

    location = os.getenv("LOCATION") or _load_workflow_setting("defaultLocation") or "us-central1"

    run_id_from_env = os.getenv("RUN_ID")
    if run_id_from_env:
        run_id_base = run_id_from_env
    else:
        run_id_base = _MODEL_DEFAULT_RUN_ID.setdefault(model_name, f"it_{uuid.uuid4().hex[:8]}")
    safe_run_id = _sanitize_token(f"{run_id_base}_{model_name}")

    source_dataset_env = os.getenv("SOURCE_DATASET")
    schema_suffix_env = os.getenv("SCHEMA_SUFFIX")
    assertion_schema_env = os.getenv("ASSERTION_SCHEMA")
    action_name_env = os.getenv("ACTION_NAME")
    cleanup = os.getenv("CLEANUP", "false").lower() == "true"

    source_dataset = source_dataset_env or f"it_src_{safe_run_id}"
    schema_suffix = schema_suffix_env or f"it_{safe_run_id}"
    assertion_schema = assertion_schema_env or f"dataform_assertions_{schema_suffix}"
    action_name = action_name_env or model_config.get("action_name", model_name)

    context_cache_key = (
        model_name,
        project_id,
        location,
        source_dataset,
        schema_suffix,
        assertion_schema,
        action_name,
        cleanup,
    )
    if context_cache_key in _MODEL_CONTEXT_CACHE:
        return _MODEL_CONTEXT_CACHE[context_cache_key]

    target_table = f"{project_id}.retail_mart_{schema_suffix}.{model_name}"

    context = {
        "model_name": model_name,
        "project_id": project_id,
        "location": location,
        "source_dataset": source_dataset,
        "schema_suffix": schema_suffix,
        "assertion_schema": assertion_schema,
        "action_name": action_name,
        "cleanup": cleanup,
        "target_table": target_table,
        "model_config": model_config,
        "model_sql_paths": model_sql_paths,
    }

    _MODEL_CONTEXT_CACHE[context_cache_key] = context
    return context


@pytest.fixture
def pipeline_run(model_run_context: dict):
    cache_key = _context_key(model_run_context)
    if cache_key in _PIPELINE_CACHE:
        return _PIPELINE_CACHE[cache_key]

    project_id = model_run_context["project_id"]
    location = model_run_context["location"]
    source_dataset = model_run_context["source_dataset"]
    schema_suffix = model_run_context["schema_suffix"]
    assertion_schema = model_run_context["assertion_schema"]
    action_name = model_run_context["action_name"]

    mock_data_sql = (
        model_run_context["model_sql_paths"]["mock_data"].read_text()
        .replace("__SOURCE_PROJECT__", project_id)
        .replace("__SOURCE_DATASET__", source_dataset)
    )

    _run_bq_query(
        project_id,
        location,
        f"CREATE SCHEMA IF NOT EXISTS `{project_id}.{source_dataset}` "
        f"OPTIONS(location='{location}')",
    )
    _run_bq_query(project_id, location, mock_data_sql)

    _run_command(
        [
            "dataform",
            "run",
            ".",
            "--default-database",
            project_id,
            "--default-location",
            location,
            "--assertion-schema",
            assertion_schema,
            "--schema-suffix",
            schema_suffix,
            "--vars",
            f"source_project={project_id},source_dataset={source_dataset}",
            "--actions",
            action_name,
            "--include-deps",
        ],
        cwd=PROJECT_DIR,
    )

    _PIPELINE_CACHE[cache_key] = model_run_context
    if model_run_context["cleanup"]:
        _CLEANUP_CONTEXTS[cache_key] = model_run_context
    return model_run_context


@pytest.fixture
def expected_rows_by_key(pipeline_run: dict):
    cache_key = _context_key(pipeline_run)
    if cache_key in _EXPECTED_CACHE:
        return _EXPECTED_CACHE[cache_key]

    config = pipeline_run["model_config"]
    columns = config["columns"]
    column_types = config["column_types"]
    key_columns = config["key_columns"]

    raw = _run_bq_query(
        pipeline_run["project_id"],
        pipeline_run["location"],
        pipeline_run["model_sql_paths"]["expected"].read_text(),
        output_format="json",
    )
    rows = [_normalize_row(row, columns, column_types) for row in _parse_json_rows(raw)]
    result = {
        _row_key(row, key_columns): row
        for row in rows
    }
    _EXPECTED_CACHE[cache_key] = result
    return result


@pytest.fixture
def actual_rows_by_key(pipeline_run: dict):
    cache_key = _context_key(pipeline_run)
    if cache_key in _ACTUAL_CACHE:
        return _ACTUAL_CACHE[cache_key]

    config = pipeline_run["model_config"]
    columns = config["columns"]
    column_types = config["column_types"]
    key_columns = config["key_columns"]

    actual_sql = "SELECT " + ", ".join(columns) + f" FROM `{pipeline_run['target_table']}`"
    raw = _run_bq_query(
        pipeline_run["project_id"],
        pipeline_run["location"],
        actual_sql,
        output_format="json",
    )
    rows = [_normalize_row(row, columns, column_types) for row in _parse_json_rows(raw)]
    result = {
        _row_key(row, key_columns): row
        for row in rows
    }
    _ACTUAL_CACHE[cache_key] = result
    return result


@pytest.fixture
def assert_diff_rows(pipeline_run: dict):
    cache_key = _context_key(pipeline_run)
    if cache_key in _ASSERT_CACHE:
        return _ASSERT_CACHE[cache_key]

    expected_sql = pipeline_run["model_sql_paths"]["expected"].read_text().strip()
    assert_sql = (
        pipeline_run["model_sql_paths"]["assert"].read_text()
        .replace("__EXPECTED_SQL__", expected_sql)
        .replace("__TARGET_TABLE__", pipeline_run["target_table"])
    )
    raw = _run_bq_query(
        pipeline_run["project_id"],
        pipeline_run["location"],
        assert_sql,
        output_format="json",
    )
    result = _parse_json_rows(raw)
    _ASSERT_CACHE[cache_key] = result
    return result


def test_row_count_matches(model_name: str, expected_rows_by_key: dict, actual_rows_by_key: dict):
    assert len(actual_rows_by_key) == len(expected_rows_by_key), (
        f"Row count mismatch for model {model_name}: "
        f"expected={len(expected_rows_by_key)}, actual={len(actual_rows_by_key)}"
    )


def test_no_missing_rows(
    model_name: str,
    assert_diff_rows: list[dict],
    expected_rows_by_key: dict,
    actual_rows_by_key: dict,
):
    missing_keys = sorted(set(expected_rows_by_key.keys()) - set(actual_rows_by_key.keys()))
    missing_rows_from_assert = [
        row for row in assert_diff_rows if row.get("diff_type") == "MISSING_IN_ACTUAL"
    ]
    assert not missing_rows_from_assert, (
        f"Missing rows via assert.sql for model {model_name}: {missing_rows_from_assert}"
    )
    assert not missing_keys, f"Missing rows in actual output for model {model_name}: {missing_keys}"


def test_no_unexpected_rows(
    model_name: str,
    assert_diff_rows: list[dict],
    expected_rows_by_key: dict,
    actual_rows_by_key: dict,
):
    unexpected_keys = sorted(set(actual_rows_by_key.keys()) - set(expected_rows_by_key.keys()))
    unexpected_rows_from_assert = [
        row for row in assert_diff_rows if row.get("diff_type") == "UNEXPECTED_IN_ACTUAL"
    ]
    assert not unexpected_rows_from_assert, (
        f"Unexpected rows via assert.sql for model {model_name}: {unexpected_rows_from_assert}"
    )
    assert not unexpected_keys, (
        f"Unexpected rows found in actual output for model {model_name}: {unexpected_keys}"
    )


def test_each_scenario_row_matches_expected(
    model_name: str,
    scenario_case: dict,
    model_config: dict,
    expected_rows_by_key: dict,
    actual_rows_by_key: dict,
):
    key_columns = model_config["key_columns"]
    column_types = model_config["column_types"]
    columns = model_config["columns"]

    scenario_key = tuple(
        _normalize_value(scenario_case["key"][col], column_types.get(col, "string"))
        for col in key_columns
    )
    assert scenario_key in expected_rows_by_key, (
        f"Scenario key missing from expected set for model {model_name}: {scenario_key}"
    )
    assert scenario_key in actual_rows_by_key, (
        f"Scenario key missing from actual set for model {model_name}: {scenario_key}"
    )

    expected_row = expected_rows_by_key[scenario_key]
    actual_row = actual_rows_by_key[scenario_key]
    diff = _row_diff(expected_row, actual_row, columns)
    assert not diff, (
        f"Scenario {scenario_case['id']} mismatch for model {model_name}: {diff}"
    )
