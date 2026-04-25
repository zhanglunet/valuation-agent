from __future__ import annotations

from .calculators import calculate_valuation, normalize_financials, scenario_analysis
from .public_data import enrich_payload_from_public_data
from .schemas import CompanyProfile, FinancialStatement, MarketSnapshot
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


def run_payload_analysis(payload: dict) -> dict:
    """Analyze any listed company from explicit user-provided market and financial inputs."""
    payload = enrich_payload_from_public_data(payload)
    assumptions = load_assumptions()
    ticker = payload["ticker"]
    currency = payload.get("currency", "HKD")
    financial_currency = payload.get("financial_currency") or payload.get("reporting_currency") or currency
    company = CompanyProfile(
        company_id=payload.get("company_id") or ticker.lower().replace(".", "_").replace("-", "_"),
        company_name=payload.get("company_name") or ticker,
        ticker=ticker,
        exchange=payload.get("exchange", ""),
        currency=currency,
        reporting_currency=financial_currency,
        industry=payload.get("industry", []),
        default_target_market_cap=payload.get("target_market_cap"),
    )

    shares_outstanding = payload["shares_outstanding"]
    share_price = payload.get("share_price")
    market_cap = payload.get("market_cap")
    if market_cap is None and share_price is not None:
        market_cap = share_price * shares_outstanding

    market = MarketSnapshot(
        ticker=ticker,
        trade_date=payload.get("trade_date", "user_input"),
        currency=currency,
        share_price=share_price,
        market_cap=market_cap,
        shares_outstanding=shares_outstanding,
        volume=payload.get("volume"),
        source_url=payload.get("market_source_url", "user_input"),
    )
    statement = FinancialStatement(
        period=payload.get("period", "user_input"),
        currency=financial_currency,
        unit=payload.get("unit", "yuan"),
        revenue=payload.get("revenue"),
        gross_profit=payload.get("gross_profit"),
        operating_profit=payload.get("operating_profit"),
        net_profit=payload.get("net_profit"),
        adjusted_net_profit=payload.get("adjusted_net_profit"),
        ebitda=payload.get("ebitda"),
        operating_cash_flow=payload.get("operating_cash_flow"),
        cash=payload.get("cash"),
        debt=payload.get("debt"),
        source_url=payload.get("financial_source_url", "user_input"),
    )

    target = payload.get("target_market_cap") or market.market_cap
    if target is None:
        raise ValueError("target_market_cap is required when public market cap is unavailable")
    normalized = normalize_financials(statement, target_currency=currency, fx_rates=assumptions["fx_rates"])
    valuation = calculate_valuation(
        target_market_cap=target,
        currency=currency,
        shares_outstanding=shares_outstanding,
        revenue=normalized.revenue,
        net_profit=normalized.adjusted_net_profit or normalized.net_profit,
    )
    scenarios = scenario_analysis(
        base_revenue=normalized.revenue,
        shares_outstanding=shares_outstanding,
        scenarios=payload.get("scenarios") or assumptions["scenario_defaults"],
        currency=currency,
    )

    return {
        "company": company,
        "market": market,
        "financial_statement": statement,
        "normalized_financials": normalized,
        "valuation": valuation,
        "scenarios": scenarios,
    }
