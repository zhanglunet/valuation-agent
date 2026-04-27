from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .agent_harness_valuation import evaluate_agent_harness
from .assumption_validator import build_assumption_audit
from .competitive_scorecard import score_competitors
from .paths import REPORTS_DIR
from .pipeline import run_payload_analysis
from .project_valuation import build_project_cashflow
from .risk_expected_loss import evaluate_risks
from .schemas import (
    SCENARIO_NAMES,
    AgentHarnessScore,
    AssumptionAudit,
    CashFlowResult,
    CompetitiveScoreResult,
    PartnerShare,
    ProjectAssumptions,
    RiskExpectedLoss,
    SourcedValue,
    StrategicControlScore,
    ValueAttribution,
)
from .strategic_control import evaluate_strategic_control
from .value_attribution import evaluate_value_attribution


SCENARIO_LABELS_CN: dict[str, str] = {
    "very_bear": "极悲观",
    "bear": "悲观",
    "base": "基准",
    "bull": "乐观",
    "very_bull": "极乐观",
}


def _money(value: float | None) -> str:
    if value is None:
        return "缺失"
    if abs(value) >= 1e8:
        return f"{value / 1e8:.2f} 亿"
    if abs(value) >= 1e4:
        return f"{value / 1e4:.2f} 万"
    return f"{value:.2f}"


def _pct(value: float | None) -> str:
    if value is None:
        return "缺失"
    return f"{value * 100:.1f}%"


# ---------------------------------------------------------------------------
# Skeleton 1: company-only — extends v2 deep report with a control-point
# preview (12 sections total).
# ---------------------------------------------------------------------------


def _render_control_preview(
    control: StrategicControlScore | None,
) -> str:
    if control is None:
        return "暂无战略控制点初评。可在请求中传入 `control_scores` 字段触发评分。"
    rows = "\n".join(
        f"| {d.name} | {d.score:.0f} | {d.weight:.2f} |"
        for d in control.dimensions
    )
    explain = "\n".join(f"- {line}" for line in control.explanation)
    return (
        "| 维度 | 评分 | 权重 |\n"
        "|---|---|---|\n"
        f"{rows}\n\n"
        f"加权总分：**{control.weighted_score:.1f}/100**\n\n"
        f"估值溢价系数（四因子映射）：**{control.valuation_premium:.4f}**\n\n"
        f"{explain}\n"
    )


def render_company_only_skeleton(
    company_payload: dict[str, Any],
    control: StrategicControlScore | None,
    audit: AssumptionAudit | None,
) -> str:
    company_name = company_payload.get("company_name") or company_payload.get("query", "<company>")
    audit_block = _render_audit_section(audit) if audit else "本次分析未生成假设审计表。"
    return f"""# {company_name} 战略投研报告（v3 公司级）

> 本报告由 valuation-agent 3.0 生成。3.0 在 v2 深度投研报告基础上增加战略控制点初评。

## 1. 核心结论

公司级判断仍以公开市场数据为基础。如果该公司战略价值由具体项目驱动，请使用 `--depth project` 或 `--depth agent` 调用项目级流程。

## 2. 公司与市场概览

公开行情、市值、股本、行业等数据请见 v2 深度报告（生成于 `data/reports/`）。

## 3. 业务分部拆解

继承 v2 业务分部模块。

## 4. 财务质量与趋势

继承 v2 多期财务质量分析。

## 5. 增长驱动因素

继承 v2 增长驱动分析。

## 6. 可比公司分析

继承 v2 同行池中位数与可比性说明。

## 7. 估值分析与交叉验证

继承 v2 PE/PS 倍数与目标市值倒推。

## 8. 战略控制点初评

3.0 新增。控制点评分使用统一 10 维 schema（见配置 `config/strategic_control_weights.json`）。

{_render_control_preview(control)}

## 9. 情景与敏感性分析

继承 v2 三情景分析。如需五情景与项目现金流，请改用 `--depth project`。

## 10. 风险与反证

继承 v2 风险规则。3.0 项目级流程额外提供期望损失矩阵。

## 11. 待验证问题清单

继承 v2 待验证问题。

## 12. 数据来源、缺失项与免责声明

{audit_block}

本系统仅用于研究分析辅助，不构成投资建议。
"""


# ---------------------------------------------------------------------------
# Skeleton 2: company + project — 13 sections, with optional Agent/Harness
# subsection inserted under section 10.
# ---------------------------------------------------------------------------


