from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


SourceLevel = Literal[
    "user_explicit",
    "disclosed",
    "template",
    "analogy",
    "derived",
    "fabricated",
]

ScenarioName = Literal[
    "very_bear",
    "bear",
    "base",
    "bull",
    "very_bull",
]

SCENARIO_NAMES: tuple[str, ...] = (
    "very_bear",
    "bear",
    "base",
    "bull",
    "very_bull",
)

DEFAULT_SOURCE_CONFIDENCE: dict[str, float] = {
    "user_explicit": 0.9,
    "disclosed": 0.85,
    "template": 0.5,
    "analogy": 0.4,
    "derived": 0.4,
    "fabricated": 0.0,
}


@dataclass(frozen=True)
class CompanyProfile:
    company_id: str
    company_name: str
    ticker: str
    exchange: str
    currency: str
    reporting_currency: str
    industry: list[str] = field(default_factory=list)
    default_target_market_cap: float | None = None


@dataclass(frozen=True)
class MarketSnapshot:
    ticker: str
    trade_date: str
    currency: str
    share_price: float | None
    market_cap: float | None
    shares_outstanding: float | None
    volume: float | None = None
    source_url: str = ""


@dataclass(frozen=True)
class FinancialStatement:
    period: str
    currency: str
    unit: str
    revenue: float | None
    gross_profit: float | None
    operating_profit: float | None
    net_profit: float | None
    adjusted_net_profit: float | None
    ebitda: float | None
    operating_cash_flow: float | None
    cash: float | None
    debt: float | None
    source_url: str = ""


@dataclass(frozen=True)
class NormalizedFinancials:
    period: str
    currency: str
    revenue: float | None
    net_profit: float | None
    adjusted_net_profit: float | None
    ebitda: float | None
    operating_cash_flow: float | None
    cash: float | None
    debt: float | None
    source_url: str = ""
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ValuationResult:
    target_market_cap: float
    currency: str
    shares_outstanding: float
    target_share_price: float
    implied_pe: float | None
    implied_ps: float | None
    required_net_profit_at_pe: dict[str, float]
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_market_cap": self.target_market_cap,
            "currency": self.currency,
            "shares_outstanding": self.shares_outstanding,
            "target_share_price": self.target_share_price,
            "implied_pe": self.implied_pe,
            "implied_ps": self.implied_ps,
            "required_net_profit_at_pe": self.required_net_profit_at_pe,
            "warnings": self.warnings,
        }


# ============================================================================
# V3 schemas: project-level cash flow, scenarios, control points, risks,
# value attribution, agent/harness valuation.
# Every numeric input must be wrapped in SourcedValue (see V3_DESIGN_AND_DEV_PLAN
# section 3.8 — "fabricated" is rejected by the validator).
# ============================================================================


@dataclass
class SourcedValue:
    value: float
    source: SourceLevel = "user_explicit"
    source_detail: str | None = None
    confidence: float | None = None

    def __post_init__(self) -> None:
        if self.confidence is None:
            self.confidence = DEFAULT_SOURCE_CONFIDENCE.get(self.source, 0.0)

    def to_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "source": self.source,
            "source_detail": self.source_detail,
            "confidence": self.confidence,
        }

    @classmethod
    def from_any(cls, raw: Any) -> "SourcedValue":
        if isinstance(raw, SourcedValue):
            return raw
        if isinstance(raw, dict):
            return cls(
                value=float(raw.get("value", 0.0)),
                source=raw.get("source", "user_explicit"),
                source_detail=raw.get("source_detail"),
                confidence=raw.get("confidence"),
            )
        return cls(value=float(raw))


@dataclass
class RevenueLine:
    name: str
    category: str
    base_values: dict[int, SourcedValue]
    owner_share: SourcedValue
    gross_margin: SourcedValue | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "base_values": {str(k): v.to_dict() for k, v in self.base_values.items()},
            "owner_share": self.owner_share.to_dict(),
            "gross_margin": self.gross_margin.to_dict() if self.gross_margin else None,
        }


@dataclass
class CostLine:
    name: str
    category: str
    base_values: dict[int, SourcedValue]
    is_capex: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "base_values": {str(k): v.to_dict() for k, v in self.base_values.items()},
            "is_capex": self.is_capex,
        }


