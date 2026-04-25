from __future__ import annotations

from pathlib import Path


def main() -> int:
    scenarios_dir = Path("tests/scenarios")
    if not scenarios_dir.exists():
        print("No tests/scenarios folder found")
        return 1
    for path in sorted(scenarios_dir.glob("*.md")):
        print(path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
