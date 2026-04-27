---
name: strategic-report-skill
description: 3.0 综合战略估值报告。`depth=strategic` 输出公司级骨架，`depth=project|agent` 输出公司+项目骨架（agent 额外渲染 Agent/Harness 子节）。
license: internal
---

# strategic-report-skill

## 输入

```json
{
  "company_name": "<company>",
  "depth": "agent",
  "project_payload": "<path or inline JSON>",
  "risks_payload": "<optional>",
  "partners_payload": "<optional>",
  "control_scores": "<optional>",
  "competitive": "<optional>",
  "agent_scores": "<optional>",
  "token_cost_score": 70,
  "project_strategic_weight": 0.6,
  "project_revenue_share": 0.10,
  "narrative_amplification": 2.0,
  "multiple": 12
}
```

## 调用

```bash
python3 strategic_report_skill.py '{"company_name": "<company>", "depth": "agent", ...}'
```