@dataclass
class ScenarioOverride:
    scenario: ScenarioName
    scenario_probability: float
    revenue_multiplier: dict[str, float] = field(default_factory=dict)
    margin_delta: dict[str, float] = field(default_factory=dict)
    owner_share_delta: dict[str, float] = field(default_factory=dict)
    discount_rate_delta: float = 0.0
    capex_multiplier: dict[str, float] = field(default_factory=dict)
    activated_risks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario": self.scenario,
            "scenario_probability": self.scenario_probability,
            "revenue_multiplier": self.revenue_multiplier,
            "margin_delta": self.margin_delta,
            "owner_share_delta": self.owner_share_delta,
            "discount_rate_delta": self.discount_rate_delta,
            "capex_multiplier": self.capex_multiplier,
            "activated_risks": self.activated_risks,
        }


@dataclass
class ProjectCaseAssumptions:
    project_name: str
    start_year: int
    years: list[int]
    revenue_lines: list[RevenueLine]
    cost_lines: list[CostLine] = field(default_factory=list)
    capex_lines: list[CostLine] = field(default_factory=list)
    tax_rate: SourcedValue = field(default_factory=lambda: SourcedValue(0.25, "template"))
    discount_rate: SourcedValue = field(default_factory=lambda: SourcedValue(0.12, "template"))
    terminal_growth_rate: SourcedValue | None = None


@dataclass
class ProjectAssumptions:
    base_case: ProjectCaseAssumptions
    scenarios: dict[str, ScenarioOverride] = field(default_factory=dict)
    attribution_method: Literal[
        "row_level_via_owner_share",
        "project_level_via_value_attribution",
    ] = "row_level_via_owner_share"


@dataclass
class ScenarioCashFlow:
    scenario: ScenarioName
    scenario_probability: float
    annual_revenue: dict[int, float]
    annual_cost: dict[int, float]
    annual_ebit: dict[int, float]
    annual_tax: dict[int, float]
    annual_fcf: dict[int, float]
    cumulative_fcf: dict[int, float]
    discount_rate: float
    npv: float
    irr: float | None
    moic: float | None
    payback_year: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario": self.scenario,
            "scenario_probability": self.scenario_probability,
            "annual_revenue": self.annual_revenue,
            "annual_cost": self.annual_cost,
            "annual_ebit": self.annual_ebit,
            "annual_tax": self.annual_tax,
            "annual_fcf": self.annual_fcf,
            "cumulative_fcf": self.cumulative_fcf,
            "discount_rate": self.discount_rate,
            "npv": self.npv,
            "irr": self.irr,
            "moic": self.moic,
            "payback_year": self.payback_year,
        }


@dataclass
class CashFlowResult:
    by_scenario: dict[str, ScenarioCashFlow]
    probability_weighted_npv: float
    risk_adjusted_base_npv: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "by_scenario": {k: v.to_dict() for k, v in self.by_scenario.items()},
            "probability_weighted_npv": self.probability_weighted_npv,
            "risk_adjusted_base_npv": self.risk_adjusted_base_npv,
        }


@dataclass
class ControlDimension:
    name: str
    score: float
    weight: float
    evidence: list[str] = field(default_factory=list)


@dataclass
class StrategicControlScore:
    dimensions: list[ControlDimension]
    weighted_score: float
    project_strategic_weight: float
    project_revenue_share: float
    narrative_amplification: float
    valuation_premium: float
    explanation: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimensions": [
                {
                    "name": d.name,
                    "score": d.score,
                    "weight": d.weight,
                    "evidence": d.evidence,
                }
                for d in self.dimensions
            ],
            "weighted_score": self.weighted_score,
            "project_strategic_weight": self.project_strategic_weight,
            "project_revenue_share": self.project_revenue_share,
            "narrative_amplification": self.narrative_amplification,
            "valuation_premium": self.valuation_premium,
            "explanation": self.explanation,
        }


@dataclass
class CompetitorScorecard:
    company: str
    dimensions: list[ControlDimension]
    weighted_score: float


