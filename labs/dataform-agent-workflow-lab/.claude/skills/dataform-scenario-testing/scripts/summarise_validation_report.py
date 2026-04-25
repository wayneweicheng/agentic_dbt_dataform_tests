from __future__ import annotations

from pathlib import Path


def main() -> int:
    report_dir = Path("tests/reports")
    if not report_dir.exists():
        print("No reports folder found")
        return 1
    for path in sorted(report_dir.glob("*.md")):
        print(path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
