from __future__ import annotations

from .assumption_validator import (
    DoubleAttributionError,
    validate_attribution_against_assumptions,
)
from .schemas import (
    CashFlowResult,
    PartnerShare,
    ProjectAssumptions,
    ValueAttribution,
)


def validate_attribution_method(assumptions: ProjectAssumptions) -> None:
    """Surface the same constraint as assumption_validator but as a public
    entry-point used by reporting and CLI before any calculation runs."""
    if assumptions.attribution_method not in (
        "row_level_via_owner_share",
        "project_level_via_value_attribution",
    ):
        raise DoubleAttributionError(
            f"unknown attribution_method: {assumptions.attribution_method}"
        )


def calculate_partner_split(
    revenue_pool: dict[int, float],
    partner_shares: list[PartnerShare],
) -> dict[str, dict[int, float]]:
    """Given a year-indexed total revenue pool and the configured partner
    shares, return per-role year-indexed revenue. Shares need not sum to 1.0
    (a warning is the caller's responsibility)."""
    out: dict[str, dict[int, float]] = {}
    for partner in partner_shares:
        ratio = float(partner.share_ratio.value)
        out[partner.role] = {y: v * ratio for y, v in revenue_pool.items()}
    return out


def _row_level_attribution(
    cashflow: CashFlowResult,
) -> tuple[dict[int, float], dict[int, float], dict[int, float], float]:
    """When using row-level owner_share, the project_valuation module has
    already stripped non-target revenue, so 'project_revenue' equals the
    target company's revenue. NPV stays as-is."""
    base = cashflow.by_scenario.get(
        "base", next(iter(cashflow.by_scenario.values()))
    )
    revenue = dict(base.annual_revenue)
    profit = dict(base.annual_ebit)
    npv = base.npv
    return revenue, revenue, profit, npv


def _project_level_attribution(
    cashflow: CashFlowResult,
    partner_shares: list[PartnerShare],
) -> tuple[dict[int, float], dict[int, float], dict[int, float], float]:
    base = cashflow.by_scenario.get(
        "base", next(iter(cashflow.by_scenario.values()))
    )
    total_revenue = dict(base.annual_revenue)
    listed_share = next(
        (p.share_ratio.value for p in partner_shares if p.role == "listed_company"),
        1.0,
    )
    target_revenue = {y: v * listed_share for y, v in total_revenue.items()}
    target_profit = {y: v * listed_share for y, v in base.annual_ebit.items()}
    npv = base.npv * listed_share
    return total_revenue, target_revenue, target_profit, npv


def calculate_market_cap_uplift(
    npv_contribution: float,
    multiple: float,
) -> float:
    """Convert the NPV that accrues to the listed company into a market-cap
    uplift via a chosen valuation multiple (PE-equivalent or PS-equivalent
    depending on context)."""
    return npv_contribution * multiple


def evaluate_value_attribution(
    assumptions: ProjectAssumptions,
    cashflow: CashFlowResult,
    partner_shares: list[PartnerShare] | None = None,
    multiple: float = 1.0,
) -> ValueAttribution:
    validate_attribution_method(assumptions)
    method = assumptions.attribution_method
    partners = partner_shares or []

    if method == "row_level_via_owner_share":
        total_rev, target_rev, target_profit, npv = _row_level_attribution(cashflow)
    else:
        total_rev, target_rev, target_profit, npv = _project_level_attribution(
            cashflow, partners
        )

    pool_total = sum(total_rev.values()) or 1.0
    target_total = sum(target_rev.values())
    attribution_ratio = target_total / pool_total
    uplift = calculate_market_cap_uplift(npv, multiple)

    return ValueAttribution(
        total_project_revenue=total_rev,
        target_company_revenue=target_rev,
        target_company_profit=target_profit,
        target_company_npv_contribution=npv,
        target_company_market_cap_uplift=uplift,
        attribution_ratio=attribution_ratio,
        partner_shares=partners,
        method=method,
    )
