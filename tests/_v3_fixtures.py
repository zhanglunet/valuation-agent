from __future__ import annotations

from valuation_agent.schemas import (
    CostLine,
    ProjectAssumptions,
    ProjectCaseAssumptions,
    RevenueLine,
    ScenarioOverride,
    SourcedValue,
)


def _sv(value: float, source: str = "user_explicit") -> SourcedValue:
    return SourcedValue(value=value, source=source)  # type: ignore[arg-type]


def make_revenue_line(
    name: str,
    yearly: dict[int, float],
    owner_share: float = 1.0,
    gross_margin: float = 0.5,
) -> RevenueLine:
    return RevenueLine(
        name=name,
        category="primary",
        base_values={y: _sv(v) for y, v in yearly.items()},
        owner_share=_sv(owner_share),
        gross_margin=_sv(gross_margin),
    )


def make_cost_line(name: str, yearly: dict[int, float], is_capex: bool = False) -> CostLine:
    return CostLine(
        name=name,
        category="capex" if is_capex else "opex",
        base_values={y: _sv(v) for y, v in yearly.items()},
        is_capex=is_capex,
    )


def make_basic_assumptions(
    years: tuple[int, ...] = (2026, 2027, 2028, 2029, 2030),
    revenue_yearly: tuple[float, ...] = (50.0, 80.0, 120.0, 180.0, 240.0),
    capex_year: int | None = 2026,
    capex_amount: float = 100.0,
    owner_share: float = 1.0,
    discount_rate: float = 0.15,
    tax_rate: float = 0.25,
    five_scenarios: bool = True,
    attribution_method: str = "row_level_via_owner_share",
) -> ProjectAssumptions:
    revenue = make_revenue_line(
        "subscription_fee",
        {y: rv for y, rv in zip(years, revenue_yearly)},
        owner_share=owner_share,
        gross_margin=0.55,
    )
    capex = []
    if capex_year is not None:
        capex.append(make_cost_line("platform_buildout", {capex_year: capex_amount}, is_capex=True))
    base = ProjectCaseAssumptions(
        project_name="reference_project",
        start_year=years[0],
        years=list(years),
        revenue_lines=[revenue],
        cost_lines=[],
        capex_lines=capex,
        tax_rate=_sv(tax_rate),
        discount_rate=_sv(discount_rate),
    )
    scenarios = {}
    if five_scenarios:
        config = [
            ("very_bear", 0.10, 0.5, 0.04, ["compliance_blocker"]),
            ("bear", 0.20, 0.75, 0.02, []),
            ("base", 0.40, 1.0, 0.0, []),
            ("bull", 0.20, 1.20, -0.01, []),
            ("very_bull", 0.10, 1.50, -0.03, []),
        ]
        for name, prob, mult, dr_delta, risks in config:
            scenarios[name] = ScenarioOverride(
                scenario=name,  # type: ignore[arg-type]
                scenario_probability=prob,
                revenue_multiplier={"subscription_fee": mult},
                margin_delta={},
                owner_share_delta={},
                discount_rate_delta=dr_delta,
                capex_multiplier={},
                activated_risks=risks,
            )
    return ProjectAssumptions(
        base_case=base,
        scenarios=scenarios,
        attribution_method=attribution_method,  # type: ignore[arg-type]
    )
