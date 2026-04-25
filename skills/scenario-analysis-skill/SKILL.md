---
name: scenario-analysis-skill
description: 生成悲观、中性、乐观三情景估值分析。基于收入、净利率、PE、PS 和总股本计算综合市值与目标股价。
license: internal
---

# scenario-analysis-skill

## 输入

```json
{"currency":"HKD","revenue":650000000000,"shares_outstanding":9500000000}
```

## 调用

```bash
python3 scenario_analysis_skill.py '{"currency":"HKD","revenue":650000000000,"shares_outstanding":9500000000}'
```
