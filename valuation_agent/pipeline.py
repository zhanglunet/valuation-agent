from __future__ import annotations

from .calculators import calculate_valuation, normalize_financials, scenario_analysis
from .storage import load_assumptions, load_company, load_financial_statement, load_market_snapshot


def run_company_analysis(company_id: str, target_market_cap: float | None = None) -> dict:
    company = load_company(company_id)
    assumptions = load_assumptions()
    market = load_market_snapshot(company_id)
    statement = load_financial_statement(company_id)
    target = target_market_cap or company.default_target_market_cap
    if target is None:
        raise ValueError("target_market_cap is required")

    normalized = normalize_financials(
        statement,
        target_currency=company.currency,
        fx_rates=assumptions["fx_rates"],
    )
    valuation = calculate_valuation(
        target_market_cap=target,
        currency=company.currency,
        shares_outstanding=market.shares_outstanding,
        revenue=normalized.revenue,
        net_profit=normalized.adjusted_net_profit or normalized.net_profit,
    )
    scenarios = scenario_analysis(
        base_revenue=normalized.revenue,
        shares_outstanding=market.shares_outstanding,
        scenarios=assumptions["scenario_defaults"],
        currency=company.currency,
    )

    return {
        "company": company,
        "market": market,
        "financial_statement": statement,
        "normalized_financials": normalized,
        "valuation": valuation,
        "scenarios": scenarios,
    }
