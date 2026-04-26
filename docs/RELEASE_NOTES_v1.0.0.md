# Release Notes v1.0.0

## 版本摘要

`v1.0.0` 是 Valuation Agent 的第一个正式版本。该版本完成了从公司名称到基础估值报告的最小闭环。

用户只需要输入上市公司名称、简称或股票代码，系统即可自动检索公开信息，生成基础估值分析报告。

## 主要功能

- 支持公司名称、简称、ticker 输入。
- 支持中文别名解析，例如“腾讯”“苹果”“贵州茅台”。
- 自动获取公开行情、股价、市值、股本。
- 自动获取公开财务摘要，包括收入、净利润和平均股数等。
- 支持用户手工输入数据覆盖公开数据。
- 支持目标市值倒推股价。
- 支持隐含 PE / PS 测算。
- 支持不同 PE 假设下所需净利润测算。
- 支持悲观、中性、乐观三情景分析。
- 支持 Markdown 报告生成。
- 提供 Hermes Skills 包装。
- 提供飞书安装说明。

## Skills

本版本包含：

- `market-data-skill`
- `financial-report-skill`
- `financial-normalization-skill`
- `valuation-skill`
- `scenario-analysis-skill`
- `peer-comparison-skill`
- `research-report-skill`

## 使用示例

```bash
python3 -m valuation_agent.cli generate-report --query 腾讯
```

```bash
python3 skills/research-report-skill/research_report_skill.py '{"company_name":"腾讯"}'
```

飞书 / Hermes：

```text
@Hermes 请用 valuation-agent 分析腾讯控股
```

## 测试

发布前验证：

```bash
python3 -m unittest discover -s tests
```

结果：

```text
12 tests OK
```

## 已知限制

- 可比公司分析仍为占位实现。
- 尚未做业务分部深度拆解。
- 尚未做财务质量多期分析。
- 尚未做 DCF 和 EV/EBITDA。
- 尚未支持 DOCX / PPTX 输出。
- Yahoo Finance 数据存在延迟和口径差异，正式投研应以交易所公告和公司披露为准。

## 下一步

2.0 将从估值计算 Agent 升级为投研分析 Agent，重点增加：

- 可比公司分析。
- 业务分部拆解。
- 财务质量分析。
- 增长驱动因素。
- 风险与反证。
- 待验证问题清单。
- 深度投研报告模板。

