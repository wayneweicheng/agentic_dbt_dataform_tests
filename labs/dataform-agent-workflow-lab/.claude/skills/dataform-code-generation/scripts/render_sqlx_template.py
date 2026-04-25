from __future__ import annotations

from pathlib import Path
import sys


def render(template: str, values: dict[str, str]) -> str:
    output = template
    for key, value in values.items():
        output = output.replace("${" + key + "}", value)
    return output


def main() -> int:
    if len(sys.argv) != 5:
        print("Usage: python render_sqlx_template.py <template> <target_table> <source_name> <description>")
        return 2
    template_path = Path(sys.argv[1])
    values = {
        "target_table_name": sys.argv[2],
        "source_name": sys.argv[3],
        "description": sys.argv[4],
    }
    print(render(template_path.read_text(encoding="utf-8"), values))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