@dataclass
class CompetitiveScoreResult:
    target_company: str
    target_scorecard: CompetitorScorecard
    competitor_scorecards: list[CompetitorScorecard]
    rankings: list[str]
    target_strengths: list[str]
    target_weaknesses: list[str]
    multiple_premium_suggestion: float
    explanation: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        def _scorecard_to_dict(sc: CompetitorScorecard) -> dict[str, Any]:
            return {
                "company": sc.company,
                "dimensions": [
                    {"name": d.name, "score": d.score, "weight": d.weight}
                    for d in sc.dimensions
                ],
                "weighted_score": sc.weighted_score,
            }

        return {
            "target_company": self.target_company,
            "target_scorecard": _scorecard_to_dict(self.target_scorecard),
            "competitor_scorecards": [_scorecard_to_dict(c) for c in self.competitor_scorecards],
            "rankings": self.rankings,
            "target_strengths": self.target_strengths,
            "target_weaknesses": self.target_weaknesses,
            "multiple_premium_suggestion": self.multiple_premium_suggestion,
            "explanation": self.explanation,
        }


RiskCategory = Literal[
    "strategic",
    "organizational",
    "competitive",
    "financial",
    "compliance",
    "technical",
]


@dataclass
class RiskExpectedLoss:
    risk_name: str
    category: RiskCategory
    probability_by_scenario: dict[str, float]
    loss_by_scenario: dict[str, SourcedValue]
    expected_loss_by_scenario: dict[str, float] = field(default_factory=dict)
    mitigation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "risk_name": self.risk_name,
            "category": self.category,
            "probability_by_scenario": self.probability_by_scenario,
            "loss_by_scenario": {k: v.to_dict() for k, v in self.loss_by_scenario.items()},
            "expected_loss_by_scenario": self.expected_loss_by_scenario,
            "mitigation": self.mitigation,
        }


PartnerRole = Literal[
    "listed_company",
    "model_vendor",
    "channel_partner",
    "client",
    "ecosystem_partner",
]


@dataclass
class PartnerShare:
    role: PartnerRole
    share_ratio: SourcedValue
    description: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "share_ratio": self.share_ratio.to_dict(),
            "description": self.description,
        }


@dataclass
class ValueAttribution:
    total_project_revenue: dict[int, float]
    target_company_revenue: dict[int, float]
    target_company_profit: dict[int, float]
    target_company_npv_contribution: float
    target_company_market_cap_uplift: float
    attribution_ratio: float
    partner_shares: list[PartnerShare] = field(default_factory=list)
    method: Literal[
        "row_level_via_owner_share",
        "project_level_via_value_attribution",
    ] = "row_level_via_owner_share"

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_project_revenue": self.total_project_revenue,
            "target_company_revenue": self.target_company_revenue,
            "target_company_profit": self.target_company_profit,
            "target_company_npv_contribution": self.target_company_npv_contribution,
            "target_company_market_cap_uplift": self.target_company_market_cap_uplift,
            "attribution_ratio": self.attribution_ratio,
            "partner_shares": [p.to_dict() for p in self.partner_shares],
            "method": self.method,
        }


@dataclass
class AgentHarnessScore:
    model_intelligence: float
    harness_quality: float
    skill_surface: float
    identity_security_control: float
    workflow_ownership: float
    outcome_pricing_ability: float
    weights: dict[str, float]
    agent_value_score: float
    token_cost_efficiency: float
    token_efficiency_modifier: float
    final_agent_score: float
    valuation_premium_band: Literal["discount", "neutral", "premium", "platform_premium"]
    explanation: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_intelligence": self.model_intelligence,
            "harness_quality": self.harness_quality,
            "skill_surface": self.skill_surface,
            "identity_security_control": self.identity_security_control,
            "workflow_ownership": self.workflow_ownership,
            "outcome_pricing_ability": self.outcome_pricing_ability,
            "weights": self.weights,
            "agent_value_score": self.agent_value_score,
            "token_cost_efficiency": self.token_cost_efficiency,
            "token_efficiency_modifier": self.token_efficiency_modifier,
            "final_agent_score": self.final_agent_score,
            "valuation_premium_band": self.valuation_premium_band,
            "explanation": self.explanation,
        }


@dataclass
class AssumptionAuditEntry:
    field_path: str
    value: float
    source: SourceLevel
    source_detail: str | None
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "field_path": self.field_path,
            "value": self.value,
            "source": self.source,
            "source_detail": self.source_detail,
            "confidence": self.confidence,
        }


@dataclass
class AssumptionAudit:
    entries: list[AssumptionAuditEntry]
    high_confidence_share: float
    has_fabricated: bool
    warning_label: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "entries": [e.to_dict() for e in self.entries],
            "high_confidence_share": self.high_confidence_share,
            "has_fabricated": self.has_fabricated,
            "warning_label": self.warning_label,
        }
