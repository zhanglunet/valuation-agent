# Skills 说明

## v1 / v2 Skills

### market-data-skill

根据公司名称、简称或股票代码自动查询公开行情；也支持用户输入或 seed 行情数据，返回股价、市值、总股本、交易日期和来源。公开接口结果会缓存到 `data/raw/`，需要最新数据时可传入 `refresh=true` 或 CLI `--refresh`。

中文简称优先通过 `config/company_aliases.json` 解析。

### financial-report-skill

根据公司名称、简称或股票代码自动查询公开财务摘要；也支持用户输入或 seed 财务数据，返回收入、净利润、经调整净利润、现金流、现金、债务和多期财务历史等核心指标。

### financial-normalization-skill

把财务数据统一到目标币种和标准单位。1.0 支持 CNY/HKD。

### valuation-skill

确定性估值计算：

- 目标市值倒推股价
- 隐含 PE
- 隐含 PS
- 不同 PE 下达成目标市值所需净利润

### scenario-analysis-skill

输出悲观、中性、乐观三情景。2.0 正式版基于公司当前净利率动态校准情景利润率：

- 收入预测
- 净利润预测
- PE / PS 估值
- 综合市值
- 对应股价

### peer-comparison-skill

2.0 已升级为真实可比公司分析：根据公司名称、简称或 ticker 匹配 `config/peer_groups.json`，批量获取同行公开数据，并计算 PE、PS、净利率、同行中位数、估值定位和每个同行的可比原因。

### research-report-skill

串联核心管线并生成 Markdown 投研报告。直接传入公司名称、简称或股票代码即可自动查找公开数据；也可手工传入 ticker、股本、收入、利润和目标市值覆盖公开数据。

支持：

```json
{"company_name":"<company>","depth":"deep"}
```

`depth=deep` 输出深度投研报告，包含可比公司分析、财务质量、增长驱动、风险反证和待验证问题。

可选强制刷新公开数据：

```json
{"company_name":"<company>","depth":"deep","refresh":true}
```

## v3 Skills

### project-valuation-skill

项目级现金流（FCF / IRR / MOIC / Payback / NPV）+ 五情景遍历 + 概率加权 NPV。输入 ProjectAssumptions JSON（每个数字字段必须带 source 等级，禁止 fabricated）。可选输入风险矩阵列表，自动从基准情景 NPV 中扣减期望损失。

```json
{
  "project_payload": "<path or inline JSON>",
  "risks_payload": "<optional list>"
}
```

### risk-expected-loss-skill

风险矩阵 + 期望损失计算。仅扣减基准情景 NPV；前置校验风险条目不与五情景叙事重复。

```json
{
  "project_payload": "<path or inline JSON>",
  "risks_payload": [{"risk_name": "...", "category": "...", "probability_by_scenario": {"base": 0.2}, "loss_by_scenario": {"base": {"value": 100, "source": "user_explicit"}}}]
}
```

### strategic-control-skill

10 维统一控制点评分 + 四因子映射到公司估值溢价（控制点 × 战略权重 × 收入占比 × 叙事放大）。

```json
{
  "control_scores": {"gateway_control": 80, "data_security": 75, "agent_lifecycle": 85, "industry_knowhow": 70, "channel_access": 60, "technology": 75, "system_integration": 70, "retention": 65, "resource_mobilization": 60, "repeatable_methodology": 70},
  "project_strategic_weight": 0.6,
  "project_revenue_share": 0.10,
  "narrative_amplification": 2.0
}
```

### competitive-scorecard-skill

复用 10 维 schema 对目标公司和竞争者评分，输出排名、相对优势/短板、相对位次的多倍数溢价建议。

```json
{
  "target_company": "<target>",
  "target_scores": {"gateway_control": 80, "...": 0},
  "competitor_scores": {"<peer1>": {...}, "<peer2>": {...}},
  "industry": "ai_agent_platform"
}
```

### value-attribution-skill

行级 owner_share 与项目级 partner_shares 互斥；输出归属上市公司的 NPV 与按 PE/PS 倍数换算的 market_cap_uplift。

```json
{
  "project_payload": "<path or inline JSON>",
  "partners_payload": [{"role": "listed_company", "share_ratio": {"value": 0.4, "source": "user_explicit"}}],
  "multiple": 12.0
}
```

### agent-harness-valuation-skill

AI Agent / Harness 项目六维加权（Model / Harness / Skill / Security / Workflow / Outcome）+ Token 调节器（0.5–1.5）+ 估值溢价带（discount / neutral / premium / platform_premium）。

```json
{
  "agent_scores": {"model_intelligence": 80, "harness_quality": 85, "skill_surface": 70, "identity_security_control": 75, "workflow_ownership": 80, "outcome_pricing_ability": 60},
  "token_cost_score": 70
}
```

### strategic-report-skill

3.0 综合战略估值报告。`depth=strategic` 输出公司级骨架；`depth=project|agent` 输出公司+项目骨架（agent 额外渲染 Agent/Harness 子节）。

```json
{
  "company_name": "<company>",
  "depth": "agent",
  "project_payload": "<path or inline JSON>",
  "risks_payload": "<optional>",
  "partners_payload": "<optional>",
  "control_scores": "<optional>",
  "competitive": "<optional>",
  "agent_scores": "<optional>",
  "token_cost_score": 70,
  "project_strategic_weight": 0.6,
  "project_revenue_share": 0.10,
  "narrative_amplification": 2.0,
  "multiple": 12
}
```
