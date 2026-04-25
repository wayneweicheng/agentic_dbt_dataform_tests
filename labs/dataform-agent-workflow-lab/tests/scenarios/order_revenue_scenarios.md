# Order Revenue Scenario Coverage

| Scenario | Business rule covered | Mock data rows | Expected outcome |
|---|---|---:|---|
| Happy path paid orders | Include paid orders and aggregate by date/customer | O100, O101 | C001 on 2026-01-01 has 2 orders and net revenue 140 |
| Status exclusion | Exclude cancelled and pending orders | O102, O104 | Rows do not contribute to output |
| Null discount | Treat null discount as zero | O101 | O101 contributes 50 net revenue |
| Duplicate order | Keep latest updated_at per order_id | O105 duplicate rows | Later O105 row contributes 125 net revenue |
| Null critical fields | Exclude missing order_id, customer_id, or order_ts | blank order_id, O107, O108 | Rows do not contribute to output |
| Non-positive net revenue | Exclude zero or negative net revenue | O103, O109 | Rows do not contribute to output |
| Multiple grains | Separate customers and dates | C001, C002, C003 | Separate rows by order_date/customer_id |
