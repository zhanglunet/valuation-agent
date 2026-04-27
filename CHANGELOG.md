# Changelog

## v3.0.0 - 2026-04-28

### Added

- 项目级现金流模型 `project_valuation`（FCF / IRR / MOIC / Payback / NPV / 五情景遍历 / 概率加权）。
- 战略控制点评分 `strategic_control`（10 维统一 schema + 四因子映射到公司估值溢价）。
- 风险期望损失 `risk_expected_loss`（按情景概率/损失矩阵；仅扣减基准情景，不与五情景叙事重复）。
- 价值归属 `value_attribution`（行级 owner_share 与项目级 partner_shares 互斥）。
- 竞争情报评分 `competitive_scorecard`（复用 10 维 schema，输出排名/优势/短板/相对位次溢价建议）。
- AI Agent / Harness 估值 `agent_harness_valuation`（六维加权 + Token 调节器 + 估值溢价带）。
- 假设来源与置信度框架 `assumption_validator`（L1–L5 来源等级、禁止 L6 fabricated、归属互斥校验、概率和校验、风险/情景重复校验、报告假设审计表）。
- 条件骨架报告渲染器 `reporting_v3`（`strategic` 公司级 12 节 / `project` 公司+项目 13 节 / `agent` 项目骨架 + Agent/Harness 子节）。
- CLI `generate-report --depth {strategic,project,agent}` 与对应参数 `--project-assumptions / --risks / --partners / --control-scores / --competitive / --agent-scores / --token-cost-score / --project-strategic-weight / --project-revenue-share / --narrative-amplification / --multiple`。
- 7 个 v3 Skills：`project-valuation-skill`、`risk-expected-loss-skill`、`strategic-control-skill`、`competitive-scorecard-skill`、`value-attribution-skill`、`agent-harness-valuation-skill`、`strategic-report-skill`。
- v3 配置：`config/strategic_control_weights.json`、`config/competitive_scorecards.json`、`config/agent_harness_weights.json`、`config/project_templates.json`、`config/risk_matrix_templates.json`、`config/partner_split_templates.json`。
- 单元测试 `test_assumption_validator.py`、`test_project_valuation.py`、`test_strategic_control.py`、`test_risk_expected_loss.py`、`test_competitive_scorecard.py`、`test_value_attribution.py`、`test_agent_harness_valuation.py`、`test_reporting_v3.py`，共 64 用例全部通过。

### Changed

- `schemas.py` 扩充 `SourcedValue`、`ProjectAssumptions`、`ScenarioOverride`、`CashFlowResult`、`StrategicControlScore`、`CompetitiveScoreResult`、`RiskExpectedLoss`、`ValueAttribution`、`AgentHarnessScore`、`AssumptionAudit`。
- 文档全部脱敏（移除具体公司名称示例，使用 `<company>` / `<某上市公司>` 占位符）。

### Known Limitations

- 项目假设来源仍依赖用户/披露/模板，3.0 不会自动从年报 PDF 或 Excel 抽取项目级数据。
- 五情景与风险矩阵需要人工配置；3.0 未做蒙特卡洛敏感性。
- 公开市场数据继承 v2，依赖 Yahoo Finance 公开接口。

## v2.0.0 - 2026-04-26

### Added

- Added public data JSON cache under `data/raw/` with `--refresh` support.
- Added business segment profiles for representative listed companies.
- Added configurable risk rules.
- Added peer comparison reasons and cleaner peer median filtering.
- Added multi-period financial history analysis, CAGR, margin trend, and share count change.
- Added deep report sections for business segments, financial trend tables, missing items, peer reasons, and risk/refutation checks.
- Added dynamic scenario margins based on the company's current profitability.
- Added tests for cache, business profiles, financial history, risk rules, and dynamic scenarios.

### Changed

- Promoted deep research mode from beta to the 2.0 formal implementation.
- Updated Skills and CLI docs for `depth=deep` and `refresh`.
- Improved `scenario-analysis-skill` to use the same dynamic scenario logic as the core pipeline.

### Known Limitations

- Business segment details are profile-based and still require annual report verification.
- Peer groups are curated and should be expanded by industry.
- Public data depends on Yahoo Finance endpoints and should be verified against official filings.

## v2.0.0-beta.1 - 2026-04-26

### Added

- Added `--depth deep` deep research report mode.
- Added `config/peer_groups.json`.
- Added `valuation_agent/research_analysis.py`.
- Added first working peer comparison analysis.
- Added financial quality analysis.
- Added growth driver analysis.
- Added risk and refutation analysis.
- Added research question list generation.
- Added deep research Markdown report template.
- Added tests for research analysis.

### Changed

- Upgraded `peer-comparison-skill` from placeholder to working beta implementation.
- Upgraded `research-report-skill` to support `depth=deep`.
- Updated version to `2.0.0-beta.1`.

### Known Limitations

- Business segment analysis is still a missing-data prompt rather than full extraction.
- Peer groups are manually curated and limited.
- Public data depends on Yahoo Finance endpoints and should be verified against official filings.

## v1.0.0 - 2026-04-26

### Added

- First formal release of Valuation Agent.
- Company name / alias / ticker based lookup.
- Chinese alias mapping via `config/company_aliases.json`.
- Public market data lookup using Yahoo Finance public endpoints.
- Market snapshot extraction.
- Financial summary extraction.
- PE / PS valuation.
- Market-cap-to-share-price calculation.
- Required net profit by target PE.
- Bear / base / bull scenario analysis.
- Markdown report generation.
- Hermes Skills wrappers.
- Feishu / Hermes installation documentation.
- Unit and integration tests.

### Known Limitations

- Peer comparison is still a placeholder.
- Business segment analysis is not implemented.
- Financial quality analysis is not implemented.
- DCF and EV/EBITDA are not implemented.
- DOCX / PPTX export is not implemented.
