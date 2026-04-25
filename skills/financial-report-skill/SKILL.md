---
name: financial-report-skill
description: 获取上市公司财务报表核心指标。1.0 版本读取本地 seed 数据，返回收入、净利润、经调整净利润、EBITDA、现金流和来源。
license: internal
---

# financial-report-skill

## 输入

```json
{"company_id":"asiasoft_1675_hk"}
```

## 输出

返回 `FinancialStatement` JSON。

## 调用

```bash
python3 financial_report_skill.py '{"company_id":"asiasoft_1675_hk"}'
```