def _render_scenario_table(cashflow: CashFlowResult) -> str:
    lines = ["| 情景 | 概率 | NPV | IRR | MOIC | 回收期 | 折现率 |", "|---|---|---|---|---|---|---|"]
    for name in SCENARIO_NAMES:
        if name not in cashflow.by_scenario:
            continue
        sc = cashflow.by_scenario[name]
        lines.append(
            "| {label} | {p:.0%} | {npv} | {irr} | {moic} | {pb} | {dr:.1%} |".format(
                label=SCENARIO_LABELS_CN.get(name, name),
                p=sc.scenario_probability,
                npv=_money(sc.npv),
                irr=f"{sc.irr*100:.1f}%" if sc.irr is not None else "不存在",
                moic=f"{sc.moic:.2f}x" if sc.moic is not None else "不可计算",
                pb=f"{sc.payback_year:.2f} 年" if sc.payback_year is not None else "未回收",
                dr=sc.discount_rate,
            )
        )
    return "\n".join(lines)


def _render_base_cashflow_table(cashflow: CashFlowResult) -> str:
    base = cashflow.by_scenario.get("base") or next(iter(cashflow.by_scenario.values()))
    years = sorted(base.annual_revenue.keys())
    rows = ["| 年份 | 收入 | 成本合计 | EBIT | 税 | FCF | 累计 FCF |", "|---|---|---|---|---|---|---|"]
    for y in years:
        rows.append(
            f"| {y} | {_money(base.annual_revenue.get(y))} | {_money(base.annual_cost.get(y))} | "
            f"{_money(base.annual_ebit.get(y))} | {_money(base.annual_tax.get(y))} | "
            f"{_money(base.annual_fcf.get(y))} | {_money(base.cumulative_fcf.get(y))} |"
        )
    return "\n".join(rows)


def _render_audit_section(audit: AssumptionAudit) -> str:
    rows = ["| 字段 | 数值 | 来源 | 置信度 | 备注 |", "|---|---|---|---|---|"]
    for e in audit.entries:
        rows.append(
            f"| {e.field_path} | {e.value:.4g} | {e.source} | {e.confidence:.2f} | {e.source_detail or ''} |"
        )
    warning = ""
    if audit.warning_label:
        warning = f"\n> ⚠️ 警示：`{audit.warning_label}`，L1+L2 高置信度来源占比 {audit.high_confidence_share:.0%}。\n"
    return warning + "\n".join(rows)


def _render_risk_block(
    risks: list[RiskExpectedLoss],
    risk_summary: dict[str, Any],
) -> str:
    if not risks:
        return "未配置风险矩阵条目。"
    rows = ["| 风险 | 类别 | 基准概率 | 基准损失 | 基准期望损失 | 缓解 |", "|---|---|---|---|---|---|"]
    for r in risks:
        prob = r.probability_by_scenario.get("base", 0.0)
        loss_sv = r.loss_by_scenario.get("base")
        loss = loss_sv.value if loss_sv else 0.0
        el = r.expected_loss_by_scenario.get("base", prob * loss)
        rows.append(
            f"| {r.risk_name} | {r.category} | {prob:.0%} | {_money(loss)} | {_money(el)} | {r.mitigation} |"
        )
    rows.append("")
    rows.append(f"基准情景期望损失合计：**{_money(risk_summary.get('total_expected_loss_base', 0.0))}**")
    rows.append("")
    rows.append(
        "注：风险矩阵仅扣减基准情景 NPV，不与五情景叙事重复扣减（V3 设计 §3.3 / §3.4 边界）。"
    )
    return "\n".join(rows)


def _render_attribution_block(attribution: ValueAttribution) -> str:
    partner_rows = (
        ["| 角色 | 分账比例 | 说明 |", "|---|---|---|"]
        + [
            f"| {p.role} | {p.share_ratio.value:.1%} | {p.description or ''} |"
            for p in attribution.partner_shares
        ]
        if attribution.partner_shares
        else ["（未配置 partner_shares，使用行级 owner_share 分账）"]
    )
    total_rev = sum(attribution.total_project_revenue.values())
    target_rev = sum(attribution.target_company_revenue.values())
    return (
        f"分账方法：`{attribution.method}`\n\n"
        + "\n".join(partner_rows)
        + "\n\n"
        f"| 指标 | 值 |\n|---|---|\n"
        f"| 项目总收入（合作方合计） | {_money(total_rev)} |\n"
        f"| 归属上市公司收入 | {_money(target_rev)} |\n"
        f"| 归属比例 | {attribution.attribution_ratio:.1%} |\n"
        f"| 归属上市公司 NPV | {_money(attribution.target_company_npv_contribution)} |\n"
        f"| 估值倍数换算市值增量 | {_money(attribution.target_company_market_cap_uplift)} |\n"
    )


