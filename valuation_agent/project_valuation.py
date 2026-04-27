from __future__ import annotations

from typing import Iterable

from .assumption_validator import (
    ScenarioProbabilityError,
    validate_project_assumptions,
)
from .schemas import (
    SCENARIO_NAMES,
    CashFlowResult,
    CostLine,
    ProjectAssumptions,
    ProjectCaseAssumptions,
    RevenueLine,
    ScenarioCashFlow,
    ScenarioOverride,
)


def calculate_irr(cashflows: list[float], guess: float = 0.1) -> float | None:
    """Bisection-based IRR. Returns None when no sign change is present
    (cash flows all-positive or all-negative) or when the search fails."""
    if not cashflows or all(cf == 0 for cf in cashflows):
        return None
    has_pos = any(cf > 0 for cf in cashflows)
    has_neg = any(cf < 0 for cf in cashflows)
    if not (has_pos and has_neg):
        return None

    def npv(rate: float) -> float:
        return sum(cf / ((1 + rate) ** t) for t, cf in enumerate(cashflows))

    low, high = -0.99, 10.0
    f_low, f_high = npv(low), npv(high)
    if f_low * f_high > 0:
        return None
    for _ in range(200):
        mid = (low + high) / 2
        f_mid = npv(mid)
        if abs(f_mid) < 1e-6:
            return mid
        if f_low * f_mid < 0:
            high = mid
            f_high = f_mid
        else:
            low = mid
            f_low = f_mid
    return (low + high) / 2


def calculate_moic(cashflows: list[float]) -> float | None:
    invested = sum(-cf for cf in cashflows if cf < 0)
    returned = sum(cf for cf in cashflows if cf > 0)
    if invested <= 0:
        return None
    return returned / invested


def calculate_payback(cashflows: list[float]) -> float | None:
    """Returns the (fractional) period index when cumulative cash flow
    first turns non-negative. None if it never does."""
    cumulative = 0.0
    prev_cumulative = 0.0
    for t, cf in enumerate(cashflows):
        prev_cumulative = cumulative
        cumulative += cf
        if cumulative >= 0 and prev_cumulative < 0 and cf != 0:
            fraction = -prev_cumulative / cf
            return t - 1 + fraction
        if cumulative >= 0 and prev_cumulative >= 0 and t == 0:
            return 0.0
    return None


def calculate_npv(cashflows: list[float], discount_rate: float) -> float:
    return sum(cf / ((1 + discount_rate) ** t) for t, cf in enumerate(cashflows))


def _apply_overrides(
    base: ProjectCaseAssumptions,
    override: ScenarioOverride | None,
) -> tuple[
    list[RevenueLine],
    list[CostLine],
    list[CostLine],
    float,
]:
    """Return scenario-adjusted (revenue_lines, cost_lines, capex_lines,
    discount_rate). Adjustments are non-destructive copies."""
    discount_rate = base.discount_rate.value
    if override:
        discount_rate = max(0.001, discount_rate + override.discount_rate_delta)

    rev_mult = override.revenue_multiplier if override else {}
    margin_delta = override.margin_delta if override else {}
    owner_delta = override.owner_share_delta if override else {}

    adj_revenue: list[RevenueLine] = []
    for line in base.revenue_lines:
        mult = rev_mult.get(line.name, 1.0)
        adj_values = {
            year: type(sv)(  # SourcedValue copy with adjusted value
                value=sv.value * mult,
                source=sv.source,
                source_detail=sv.source_detail,
                confidence=sv.confidence,
            )
            for year, sv in line.base_values.items()
        }
        new_owner = max(0.0, min(1.0, line.owner_share.value + owner_delta.get(line.name, 0.0)))
        new_owner_sv = type(line.owner_share)(
            value=new_owner,
            source=line.owner_share.source,
            source_detail=line.owner_share.source_detail,
            confidence=line.owner_share.confidence,
        )
        new_gm = line.gross_margin
        if line.gross_margin and line.name in margin_delta:
            new_gm_value = max(-1.0, min(1.0, line.gross_margin.value + margin_delta[line.name]))
            new_gm = type(line.gross_margin)(
                value=new_gm_value,
                source=line.gross_margin.source,
                source_detail=line.gross_margin.source_detail,
                confidence=line.gross_margin.confidence,
            )
        adj_revenue.append(
            RevenueLine(
                name=line.name,
                category=line.category,
                base_values=adj_values,
                owner_share=new_owner_sv,
                gross_margin=new_gm,
            )
        )

    adj_cost = list(base.cost_lines)

    capex_mult = override.capex_multiplier if override else {}
    adj_capex: list[CostLine] = []
    for line in base.capex_lines:
        mult = capex_mult.get(line.name, 1.0)
        adj_values = {
            year: type(sv)(
                value=sv.value * mult,
                source=sv.source,
                source_detail=sv.source_detail,
                confidence=sv.confidence,
            )
            for year, sv in line.base_values.items()
        }
        adj_capex.append(
            CostLine(
                name=line.name,
                category=line.category,
                base_values=adj_values,
                is_capex=True,
            )
        )

    return adj_revenue, adj_cost, adj_capex, discount_rate


