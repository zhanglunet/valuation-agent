---
name: risk-expected-loss-skill
description: Validate risk-matrix entries do not overlap with scenario narratives, then compute per-scenario expected loss (probability × loss). Subtracts only from base-case NPV.
license: internal
---

# risk-expected-loss-skill

## 输入

```json
{
  "project_payload": "<path or inline JSON for ProjectAssumptions>",
  "risks_payload": [
    {"risk_name": "<id>", "category": "financial",
     "probability_by_scenario": {"base": 0.2, "bear": 0.3},
     "loss_by_scenario": {"base": {"value": 100, "source": "user_explicit"}}}
  ]
}
```

## 调用

```bash
python3 risk_expected_loss_skill.py '{"project_payload": "<...>", "risks_payload": [...]}'
```
