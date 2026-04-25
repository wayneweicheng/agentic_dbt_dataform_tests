from __future__ import annotations

from pathlib import Path
import sys


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python extract_spec_skeleton.py <tech-spec.md>")
        return 2
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    print("# Tech Spec Skeleton")
    print()
    print(f"Source: {path}")
    print()
    print("## Headings")
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            print(f"- {stripped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
