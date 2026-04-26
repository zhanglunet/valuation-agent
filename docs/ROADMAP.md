# Roadmap

## 1.0 已实现

- 离线 seed 数据闭环。
- 任意上市公司的公司名/简称/股票代码自动检索分析。
- 一个本地 seed 示例用于回归测试。
- 市值倒推股价。
- PE / PS 隐含倍数。
- 三情景分析。
- Markdown 报告。
- Hermes Skills 包装。
- 单元测试和集成测试。

## 2.0 已实现

2.0 的目标是从“估值计算 Agent”升级为“投研分析 Agent”。

- `--depth deep` 深度报告入口。
- 公开数据本地缓存与 `--refresh`。
- 可比公司分析、同行中位数和可比原因。
- 业务分部 profile 框架。
- 财务质量分析和多期财务趋势。
- 增长驱动因素初版。
- 风险规则和反证测试。
- 待验证问题清单初版。
- 动态情景利润率假设。
- 深度投研报告模板。

详细设计见：[V2_DESIGN_AND_DEV_PLAN.md](V2_DESIGN_AND_DEV_PLAN.md)

正式版开发计划见：[V2_FINAL_DESIGN_AND_DEV_PLAN.md](V2_FINAL_DESIGN_AND_DEV_PLAN.md)

## 2.x 后续增强

- 年报 PDF 深度解析。
- 更多行业的业务分部 profile 和同行池。
- EV/EBITDA。
- DCF 简版。
- DOCX / PPTX 输出。
- SQLite 缓存和报告版本归档。
