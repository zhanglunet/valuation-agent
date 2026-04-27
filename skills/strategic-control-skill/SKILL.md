---
name: strategic-control-skill
description: Score a project on the unified 10-dimension control-point schema and apply the four-factor mapping to produce a company-level valuation premium.
license: internal
---

# strategic-control-skill

## 输入

```json
{
  "control_scores": {"gateway_control": 80, "data_security": 70, "...": 0},
  "project_strategic_weight": 0.6,
  "project_revenue_share": 0.10,
  "narrative_amplification": 2.0
}
```

## 调用

```bash
python3 strategic_control_skill.py '{"control_scores": {...}}'
```
