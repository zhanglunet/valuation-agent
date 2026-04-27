---
name: project-valuation-skill
description: Compute project-level cash flow (FCF / IRR / MOIC / payback / NPV) across five scenarios with risk adjustment. Inputs ProjectAssumptions JSON; rejects fabricated sources.
license: internal
---

# project-valuation-skill

## 输入

```json
{
  "project_payload": "<path or inline JSON for ProjectAssumptions>",
  "risks_payload": "<optional list of risk-matrix entries>"
}
```

## 调用

```bash
python3 project_valuation_skill.py '{"project_payload": "<...>"}'
```
