---
name: value-attribution-skill
description: Compute project-to-listed-company value attribution. Enforces row-level vs project-level methods are mutually exclusive. Outputs target NPV contribution and PE/PS-based market-cap uplift.
license: internal
---

# value-attribution-skill

## 输入

```json
{
  "project_payload": "<path or inline JSON for ProjectAssumptions>",
  "partners_payload": [
    {"role": "listed_company", "share_ratio": {"value": 0.4, "source": "user_explicit"}}
  ],
  "multiple": 12.0
}
```

## 调用

```bash
python3 value_attribution_skill.py '{"project_payload": "<...>", "partners_payload": [...]}'
```
