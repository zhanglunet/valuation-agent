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

2.0 的目标是从"估值计算 Agent"升级为"投研分析 Agent"。

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

## 3.0 已实现

3.0 的目标是从"通用上市公司投研估值 Agent"升级为"上市公司战略价值与项目现金流穿透 Agent"。

- 项目级现金流模型：FCF / IRR / MOIC / Payback / NPV。
- 五情景分析（极悲观 / 悲观 / 基准 / 乐观 / 极乐观）+ 概率加权 NPV。
- 战略控制点 10 维评分 + 四因子映射到公司估值溢价。
- 风险期望损失矩阵（仅扣减基准情景，与五情景叙事不重复）。
- 价值归属（行级 owner_share 与项目级 partner_shares 互斥）。
- 竞争情报评分（复用 10 维 schema）。
- AI Agent / Harness 六维评估 + Token 调节器。
- 假设来源与置信度框架（L1–L5，禁止 L6 fabricated）。
- 报告骨架按 `--depth` 分支（strategic / project / agent）。
- 7 个 v3 Skills + 单一 CLI 入口。

详细设计见：[V3_DESIGN_AND_DEV_PLAN.md](V3_DESIGN_AND_DEV_PLAN.md)

## 3.x 后续增强

- 项目假设从公开披露文件（年报 / 公告 / 招股书）半自动抽取。
- Excel 财务模型导入器（把已有的项目模型转换为 ProjectAssumptions JSON）。
- 关键变量单变量 ±20% 敏感性自动呈现（接到报告"对公司整体估值的影响"章节）。
- 假设审计表导出独立 CSV / DOCX。
- 多项目组合估值（一家公司同时穿透多个战略项目）。

## 长期方向

- 月度 / 季度颗粒度现金流。
- DCF 完整模型与终值法。
- EV/EBITDA。
- 资本结构敏感性。
- 蒙特卡洛敏感性。
- DOCX / PPTX 输出。
- SQLite 缓存和报告版本归档。