def _render_control_block(control: StrategicControlScore) -> str:
    return _render_control_preview(control)


def _render_competitive_block(comp: CompetitiveScoreResult) -> str:
    rows = ["| 公司 | 加权评分 |", "|---|---|"]
    rows.append(f"| **{comp.target_company}**（目标） | {comp.target_scorecard.weighted_score:.1f} |")
    for c in comp.competitor_scorecards:
        rows.append(f"| {c.company} | {c.weighted_score:.1f} |")
    extra = []
    if comp.target_strengths:
        extra.append("**优势**：" + "；".join(comp.target_strengths))
    if comp.target_weaknesses:
        extra.append("**短板**：" + "；".join(comp.target_weaknesses))
    extra.append("\n".join(comp.explanation))
    return "\n".join(rows) + "\n\n" + "\n\n".join(extra)


def _render_agent_block(score: AgentHarnessScore) -> str:
    rows = ["| 维度 | 评分 | 权重 |", "|---|---|---|"]
    for name in (
        "model_intelligence",
        "harness_quality",
        "skill_surface",
        "identity_security_control",
        "workflow_ownership",
        "outcome_pricing_ability",
    ):
        rows.append(f"| {name} | {getattr(score, name):.0f} | {score.weights.get(name, 0):.2f} |")
    explain = "\n".join(f"- {line}" for line in score.explanation)
    return (
        "\n".join(rows)
        + f"\n\n加权 Agent value score = **{score.agent_value_score:.1f}/100**；"
        f"Token 调节器 = **{score.token_efficiency_modifier:.2f}**；"
        f"Final = **{score.final_agent_score:.1f}** -> 估值带 `{score.valuation_premium_band}`\n\n"
        + explain
    )


def render_company_plus_project_skeleton(
    company_name: str,
    project_name: str,
    cashflow: CashFlowResult,
    risks: list[RiskExpectedLoss],
    risk_summary: dict[str, Any],
    attribution: ValueAttribution,
    control: StrategicControlScore | None,
    competitive: CompetitiveScoreResult | None,
    agent_score: AgentHarnessScore | None,
    audit: AssumptionAudit,
) -> str:
    base_npv = next(iter(cashflow.by_scenario.values())).npv
    pw_npv = cashflow.probability_weighted_npv
    risk_adj_npv = cashflow.risk_adjusted_base_npv
    agent_section = ""
    if agent_score is not None:
        agent_section = "\n### 10.1 Agent / Harness 估值框架\n\n" + _render_agent_block(agent_score) + "\n"
    competitive_block = (
        _render_competitive_block(competitive)
        if competitive
        else "未配置竞争评分。"
    )
    return f"""# {company_name} × {project_name}（v3 项目级战略估值报告）

> 由 valuation-agent 3.0 生成。本报告穿透 *项目假设 → 五情景现金流 → 风险扣减 → 价值归属 → 公司估值溢价* 的全链路。

## 1. 核心结论（公司级 + 项目级 + 战略级）

- 项目基准情景 NPV：**{_money(base_npv)}**
- 概率加权 NPV：**{_money(pw_npv)}**
- 基准情景风险调整后 NPV：**{_money(risk_adj_npv)}**
- 归属上市公司 NPV：**{_money(attribution.target_company_npv_contribution)}**
- 通过估值倍数换算的市值增量：**{_money(attribution.target_company_market_cap_uplift)}**

## 2. 公司级估值摘要

公司级数据请参考 v2 深度报告。本节用于把项目结论挂回公司整体叙事。

## 3. 战略项目描述

`{project_name}` 项目的核心假设、合作结构和价值主张应在此描述。3.0 不会编造非公开信息。

## 4. 项目假设审计表

3.0 强制要求每条假设带 source 等级（user_explicit / disclosed / template / analogy / derived，禁止 fabricated）。

{_render_audit_section(audit)}

## 5. 五年经营模型（基准情景）

{_render_base_cashflow_table(cashflow)}

## 6. FCF / IRR / MOIC / 回收期（基准情景）

| 指标 | 值 |
|---|---|
| 基准 NPV | {_money(base_npv)} |
| 基准 IRR | {f"{cashflow.by_scenario['base'].irr*100:.1f}%" if 'base' in cashflow.by_scenario and cashflow.by_scenario['base'].irr is not None else '不存在'} |
| 基准 MOIC | {f"{cashflow.by_scenario['base'].moic:.2f}x" if 'base' in cashflow.by_scenario and cashflow.by_scenario['base'].moic is not None else '不可计算'} |
| 基准回收期 | {f"{cashflow.by_scenario['base'].payback_year:.2f} 年" if 'base' in cashflow.by_scenario and cashflow.by_scenario['base'].payback_year is not None else '未回收'} |

## 7. 五情景分析与概率加权 NPV

{_render_scenario_table(cashflow)}

> 概率加权 NPV = Σ(情景概率 × 情景 NPV) = **{_money(pw_npv)}**

## 8. 风险期望损失

{_render_risk_block(risks, risk_summary)}

## 9. 价值归属与分账

{_render_attribution_block(attribution)}

## 10. 战略控制点评分

{_render_control_block(control) if control else '未配置 control_scores。'}
{agent_section}
## 11. 竞争情报评分

{competitive_block}

## 12. 对公司整体估值的影响

- 项目归属 NPV：{_money(attribution.target_company_npv_contribution)}
- 通过估值倍数换算的市值增量：{_money(attribution.target_company_market_cap_uplift)}
- 控制点四因子映射后的估值溢价系数：{control.valuation_premium if control else '未评估'}

注：项目级 NPV 与公司估值溢价是两条**互补**的路径，请勿同时叠加；建议根据项目重要性择一对外披露。

## 13. 待验证问题、数据来源、假设审计与免责声明

- 详见 §4 假设审计表。
- 公开数据来源继承 v2（Yahoo Finance + 配置）。
- 本系统仅用于研究分析辅助，不构成投资建议。
"""


