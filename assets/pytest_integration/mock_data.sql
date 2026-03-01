-- Source mocks for __MODEL_NAME__ integration testing.
-- Replace with TECHSPEC-derived source fixtures.

CREATE OR REPLACE TABLE `__SOURCE_PROJECT__.__SOURCE_DATASET__.orders` AS
SELECT
  1 AS order_id,
  1 AS user_id,
  'complete' AS status,
  TIMESTAMP('2024-01-01 00:00:00') AS created_at;

CREATE OR REPLACE TABLE `__SOURCE_PROJECT__.__SOURCE_DATASET__.order_items` AS
SELECT
  1 AS id,
  1 AS order_id,
  1 AS user_id,
  1 AS product_id,
  'complete' AS status,
  CAST(10.00 AS NUMERIC) AS sale_price,
  TIMESTAMP('2024-01-01 00:00:00') AS created_at;

CREATE OR REPLACE TABLE `__SOURCE_PROJECT__.__SOURCE_DATASET__.products` AS
SELECT
  1 AS id,
  CAST(5.00 AS NUMERIC) AS cost,
  CAST(10.00 AS NUMERIC) AS retail_price,
  'example' AS category,
  'example' AS department,
  'example' AS brand;

CREATE OR REPLACE TABLE `__SOURCE_PROJECT__.__SOURCE_DATASET__.users` AS
SELECT
  1 AS id,
  'ExampleCountry' AS country,
  'ExampleState' AS state,
  'ExampleCity' AS city,
  'ExampleGender' AS gender,
  'ExampleSource' AS traffic_source,
  TIMESTAMP('2023-12-01 00:00:00') AS created_at;
