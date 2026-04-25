from __future__ import annotations

from .schemas import FinancialStatement, NormalizedFinancials, ValuationResult


UNIT_MULTIPLIERS = {
    "yuan": 1,
    "cny": 1,
    "hkd": 1,
    "thousand": 1_000,
    "million": 1_000_000,
    "billion": 1_000_000_000,
    "wan": 10_000,
    "yi": 100_000_000,
}


def market_cap_to_price(target_market_cap: float, shares_outstanding: float) -> float:
    if shares_outstanding is None or shares_outstanding <= 0:
        raise ValueError("shares_outstanding must be positive")
    if target_market_cap is None or target_market_cap < 0:
        raise ValueError("target_market_cap must be non-negative")
    return target_market_cap / shares_outstanding


def implied_pe(market_cap: float, net_profit: float | None) -> float | None:
    if net_profit is None or net_profit <= 0:
        return None
    return market_cap / net_profit


def implied_ps(market_cap: float, revenue: float | None) -> float | None:
    if revenue is None or revenue <= 0:
        return None
    return market_cap / revenue


def required_net_profit(target_market_cap: float, target_pe: float) -> float:
    if target_pe <= 0:
        raise ValueError("target_pe must be positive")
    return target_market_cap / target_pe


def convert_currency(value: float | None, source: str, target: str, fx_rates: dict[str, float]) -> float | None:
    if value is None:
        return None
    if source == target:
        return value
    pair = f"{source}{target}"
    if pair not in fx_rates:
        raise KeyError(f"missing fx rate: {pair}")
    return value * fx_rates[pair]


def normalize_financials(statement: FinancialStatement, target_currency: str, fx_rates: dict[str, float]) -> NormalizedFinancials:
    unit_multiplier = UNIT_MULTIPLIERS.get(statement.unit)
    if unit_multiplier is None:
        raise KeyError(f"unsupported unit: {statement.unit}")

    warnings: list[str] = []

    def norm(value: float | None) -> float | None:
        scaled = None if value is None else value * unit_multiplier
        return convert_currency(scaled, statement.currency, target_currency, fx_rates)

    if statement.net_profit is not None and statement.net_profit <= 0:
        warnings.append("net_profit is non-positive; PE will be unavailable")

    return NormalizedFinancials(
        period=statement.period,
        currency=target_currency,
        revenue=norm(statement.revenue),
        net_profit=norm(statement.net_profit),
        adjusted_net_profit=norm(statement.adjusted_net_profit),
        ebitda=norm(statement.ebitda),
        operating_cash_flow=norm(statement.operating_cash_flow),
        cash=norm(statement.cash),
        debt=norm(statement.debt),
        source_url=statement.source_url,
        warnings=warnings,
    )


def calculate_valuation(
    target_market_cap: float,
    currency: str,
    shares_outstanding: float,
    revenue: float | None,
    net_profit: float | None,
    pe_targets: tuple[int, ...] = (15, 20, 25),
) -> ValuationResult:
    target_share_price = market_cap_to_price(target_market_cap, shares_outstanding)
    pe = implied_pe(target_market_cap, net_profit)
    ps = implied_ps(target_market_cap, revenue)
    warnings: list[str] = []

    if pe is None:
        warnings.append("PE unavailable because net_profit is missing or non-positive")
    if ps is None:
        warnings.append("PS unavailable because revenue is missing or non-positive")

    required = {f"{pe_target}x": required_net_profit(target_market_cap, pe_target) for pe_target in pe_targets}

    return ValuationResult(
        target_market_cap=target_market_cap,
        currency=currency,
        shares_outstanding=shares_outstanding,
        target_share_price=target_share_price,
        implied_pe=pe,
        implied_ps=ps,
        required_net_profit_at_pe=required,
        warnings=warnings,
    )


def scenario_analysis(
    base_revenue: float,
    shares_outstanding: float,
    scenarios: dict,
    currency: str,
) -> list[dict]:
    if base_revenue is None or base_revenue < 0:
        raise ValueError("base_revenue must be non-negative")

    results = []
    for key, item in scenarios.items():
        forecast_revenue = base_revenue * (1 + item["revenue_growth"])
        forecast_net_profit = forecast_revenue * item["net_margin"]
        market_cap_pe = forecast_net_profit * item["pe"]
        market_cap_ps = forecast_revenue * item["ps"]
        blended_market_cap = (market_cap_pe + market_cap_ps) / 2
        results.append(
            {
                "key": key,
                "label": item.get("label", key),
                "currency": currency,
                "forecast_revenue": forecast_revenue,
                "forecast_net_profit": forecast_net_profit,
                "market_cap_pe": market_cap_pe,
                "market_cap_ps": market_cap_ps,
                "blended_market_cap": blended_market_cap,
                "target_share_price": market_cap_to_price(blended_market_cap, shares_outstanding),
                "assumptions": {
                    "revenue_growth": item["revenue_growth"],
                    "net_margin": item["net_margin"],
                    "pe": item["pe"],
                    "ps": item["ps"],
                },
            }
        )
    return results
