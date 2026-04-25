---
name: research-report-skill
description: 生成结构化投研估值 Markdown 报告。1.0 会读取本地 seed 数据，串联估值、标准化和情景分析结果。
license: internal
---

# research-report-skill

## 输入

```json
{"ticker":"0700.HK","company_name":"腾讯控股","exchange":"HKEX","currency":"HKD","target_market_cap":4000000000000,"shares_outstanding":9500000000,"share_price":420,"revenue":650000000000,"adjusted_net_profit":180000000000}
```

## 调用

```bash
python3 research_report_skill.py '{"ticker":"0700.HK","company_name":"腾讯控股","exchange":"HKEX","currency":"HKD","target_market_cap":4000000000000,"shares_outstanding":9500000000,"share_price":420,"revenue":650000000000,"adjusted_net_profit":180000000000}'
```
