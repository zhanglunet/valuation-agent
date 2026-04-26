from __future__ import annotations

import json
import time
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from .cache import read_cache, write_cache
from .paths import CONFIG_DIR


YAHOO_SEARCH_URL = "https://query1.finance.yahoo.com/v1/finance/search"
YAHOO_QUOTE_URL = "https://query1.finance.yahoo.com/v7/finance/quote"
YAHOO_SUMMARY_URL = "https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}"
YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
YAHOO_TIMESERIES_URL = "https://query1.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/{symbol}"


class PublicDataError(RuntimeError):
    pass


def _cache_namespace_for_url(url: str) -> str:
    if "/v1/finance/search" in url:
        return "search"
    if "/v8/finance/chart" in url:
        return "chart"
    if "/fundamentals-timeseries/" in url:
        return "financials"
    return "http"


def _get_json(url: str, timeout: int = 15, refresh: bool = False) -> dict:
    namespace = _cache_namespace_for_url(url)
    if not refresh:
        cached = read_cache(namespace, url)
        if cached is not None:
            return cached
    request = Request(
        url,
        headers={
            "User-Agent": "valuation-agent/1.0 (+https://github.com/zhanglunet/valuation-agent)",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
            write_cache(namespace, url, data)
            return data
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise PublicDataError(f"public data request failed: {url}") from exc


def _raw_value(value):
    if isinstance(value, dict) and "raw" in value:
        return value["raw"]
    return value


def _first_number(*values):
    for value in values:
        value = _raw_value(value)
        if isinstance(value, (int, float)):
            return value
    return None


def resolve_candidates(query: str, refresh: bool = False) -> list[dict]:
    url = f"{YAHOO_SEARCH_URL}?{urlencode({'q': query, 'quotesCount': 8, 'newsCount': 0})}"
    data = _get_json(url, refresh=refresh)
    quotes = data.get("quotes", [])
    return [item for item in quotes if item.get("quoteType") in {"EQUITY", "ETF"} and item.get("symbol")]


def resolve_symbol(query: str, refresh: bool = False) -> dict:
    if not query:
        raise ValueError("company name or ticker is required")

    alias_symbol = resolve_alias(query)
    if alias_symbol:
        return {
            "symbol": alias_symbol,
            "company_name": query,
            "exchange": "",
            "quote_type": "EQUITY",
            "source_url": str(CONFIG_DIR / "company_aliases.json"),
        }

    url = f"{YAHOO_SEARCH_URL}?{urlencode({'q': query, 'quotesCount': 8, 'newsCount': 0})}"
    equities = resolve_candidates(query, refresh=refresh)
    if not equities:
        raise PublicDataError(f"no listed company found for query: {query}")

    best = equities[0]
    return {
        "symbol": best["symbol"],
        "company_name": best.get("longname") or best.get("shortname") or query,
        "exchange": best.get("exchDisp") or best.get("exchange", ""),
        "quote_type": best.get("quoteType", ""),
        "sector": best.get("sectorDisp") or best.get("sector"),
        "industry": best.get("industryDisp") or best.get("industry"),
        "source_url": url,
    }


def resolve_alias(query: str) -> str | None:
    path = CONFIG_DIR / "company_aliases.json"
    if not Path(path).exists():
        return None
    try:
        aliases = json.loads(path.read_text(encoding="utf-8")).get("aliases", {})
    except json.JSONDecodeError:
        return None
    normalized = query.strip().lower()
    return aliases.get(normalized) or aliases.get(query.strip())


def fetch_quote(symbol: str, refresh: bool = False) -> dict:
    url = f"{YAHOO_CHART_URL.format(symbol=quote(symbol))}?{urlencode({'range': '1d', 'interval': '1d'})}"
    data = _get_json(url, refresh=refresh)
    results = data.get("chart", {}).get("result", [])
    if not results:
        raise PublicDataError(f"quote not found for symbol: {symbol}")
    item = results[0].get("meta", {})
    return {
        "ticker": item.get("symbol", symbol),
        "company_name": item.get("longName") or item.get("shortName") or symbol,
        "exchange": item.get("fullExchangeName") or item.get("exchangeName", ""),
        "currency": item.get("currency") or "USD",
        "share_price": item.get("regularMarketPrice"),
        "market_cap": None,
        "shares_outstanding": None,
        "trade_date": date.today().isoformat(),
        "source_url": url,
    }


def _timeseries_values(item: dict, field: str) -> list[dict]:
    values = item.get(field) or []
    rows = []
    for value in values:
        reported = value.get("reportedValue", {})
        rows.append(
            {
                "as_of_date": value.get("asOfDate"),
                "period_type": value.get("periodType"),
                "currency": value.get("currencyCode"),
                "value": _raw_value(reported),
            }
        )
    return rows


def _latest_timeseries_value(item: dict, field: str) -> tuple[float | None, str | None, str | None]:
    values = item.get(field) or []
    if not values:
        return None, None, None
    latest = values[-1]
    reported = latest.get("reportedValue", {})
    return _raw_value(reported), latest.get("currencyCode"), latest.get("asOfDate")


def fetch_financials(symbol: str, refresh: bool = False) -> dict:
    metric_types = [
        "annualTotalRevenue",
        "annualNetIncome",
        "annualGrossProfit",
        "annualOperatingIncome",
        "annualOperatingCashFlow",
        "annualFreeCashFlow",
        "annualTotalDebt",
        "annualCashCashEquivalentsAndShortTermInvestments",
        "trailingTotalRevenue",
        "trailingNetIncome",
        "trailingBasicAverageShares",
        "trailingDilutedAverageShares",
    ]
    period2 = int(time.time())
    period1 = period2 - 365 * 24 * 60 * 60 * 6
    url = f"{YAHOO_TIMESERIES_URL.format(symbol=quote(symbol))}?{urlencode({'symbol': symbol, 'type': ','.join(metric_types), 'merge': 'false', 'period1': period1, 'period2': period2})}"
    data = _get_json(url, refresh=refresh)
    result = data.get("timeseries", {}).get("result") or []
    if not result:
        raise PublicDataError(f"financial summary not found for symbol: {symbol}")

    metrics: dict[str, tuple[float | None, str | None, str | None]] = {}
    history: dict[str, list[dict]] = {}
    for item in result:
        for field in metric_types:
            if field in item:
                metrics[field] = _latest_timeseries_value(item, field)
                history[field] = _timeseries_values(item, field)

    revenue, revenue_currency, revenue_date = metrics.get("trailingTotalRevenue", (None, None, None))
    if revenue is None:
        revenue, revenue_currency, revenue_date = metrics.get("annualTotalRevenue", (None, None, None))
    net_profit, profit_currency, profit_date = metrics.get("trailingNetIncome", (None, None, None))
    if net_profit is None:
        net_profit, profit_currency, profit_date = metrics.get("annualNetIncome", (None, None, None))
    shares, _, _ = metrics.get("trailingDilutedAverageShares", (None, None, None))
    if shares is None:
        shares, _, _ = metrics.get("trailingBasicAverageShares", (None, None, None))

    return {
        "period": profit_date or revenue_date or "latest_public",
        "currency": profit_currency or revenue_currency or "USD",
        "unit": "yuan",
        "revenue": revenue,
        "net_profit": net_profit,
        "adjusted_net_profit": net_profit,
        "gross_profit": _first_number(metrics.get("annualGrossProfit", (None, None, None))[0]),
        "operating_profit": _first_number(metrics.get("annualOperatingIncome", (None, None, None))[0]),
        "operating_cash_flow": _first_number(metrics.get("annualOperatingCashFlow", (None, None, None))[0]),
        "free_cash_flow": _first_number(metrics.get("annualFreeCashFlow", (None, None, None))[0]),
        "ebitda": None,
        "cash": _first_number(metrics.get("annualCashCashEquivalentsAndShortTermInvestments", (None, None, None))[0]),
        "debt": _first_number(metrics.get("annualTotalDebt", (None, None, None))[0]),
        "shares_outstanding": shares,
        "financial_history": history,
        "source_url": url,
    }


def lookup_public_company(query: str, refresh: bool = False) -> dict:
    resolved = resolve_symbol(query, refresh=refresh)
    symbol = resolved["symbol"]
    quote_data = fetch_quote(symbol, refresh=refresh)
    financials = fetch_financials(symbol, refresh=refresh)

    shares_outstanding = quote_data.get("shares_outstanding") or financials.get("shares_outstanding")
    market_cap = quote_data.get("market_cap")
    if market_cap is None and shares_outstanding is not None and quote_data.get("share_price") is not None:
        market_cap = shares_outstanding * quote_data["share_price"]
    if shares_outstanding is None and market_cap and quote_data.get("share_price"):
        shares_outstanding = market_cap / quote_data["share_price"]

    return {
        "ticker": symbol,
        "company_name": quote_data.get("company_name") or resolved["company_name"],
        "exchange": quote_data.get("exchange") or resolved["exchange"],
        "currency": quote_data.get("currency") or financials.get("currency") or "USD",
        "financial_currency": financials.get("currency") or quote_data.get("currency") or "USD",
        "industry": [item for item in [resolved.get("sector"), resolved.get("industry")] if item],
        "share_price": quote_data.get("share_price"),
        "market_cap": market_cap,
        "shares_outstanding": shares_outstanding,
        "trade_date": quote_data.get("trade_date"),
        "revenue": financials.get("revenue"),
        "net_profit": financials.get("net_profit"),
        "adjusted_net_profit": financials.get("adjusted_net_profit"),
        "gross_profit": financials.get("gross_profit"),
        "operating_profit": financials.get("operating_profit"),
        "operating_cash_flow": financials.get("operating_cash_flow"),
        "free_cash_flow": financials.get("free_cash_flow"),
        "ebitda": financials.get("ebitda"),
        "cash": financials.get("cash"),
        "debt": financials.get("debt"),
        "financial_history": financials.get("financial_history"),
        "period": financials.get("period", "latest_public"),
        "unit": "yuan",
        "market_source_url": quote_data.get("source_url"),
        "financial_source_url": financials.get("source_url"),
        "resolver_source_url": resolved.get("source_url"),
    }


def enrich_payload_from_public_data(payload: dict) -> dict:
    query = payload.get("company_name") or payload.get("name") or payload.get("ticker") or payload.get("query")
    if not query:
        return payload

    has_profit = payload.get("adjusted_net_profit") is not None or payload.get("net_profit") is not None
    has_market_reference = payload.get("target_market_cap") is not None or payload.get("market_cap") is not None
    has_required_inputs = all(
        [
            payload.get("ticker"),
            payload.get("shares_outstanding") is not None,
            payload.get("revenue") is not None,
            has_profit,
            has_market_reference,
        ]
    )
    if has_required_inputs:
        return payload

    public_payload = lookup_public_company(query, refresh=payload.get("refresh", False))
    merged = dict(public_payload)
    for key, value in payload.items():
        if value is not None:
            merged[key] = value

    if merged.get("target_market_cap") is None:
        merged["target_market_cap"] = merged.get("market_cap")
    return merged