# ---------------------------------------------------------------------------
# Top-level dispatcher.
# ---------------------------------------------------------------------------


def _to_assumptions(payload: dict[str, Any]) -> ProjectAssumptions:
    """Light-touch parser: payload may contain ProjectAssumptions-like dicts.
    JSON inputs are rebuilt into dataclasses so the rest of the pipeline can
    rely on typed attributes."""
    from .schemas import (
        CostLine,
        ProjectAssumptions,
        ProjectCaseAssumptions,
        RevenueLine,
        ScenarioOverride,
    )

    base = payload["base_case"]

    def _sv(raw: Any) -> SourcedValue:
        return SourcedValue.from_any(raw)

    def _values(d: dict) -> dict[int, SourcedValue]:
        return {int(k): _sv(v) for k, v in d.items()}

    revenue_lines = [
        RevenueLine(
            name=line["name"],
            category=line.get("category", "primary"),
            base_values=_values(line["base_values"]),
            owner_share=_sv(line.get("owner_share", 1.0)),
            gross_margin=_sv(line["gross_margin"]) if line.get("gross_margin") is not None else None,
        )
        for line in base.get("revenue_lines", [])
    ]
    cost_lines = [
        CostLine(
            name=line["name"],
            category=line.get("category", "opex"),
            base_values=_values(line["base_values"]),
            is_capex=False,
        )
        for line in base.get("cost_lines", [])
    ]
    capex_lines = [
        CostLine(
            name=line["name"],
            category=line.get("category", "capex"),
            base_values=_values(line["base_values"]),
            is_capex=True,
        )
        for line in base.get("capex_lines", [])
    ]
    case = ProjectCaseAssumptions(
        project_name=base["project_name"],
        start_year=int(base["start_year"]),
        years=[int(y) for y in base["years"]],
        revenue_lines=revenue_lines,
        cost_lines=cost_lines,
        capex_lines=capex_lines,
        tax_rate=_sv(base.get("tax_rate", 0.25)),
        discount_rate=_sv(base.get("discount_rate", 0.12)),
        terminal_growth_rate=_sv(base["terminal_growth_rate"]) if base.get("terminal_growth_rate") is not None else None,
    )

    scenarios: dict[str, ScenarioOverride] = {}
    for name, raw in (payload.get("scenarios") or {}).items():
        scenarios[name] = ScenarioOverride(
            scenario=name,  # type: ignore[arg-type]
            scenario_probability=float(raw.get("scenario_probability", 0.0)),
            revenue_multiplier=raw.get("revenue_multiplier", {}),
            margin_delta=raw.get("margin_delta", {}),
            owner_share_delta=raw.get("owner_share_delta", {}),
            discount_rate_delta=float(raw.get("discount_rate_delta", 0.0)),
            capex_multiplier=raw.get("capex_multiplier", {}),
            activated_risks=raw.get("activated_risks", []),
        )

    return ProjectAssumptions(
        base_case=case,
        scenarios=scenarios,
        attribution_method=payload.get("attribution_method", "row_level_via_owner_share"),
    )


