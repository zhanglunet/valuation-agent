# Valuation Agent v3.0.0 Release Notes

Release date: 2026-04-28

## Highlights

3.0 把 valuation-agent 从"通用上市公司投研估值 Agent"升级为"上市公司战略价值与项目现金流穿透 Agent"。在 2.0 的公司级深度投研基础上，新增项目级经营模型、五情景分析、战略控制点评分、风险期望损失矩阵、价值归属、AI Agent / Harness 估值框架，以及强制的假设来源审计。

## What's New

- **项目级现金流模型**：FCF / IRR / MOIC / Payback / NPV，五情景遍历与概率加权 NPV。
- **五情景分析**：极悲观 / 悲观 / 基准 / 乐观 / 极乐观。每情景独立调整收入倍率、毛利、归属比例、折现率和 CAPEX，并可激活专属风险条目。
- **战略控制点评分**：10 维统一 schema（gateway / data_security / agent_lifecycle / industry_knowhow / channel_access / technology / system_integration / retention / resource_mobilization / repeatable_methodology）+ 四因子映射到公司估值溢价。
- **风险期望损失**：按情景的概率/损失矩阵；仅扣减基准情景 NPV；前置校验风险条目不与五情景叙事重复。
- **价值归属**：行级 owner_share 与项目级 partner_shares 互斥；NPV 与 market_cap_uplift 两步分离。
- **AI Agent / Harness 估值**：六维加权 + Token 调节器（0.5–1.5）+ 估值溢价带映射。
- **假设来源框架**：每条数字带 source 等级（L1 user_explicit ~ L5 derived）；禁止 L6 fabricated；报告强制输出"假设审计表"；L1+L2 占比低于 50% 报告头部打"高假设依赖"警示。
- **CLI 单一入口**：`generate-report --depth {basic, deep, strategic, project, agent}`。
- **Hermes Skills**：新增 7 个 Skills（`project-valuation-skill` / `risk-expected-loss-skill` / `strategic-control-skill` / `competitive-scorecard-skill` / `value-attribution-skill` / `agent-harness-valuation-skill` / `strategic-report-skill`）。

## Example

```bash
python3 -m valuation_agent.cli generate-report \
  --query <company> \
  --depth agent \
  --project-assumptions ./assumptions/<project>.json \
  --agent-scores '{"model_intelligence":80,"harness_quality":85,"skill_surface":70,"identity_security_control":75,"workflow_ownership":80,"outcome_pricing_ability":60}' \
  --token-cost-score 70 \
  --project-strategic-weight 0.6 \
  --project-revenue-share 0.10 \
  --narrative-amplification 2.0 \
  --multiple 12
```

## Validation

- Unit tests: `64 passed`
- Smoke test: end-to-end project report generated successfully via `--depth agent`.

## Boundaries

3.0 不承诺：

- 自动准确解析所有 Excel 财务模型。
- 自动获取所有非公开项目数据。
- 月度/季度颗粒度现金流（仅年度）。
- 蒙特卡洛敏感性。
- 资本结构优化、税盾建模、可转债稀释。
- IRR hurdle rate 建议或资本预算判断。
- LLM 编造（fabricated）的项目假设。

3.0 承诺：

- 公开市场数据可追溯。
- 项目假设可显式展示，且每条数字带 source 与 confidence。
- 财务公式可审计。
- 风险调整可解释，且与五情景叙事不重复扣减。
- 价值归属不混淆，行级与项目级分账互斥。
- 控制点溢价经过四因子映射，不被错误放大到公司整体估值。
- 缺失信息不编造。

## Notes

The system is for research assistance only and does not constitute investment advice. Public data may be delayed or use different reporting definitions; formal investment research should verify exchange announcements, annual reports, and company filings.
