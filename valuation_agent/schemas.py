from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


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
