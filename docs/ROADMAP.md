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

## 2.0 计划开发

2.0 的目标是从“估值计算 Agent”升级为“投研分析 Agent”。

当前开发态已启动：

- `--depth deep` 深度报告入口。
- 可比公司分析初版。
- 财务质量分析初版。
- 增长驱动因素初版。
- 风险与反证初版。
- 待验证问题清单初版。

优先模块：

- 真实可比公司分析。
- 业务分部拆解。
- 财务质量分析。
- 增长驱动因素分析。
- 风险与反证分析。
- 待验证问题清单。
- 深度投研报告模板。

详细设计见：[V2_DESIGN_AND_DEV_PLAN.md](V2_DESIGN_AND_DEV_PLAN.md)

正式版开发计划见：[V2_FINAL_DESIGN_AND_DEV_PLAN.md](V2_FINAL_DESIGN_AND_DEV_PLAN.md)

## 2.x 后续增强

- 年报 PDF 深度解析。
- EV/EBITDA。
- DCF 简版。
- DOCX / PPTX 输出。
- SQLite 缓存和报告版本归档。
