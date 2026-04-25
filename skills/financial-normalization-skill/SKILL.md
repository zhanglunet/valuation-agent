---
name: financial-normalization-skill
description: 标准化财务数据的币种和单位。1.0 支持 CNY/HKD 与 yuan/million/billion/wan/yi。
license: internal
---

# financial-normalization-skill

## 输入

```json
{"currency":"HKD","revenue":650000000000,"adjusted_net_profit":180000000000,"target_currency":"HKD"}
```

## 调用

```bash
python3 financial_normalization_skill.py '{"currency":"HKD","revenue":650000000000,"adjusted_net_profit":180000000000,"target_currency":"HKD"}'
```
