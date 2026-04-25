# Tech Spec Extraction Reference

Use this schema when extracting implementation requirements from a technical specification.

## Required fields

```yaml
objective: string
source_tables:
  - name: string
    columns:
      - name: string
        type: string
        required: boolean
target_tables:
  - name: string
    grain: string
    columns:
      - name: string
        type: string
business_rules:
  - id: string
    description: string
    category: filter | dedupe | transform | aggregate | quality
acceptance_criteria:
  - id: string
    description: string
scenarios:
  - id: string
    description: string
```

## Extraction rules

- Preserve the original wording of business rules when possible.
- Do not invent columns, statuses, filters, or target outputs.
- Mark missing information as `unresolved` rather than guessing.
- Separate source contract, target contract, and transformation logic.
