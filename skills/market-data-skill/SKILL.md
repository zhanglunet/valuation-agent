---
name: market-data-skill
description: 获取上市公司行情快照。1.0 版本读取本地 seed 数据，返回股价、市值、总股本、交易日期和来源。适用于亚信科技 1675.HK 的估值 MVP。
license: internal
---

# market-data-skill

## 输入

```json
{"company_id":"asiasoft_1675_hk"}
```

## 输出

返回 `MarketSnapshot` JSON。

## 调用

```bash
python3 market_data_skill.py '{"company_id":"asiasoft_1675_hk"}'
```
