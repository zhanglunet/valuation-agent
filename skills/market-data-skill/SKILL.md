---
name: market-data-skill
description: 获取上市公司行情快照。1.0 版本支持用户输入或本地 seed 数据，返回股价、市值、总股本、交易日期和来源。
license: internal
---

# market-data-skill

## 输入

```json
{"ticker":"0700.HK","currency":"HKD","share_price":420,"shares_outstanding":9500000000}
```

## 输出

返回 `MarketSnapshot` JSON。

## 调用

```bash
python3 market_data_skill.py '{"ticker":"0700.HK","currency":"HKD","share_price":420,"shares_outstanding":9500000000}'
```