def _to_risks(raw_list: list[dict[str, Any]]) -> list[RiskExpectedLoss]:
    out: list[RiskExpectedLoss] = []
    for raw in raw_list:
        out.append(
            RiskExpectedLoss(
                risk_name=raw["risk_name"],
                category=raw.get("category", "strategic"),
                probability_by_scenario={k: float(v) for k, v in raw.get("probability_by_scenario", {}).items()},
                loss_by_scenario={
                    k: SourcedValue.from_any(v) for k, v in raw.get("loss_by_scenario", {}).items()
                },
                mitigation=raw.get("mitigation", ""),
            )
        )
    return out


def _to_partners(raw_list: list[dict[str, Any]]) -> list[PartnerShare]:
    return [
        PartnerShare(
            role=raw["role"],
            share_ratio=SourcedValue.from_any(raw.get("share_ratio", 0.0)),
            description=raw.get("description"),
        )
        for raw in raw_list
    ]


def generate_strategic_report(
    company_name: str,
    control_scores: dict[str, float] | None = None,
    project_strategic_weight: float = 0.5,
    project_revenue_share: float = 0.05,
    narrative_amplification: float = 1.5,
    output_path: Path | None = None,
) -> Path:
    """Skeleton 1: strategic depth, no project."""
    control = None
    if control_scores:
        control = evaluate_strategic_control(
            scores=control_scores,
            project_strategic_weight=project_strategic_weight,
            project_revenue_share=project_revenue_share,
            narrative_amplification=narrative_amplification,
        )
    content = render_company_only_skeleton(
        company_payload={"company_name": company_name},
        control=control,
        audit=None,
    )
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = output_path or REPORTS_DIR / f"{_safe(company_name)}_strategic_report.md"
    path.write_text(content, encoding="utf-8")
    return path


def generate_project_report(
    company_name: str,
    project_payload: dict[str, Any],
    risks_payload: list[dict[str, Any]] | None = None,
    partners_payload: list[dict[str, Any]] | None = None,
    control_scores: dict[str, float] | None = None,
    competitive_payload: dict[str, Any] | None = None,
    agent_scores: dict[str, float] | None = None,
    token_cost_score: float = 50.0,
    project_strategic_weight: float = 0.5,
    project_revenue_share: float = 0.05,
    narrative_amplification: float = 1.5,
    multiple: float = 10.0,
    enable_agent_section: bool = False,
    output_path: Path | None = None,
) -> Path:
    """Skeleton 2: company + project. enable_agent_section=True triggers
    the AgentHarness subsection (depth=agent)."""
    assumptions = _to_assumptions(project_payload)
    risks = _to_risks(risks_payload or [])
    risk_summary = evaluate_risks(risks, assumptions) if risks else {
        "risks": [],
        "total_expected_loss_base": 0.0,
        "total_expected_loss_by_scenario": {name: 0.0 for name in SCENARIO_NAMES},
    }
    cashflow = build_project_cashflow(
        assumptions,
        base_total_expected_loss=risk_summary["total_expected_loss_base"],
    )
    partners = _to_partners(partners_payload or [])
    attribution = evaluate_value_attribution(
        assumptions, cashflow, partner_shares=partners, multiple=multiple
    )
    control = None
    if control_scores:
        control = evaluate_strategic_control(
            scores=control_scores,
            project_strategic_weight=project_strategic_weight,
            project_revenue_share=project_revenue_share,
            narrative_amplification=narrative_amplification,
        )
    competitive = None
    if competitive_payload:
        competitive = score_competitors(
            target_company=competitive_payload["target_company"],
            target_scores=competitive_payload["target_scores"],
            competitor_scores=competitive_payload.get("competitor_scores", {}),
            industry=competitive_payload.get("industry", "default"),
        )
    agent_score = None
    if enable_agent_section and agent_scores:
        agent_score = evaluate_agent_harness(agent_scores, token_cost_score=token_cost_score)
    audit = build_assumption_audit(assumptions)

    content = render_company_plus_project_skeleton(
        company_name=company_name,
        project_name=assumptions.base_case.project_name,
        cashflow=cashflow,
        risks=risks,
        risk_summary=risk_summary,
        attribution=attribution,
        control=control,
        competitive=competitive,
        agent_score=agent_score,
        audit=audit,
    )
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = output_path or REPORTS_DIR / f"{_safe(company_name)}_{_safe(assumptions.base_case.project_name)}_v3_report.md"
    path.write_text(content, encoding="utf-8")
    return path


def _safe(name: str) -> str:
    return (
        "".join(c if c.isalnum() else "_" for c in name)
        .strip("_")
        .lower()
    )
