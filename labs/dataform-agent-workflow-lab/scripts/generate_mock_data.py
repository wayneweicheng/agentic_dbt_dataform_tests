from __future__ import annotations

from pathlib import Path

LAB_DIR = Path(__file__).resolve().parents[1]
MOCK_DATA = LAB_DIR / "tests" / "mock_data" / "raw_order_events.csv"
EXPECTED = LAB_DIR / "tests" / "expected" / "daily_customer_revenue_expected.csv"


def main() -> int:
    if not MOCK_DATA.exists():
        raise FileNotFoundError(MOCK_DATA)
    if not EXPECTED.exists():
        raise FileNotFoundError(EXPECTED)
    print(f"Mock input exists: {MOCK_DATA}")
    print(f"Expected output exists: {EXPECTED}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
