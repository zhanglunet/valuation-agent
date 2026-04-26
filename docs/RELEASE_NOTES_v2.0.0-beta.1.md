# Release Notes v2.0.0-beta.1

## 版本摘要

`v2.0.0-beta.1` 是 Valuation Agent 2.0 的第一个测试版本。该版本从 1.0 的基础估值计算，升级为初步的深度投研分析。

核心变化是新增：

```bash
python3 -m valuation_agent.cli generate-report --query 腾讯 --depth deep
```

以及 Hermes Skill 调用：

```bash
python3 skills/research-report-skill/research_report_skill.py '{"company_name":"腾讯","depth":"deep"}'
```

## 新增功能

- 新增 `--depth deep` 深度报告入口。
- 新增 `config/peer_groups.json` 同行公司池。
- 新增 `valuation_agent/research_analysis.py` 研究分析模块。
- 升级 `peer-comparison-skill`，从占位实现变成真实可比公司分析初版。
- 升级 `research-report-skill`，支持基础报告和深度报告。
- 新增财务质量分析：
  - 净利率。
  - 盈利收益率。
  - PE / PS 质量标记。
- 新增可比公司分析：
  - 同行公司批量公开数据获取。
  - PE / PS / 净利率。
  - 同行中位数。
  - 目标公司相对定位。
- 新增增长驱动因素分析。
- 新增风险与反证分析。
- 新增待验证问题清单。
- 新增深度投研 Markdown 报告模板。

## 示例

```bash
python3 -m valuation_agent.cli generate-report --query 腾讯 --depth deep
```

输出：

```text
data/reports/0700_hk_deep_research_report.md
```

## 测试

发布前验证：

```bash
python3 -m unittest discover -s tests
```

结果：

```text
16 tests OK
```

## Beta 限制

- 业务分部拆解仍以缺失提示为主，尚未解析年报 PDF。
- 可比公司池是手工维护的初版，覆盖有限。
- 同行数据依赖 Yahoo Finance 公开接口，可能存在延迟、缺失或口径差异。
- 尚未实现 DCF、EV/EBITDA、DOCX/PPTX。
- 深度报告仍需要人工复核，不能作为投资建议。

## 后续计划

2.0 正式版将继续完善：

- 业务分部提取。
- 财务质量多期趋势。
- 更高质量同行池。
- 风险反证规则细化。
- 年报 / 公告公开资料抓取。
- 更稳定的数据缓存和来源追踪。

