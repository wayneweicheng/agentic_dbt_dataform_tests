from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

LAB_DIR = Path(__file__).resolve().parents[1]
MOCK_DATA = LAB_DIR / "tests" / "mock_data" / "raw_order_events.csv"
EXPECTED = LAB_DIR / "tests" / "expected" / "daily_customer_revenue_expected.csv"
REPORT = LAB_DIR / "tests" / "reports" / "scenario-test-report.md"

QUERY = """
WITH raw_order_events AS (
  SELECT * FROM read_csv_auto($mock_data, header = true)
),
latest_order_events AS (
  SELECT
    order_id,
    customer_id,
    CAST(order_ts AS TIMESTAMP) AS order_ts,
    status,
    CAST(amount AS DECIMAL(18, 2)) AS amount,
    COALESCE(CAST(discount_amount AS DECIMAL(18, 2)), 0) AS discount_amount,
    currency,
    CAST(updated_at AS TIMESTAMP) AS updated_at,
    ROW_NUMBER() OVER (
      PARTITION BY order_id
      ORDER BY CAST(updated_at AS TIMESTAMP) DESC
    ) AS row_num
  FROM raw_order_events
  WHERE order_id IS NOT NULL
    AND customer_id IS NOT NULL
    AND order_ts IS NOT NULL
),
valid_paid_orders AS (
  SELECT
    order_id,
    customer_id,
    order_ts,
    CAST(order_ts AS DATE) AS order_date,
    amount,
    discount_amount,
    amount - discount_amount AS net_revenue
  FROM latest_order_events
  WHERE row_num = 1
    AND status = 'PAID'
    AND amount - discount_amount > 0
)
SELECT
  CAST(order_date AS VARCHAR) AS order_date,
  customer_id,
  CAST(COUNT(*) AS BIGINT) AS order_count,
  CAST(SUM(amount) AS DECIMAL(18, 2)) AS gross_revenue,
  CAST(SUM(discount_amount) AS DECIMAL(18, 2)) AS discount_amount,
  CAST(SUM(net_revenue) AS DECIMAL(18, 2)) AS net_revenue,
  strftime(MIN(order_ts), '%Y-%m-%dT%H:%M:%SZ') AS first_order_ts,
  strftime(MAX(order_ts), '%Y-%m-%dT%H:%M:%SZ') AS last_order_ts
FROM valid_paid_orders
GROUP BY order_date, customer_id
ORDER BY order_date, customer_id
"""


def normalise(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    numeric_cols = ["gross_revenue", "discount_amount", "net_revenue"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col]).round(2)
    df["order_count"] = pd.to_numeric(df["order_count"]).astype("int64")
    return df.sort_values(["order_date", "customer_id"]).reset_index(drop=True)


def main() -> int:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    actual = con.execute(QUERY, {"mock_data": str(MOCK_DATA)}).fetchdf()
    expected = pd.read_csv(EXPECTED)

    actual = normalise(actual)
    expected = normalise(expected)
    passed = actual.equals(expected)

    report = [
        "# Scenario Test Report",
        "",
        f"Status: {'passed' if passed else 'failed'}",
        "",
        "## Scenario coverage",
        "",
        "- Happy path paid orders aggregate correctly.",
        "- Cancelled and pending orders are excluded.",
        "- Null discount is treated as zero.",
        "- Duplicate order_id keeps latest updated_at.",
        "- Null critical fields are excluded.",
        "- Zero or negative net revenue is excluded.",
        "- Multiple customers and dates produce separate rows.",
        "",
        "## Actual output",
        "",
        actual.to_markdown(index=False),
        "",
        "## Expected output",
        "",
        expected.to_markdown(index=False),
        "",
    ]
    REPORT.write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote {REPORT}")
    print("PASSED" if passed else "FAILED")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
