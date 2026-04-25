# Tech Spec: Daily Customer Revenue Mart

## Objective

Create a Dataform pipeline that transforms raw order events into a daily customer revenue mart.

## Source table

Logical source table:

```text
raw_order_events
```

Expected columns:

| Column | Type | Description |
|---|---|---|
| order_id | STRING | Unique order identifier |
| customer_id | STRING | Customer identifier |
| order_ts | TIMESTAMP | Order event timestamp |
| status | STRING | Order status |
| amount | NUMERIC | Gross order amount |
| discount_amount | NUMERIC | Discount applied to the order |
| currency | STRING | Currency code |
| updated_at | TIMESTAMP | Last update timestamp |

## Business rules

1. Include only orders where `status = 'PAID'`.
2. Exclude orders with null `order_id`, null `customer_id`, or null `order_ts`.
3. Net revenue is `amount - discount_amount`.
4. Treat null `discount_amount` as zero.
5. Exclude orders where net revenue is less than or equal to zero.
6. If duplicate rows exist for the same `order_id`, keep the row with the latest `updated_at`.
7. Aggregate to customer and order date grain.
8. `order_date` is derived from `DATE(order_ts)`.
9. Output one row per `order_date` and `customer_id`.

## Target table

Logical target table:

```text
daily_customer_revenue
```

Expected columns:

| Column | Type | Description |
|---|---|---|
| order_date | DATE | Order date |
| customer_id | STRING | Customer identifier |
| order_count | INT64 | Count of included paid orders |
| gross_revenue | NUMERIC | Sum of gross amount |
| discount_amount | NUMERIC | Sum of discount amount after null handling |
| net_revenue | NUMERIC | Sum of net revenue |
| first_order_ts | TIMESTAMP | First included order timestamp for the customer/date |
| last_order_ts | TIMESTAMP | Last included order timestamp for the customer/date |

## Required scenarios

1. Happy path paid orders aggregate correctly.
2. Cancelled and pending orders are excluded.
3. Null discount is treated as zero.
4. Duplicate `order_id` keeps latest `updated_at`.
5. Null critical fields are excluded.
6. Zero or negative net revenue is excluded.
7. Multiple customers and dates produce separate rows.

## Acceptance criteria

- Dataform compiles successfully.
- Scenario test report maps every required scenario to mock input and expected output.
- Actual output matches expected output for supplied mock data.
- Code review finds no blocking correctness issue.
