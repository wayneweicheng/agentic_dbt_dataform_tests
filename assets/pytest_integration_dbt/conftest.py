from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import pytest


INTEGRATION_TESTS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = INTEGRATION_TESTS_DIR.parent
MODELS_DIR = INTEGRATION_TESTS_DIR / "models"


@lru_cache(maxsize=None)
def load_model_config(model_name: str) -> dict:
    config_path = MODELS_DIR / model_name / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Missing model config: {config_path}")
    config = json.loads(config_path.read_text())
    declared_name = config.get("model_name")
    if declared_name and declared_name != model_name:
        raise ValueError(
            f"Model config mismatch: directory={model_name}, config.model_name={declared_name}"
        )
    return config


def discover_model_names(selected_models: list[str] | None = None) -> list[str]:
    if not MODELS_DIR.exists():
        raise pytest.UsageError(f"Missing models directory: {MODELS_DIR}")

    model_names = sorted(
        p.name for p in MODELS_DIR.iterdir() if p.is_dir() and (p / "config.json").exists()
    )
    if not model_names:
        raise pytest.UsageError(f"No model configs found under: {MODELS_DIR}")

    selected = selected_models or []
    if selected:
        missing = sorted(set(selected) - set(model_names))
        if missing:
            raise pytest.UsageError(
                f"Unknown --model values: {missing}. Available models: {model_names}"
            )
        return [m for m in model_names if m in set(selected)]

    return model_names


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--model",
        action="append",
        default=[],
        help=(
            "Model name(s) under integration_tests/models to run. "
            "May be repeated, e.g. --model fct_customer_value_monthly"
        ),
    )


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    selected = metafunc.config.getoption("model")
    model_names = discover_model_names(selected)

    fixture_names = set(metafunc.fixturenames)

    if {"model_name", "scenario_case"}.issubset(fixture_names):
        params = []
        for model_name in model_names:
            config = load_model_config(model_name)
            scenarios = config.get("scenario_cases", [])
            for scenario in scenarios:
                scenario_id = scenario.get("id")
                if not scenario_id:
                    raise pytest.UsageError(
                        f"Scenario missing 'id' in model {model_name}: {scenario}"
                    )
                params.append(
                    pytest.param(
                        model_name,
                        scenario,
                        id=f"{model_name}::{scenario_id}",
                    )
                )
        metafunc.parametrize(("model_name", "scenario_case"), params)
        return

    if "model_name" in fixture_names:
        metafunc.parametrize("model_name", model_names, ids=model_names)


@pytest.fixture
def model_config(model_name: str) -> dict:
    return load_model_config(model_name)


@pytest.fixture
def model_sql_paths(model_name: str) -> dict:
    model_dir = MODELS_DIR / model_name
    paths = {
        "model_dir": model_dir,
        "mock_data": model_dir / "mock_data.sql",
        "expected": model_dir / "expected.sql",
        "assert": model_dir / "assert.sql",
    }
    missing = [str(path) for key, path in paths.items() if key != "model_dir" and not path.exists()]
    if missing:
        raise pytest.UsageError(
            f"Missing required SQL assets for model {model_name}: {missing}"
        )
    return paths
