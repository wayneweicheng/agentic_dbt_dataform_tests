WITH expected AS (
  __EXPECTED_SQL__
),
actual AS (
  SELECT
    *
  FROM `__TARGET_TABLE__`
),
missing_rows AS (
  SELECT * FROM expected
  EXCEPT DISTINCT
  SELECT * FROM actual
),
unexpected_rows AS (
  SELECT * FROM actual
  EXCEPT DISTINCT
  SELECT * FROM expected
)
SELECT 'MISSING_IN_ACTUAL' AS diff_type, * FROM missing_rows
UNION ALL
SELECT 'UNEXPECTED_IN_ACTUAL' AS diff_type, * FROM unexpected_rows;
