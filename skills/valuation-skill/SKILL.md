---
name: valuation-skill
description: 做确定性估值测算，包括目标市值倒推股价、隐含 PE、隐含 PS、不同 PE 下所需净利润。适用于任意上市公司的目标市值和股价测算。
license: internal
---

# valuation-skill

## 输入

```json
{
  "target_market_cap": 20000000000,
  "shares_outstanding": 950000000,
  "revenue": 8640000000,
  "net_profit": 864000000,
  "currency": "HKD"
}
```

如果传 `company_id`，Skill 会读取本地 seed 示例数据并自动标准化；如果直接传财务和行情参数，则可分析任意上市公司。

## 调用

```bash
python3 valuation_skill.py '{"target_market_cap":20000000000,"shares_outstanding":950000000,"revenue":8640000000,"net_profit":864000000,"currency":"HKD"}'
```
