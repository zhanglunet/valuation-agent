---
name: valuation-skill
description: 做确定性估值测算，包括目标市值倒推股价、隐含 PE、隐含 PS、不同 PE 下所需净利润。适用于“亚信 200 亿市值对应股价多少”等问题。
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

如果只传 `company_id`，Skill 会读取本地 seed 数据并自动标准化。

## 调用

```bash
python3 valuation_skill.py '{"company_id":"asiasoft_1675_hk"}'
```