def _scenario_cashflow(
    base: ProjectCaseAssumptions,
    scenario_name: str,
    probability: float,
    override: ScenarioOverride | None,
) -> ScenarioCashFlow:
    revenue_lines, cost_lines, capex_lines, discount_rate = _apply_overrides(base, override)
    years = base.years
    annual_revenue: dict[int, float] = {}
    annual_cost: dict[int, float] = {}
    annual_ebit: dict[int, float] = {}
    annual_tax: dict[int, float] = {}
    annual_fcf: dict[int, float] = {}
    cumulative: dict[int, float] = {}

    tax_rate = base.tax_rate.value
    running = 0.0
    for year in years:
        # Revenue attributable to the listed company via row-level owner_share.
        rev_total = 0.0
        cogs_total = 0.0
        for line in revenue_lines:
            line_rev = line.base_values.get(year)
            if line_rev is None:
                continue
            owned = line_rev.value * line.owner_share.value
            rev_total += owned
            if line.gross_margin is not None:
                cogs_total += owned * (1.0 - line.gross_margin.value)

        opex_total = sum(
            line.base_values[year].value
            for line in cost_lines
            if year in line.base_values
        )
        capex_total = sum(
            line.base_values[year].value
            for line in capex_lines
            if year in line.base_values
        )

        ebit = rev_total - cogs_total - opex_total
        tax = max(0.0, ebit * tax_rate)
        fcf = ebit - tax - capex_total

        annual_revenue[year] = rev_total
        annual_cost[year] = cogs_total + opex_total + capex_total
        annual_ebit[year] = ebit
        annual_tax[year] = tax
        annual_fcf[year] = fcf
        running += fcf
        cumulative[year] = running

    cashflow_series = [annual_fcf[y] for y in years]
    npv = calculate_npv(cashflow_series, discount_rate)
    irr = calculate_irr(cashflow_series)
    moic = calculate_moic(cashflow_series)
    payback = calculate_payback(cashflow_series)

    return ScenarioCashFlow(
        scenario=scenario_name,  # type: ignore[arg-type]
        scenario_probability=probability,
        annual_revenue=annual_revenue,
        annual_cost=annual_cost,
        annual_ebit=annual_ebit,
        annual_tax=annual_tax,
        annual_fcf=annual_fcf,
        cumulative_fcf=cumulative,
        discount_rate=discount_rate,
        npv=npv,
        irr=irr,
        moic=moic,
        payback_year=payback,
    )


def build_project_cashflow(
    assumptions: ProjectAssumptions,
    base_total_expected_loss: float = 0.0,
    skip_validation: bool = False,
) -> CashFlowResult:
    if not skip_validation:
        validate_project_assumptions(assumptions)

    base = assumptions.base_case
    by_scenario: dict[str, ScenarioCashFlow] = {}

    if assumptions.scenarios:
        for name in SCENARIO_NAMES:
            override = assumptions.scenarios[name]
            by_scenario[name] = _scenario_cashflow(
                base, name, override.scenario_probability, override
            )
    else:
        # Single base-case run; assign probability 1.0.
        by_scenario["base"] = _scenario_cashflow(base, "base", 1.0, None)

    pw_npv = sum(sc.npv * sc.scenario_probability for sc in by_scenario.values())
    base_npv = by_scenario["base"].npv if "base" in by_scenario else pw_npv
    risk_adjusted_base = base_npv - base_total_expected_loss

    return CashFlowResult(
        by_scenario=by_scenario,
        probability_weighted_npv=pw_npv,
        risk_adjusted_base_npv=risk_adjusted_base,
    )


def calculate_project_value(result: CashFlowResult) -> dict[str, float]:
    """Convenience summary used by the report renderer."""
    return {
        "probability_weighted_npv": result.probability_weighted_npv,
        "risk_adjusted_base_npv": result.risk_adjusted_base_npv,
        "base_npv": result.by_scenario.get(
            "base",
            next(iter(result.by_scenario.values())),
        ).npv,
    }
