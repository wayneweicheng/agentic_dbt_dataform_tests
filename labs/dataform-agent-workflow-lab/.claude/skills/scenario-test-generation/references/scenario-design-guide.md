# Scenario Design Guide

## Purpose

Scenario generation turns business rules and acceptance criteria into concrete input rows and expected output rows.

## Scenario types

- positive path: valid records that should appear in output
- negative path: invalid records that should be excluded
- edge case: nulls, duplicates, zero values, and boundary timestamps
- grain case: multiple customers or dates that prove grouping logic

## Required mapping

Each scenario should map to:

- source input rows
- business rule under test
- expected target row or expected exclusion
- validation notes

## Naming convention

Use concise scenario IDs such as:

- `S01_paid_orders_aggregate`
- `S02_status_exclusion`
- `S03_duplicate_latest_update`
