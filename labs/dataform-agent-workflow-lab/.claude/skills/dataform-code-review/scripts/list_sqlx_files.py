from __future__ import annotations

from pathlib import Path


def main() -> int:
    root = Path("dataform/definitions")
    if not root.exists():
        print("No dataform/definitions folder found")
        return 1
    for path in sorted(root.rglob("*.sqlx")):
        print(path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
