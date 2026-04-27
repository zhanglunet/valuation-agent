from __future__ import annotations

from typing import Iterable

from .schemas import (
    AssumptionAudit,
    AssumptionAuditEntry,
    ProjectAssumptions,
    RiskExpectedLoss,
    SCENARIO_NAMES,
    SourcedValue,
    ValueAttribution,
)


class MissingSourceError(ValueError):
    """Raised when a required SourcedValue is absent or marked fabricated."""


class DoubleAttributionError(ValueError):
    """Raised when row-level owner_share and project-level value_attribution
    are both active for the same project."""


class ScenarioProbabilityError(ValueError):
    """Raised when scenario probabilities do not sum to 1."""


class RiskOverlapError(ValueError):
    """Raised when a risk-matrix entry overlaps with a scenario narrative."""


def _check_sourced(value: SourcedValue, field_path: str) -> None:
    if value is None:
        raise MissingSourceError(f"{field_path} is missing a SourcedValue wrapper")
    if value.source == "fabricated":
        raise MissingSourceError(
            f"{field_path} has source='fabricated' which is not allowed; "
            "supply user_explicit/disclosed/template/analogy/derived"
        )


def validate_project_assumptions(assumptions: ProjectAssumptions) -> None:
    """Strict validation of a ProjectAssumptions instance.

    Raises MissingSourceError, ScenarioProbabilityError, or
    DoubleAttributionError. Use this before running any cash-flow math.
    """
    base = assumptions.base_case
    if not base.years:
        raise ValueError("ProjectCaseAssumptions.years must not be empty")
    _check_sourced(base.tax_rate, "base_case.tax_rate")
    _check_sourced(base.discount_rate, "base_case.discount_rate")
    if base.terminal_growth_rate is not None:
        _check_sourced(base.terminal_growth_rate, "base_case.terminal_growth_rate")

    for line in base.revenue_lines:
        _check_sourced(line.owner_share, f"revenue.{line.name}.owner_share")
        for year, sv in line.base_values.items():
            _check_sourced(sv, f"revenue.{line.name}.base_values[{year}]")
        if line.gross_margin is not None:
            _check_sourced(line.gross_margin, f"revenue.{line.name}.gross_margin")

    for line in base.cost_lines:
        for year, sv in line.base_values.items():
            _check_sourced(sv, f"cost.{line.name}.base_values[{year}]")

    for line in base.capex_lines:
        for year, sv in line.base_values.items():
            _check_sourced(sv, f"capex.{line.name}.base_values[{year}]")

    if assumptions.scenarios:
        missing = [name for name in SCENARIO_NAMES if name not in assumptions.scenarios]
        if missing:
            raise ScenarioProbabilityError(
                f"missing scenario overrides: {missing}"
            )
        total = sum(s.scenario_probability for s in assumptions.scenarios.values())
        if abs(total - 1.0) > 1e-6:
            raise ScenarioProbabilityError(
                f"scenario probabilities sum to {total:.4f}, expected 1.0"
            )

    if assumptions.attribution_method == "project_level_via_value_attribution":
        non_default_owner = [
            line.name
            for line in base.revenue_lines
            if abs(line.owner_share.value - 1.0) > 1e-9
        ]
        if non_default_owner:
            raise DoubleAttributionError(
                "attribution_method=project_level_via_value_attribution but "
                f"these revenue lines have owner_share != 1.0: {non_default_owner}. "
                "Choose row-level OR project-level, not both."
            )


def validate_risk_no_scenario_overlap(
    risks: Iterable[RiskExpectedLoss],
    assumptions: ProjectAssumptions,
) -> None:
    """A risk's name must not appear inside any scenario.activated_risks list,
    AND vice versa. Either approach is fine, but the same event must not be
    counted in both axes — see V3 design 3.3 / 3.4 boundary."""
    risk_names = {r.risk_name for r in risks}
    for scenario in assumptions.scenarios.values():
        overlap = risk_names.intersection(scenario.activated_risks)
        if overlap:
            raise RiskOverlapError(
                f"risk(s) {sorted(overlap)} appear in both the risk matrix and "
                f"scenario '{scenario.scenario}'.activated_risks — pick one axis."
            )


def validate_attribution_against_assumptions(
    attribution: ValueAttribution,
    assumptions: ProjectAssumptions,
) -> None:
    """Confirm the attribution method matches the assumptions'."""
    if attribution.method != assumptions.attribution_method:
        raise DoubleAttributionError(
            f"ValueAttribution.method={attribution.method} but assumptions request "
            f"{assumptions.attribution_method}"
        )


def build_assumption_audit(assumptions: ProjectAssumptions) -> AssumptionAudit:
    """Walk every SourcedValue in the project and emit an audit table.

    The 'high_confidence_share' is the proportion of values whose source is
    user_explicit or disclosed (L1+L2). Below 50% the report header should
    show a 'high_assumption_dependency' warning.
    """
    entries: list[AssumptionAuditEntry] = []
    has_fabricated = False

    def push(path: str, sv: SourcedValue | None) -> None:
        nonlocal has_fabricated
        if sv is None:
            return
        if sv.source == "fabricated":
            has_fabricated = True
        entries.append(
            AssumptionAuditEntry(
                field_path=path,
                value=sv.value,
                source=sv.source,
                source_detail=sv.source_detail,
                confidence=float(sv.confidence or 0.0),
            )
        )

    base = assumptions.base_case
    push("base_case.tax_rate", base.tax_rate)
    push("base_case.discount_rate", base.discount_rate)
    push("base_case.terminal_growth_rate", base.terminal_growth_rate)
    for line in base.revenue_lines:
        push(f"revenue.{line.name}.owner_share", line.owner_share)
        push(f"revenue.{line.name}.gross_margin", line.gross_margin)
        for year, sv in line.base_values.items():
            push(f"revenue.{line.name}.base_values[{year}]", sv)
    for line in base.cost_lines:
        for year, sv in line.base_values.items():
            push(f"cost.{line.name}.base_values[{year}]", sv)
    for line in base.capex_lines:
        for year, sv in line.base_values.items():
            push(f"capex.{line.name}.base_values[{year}]", sv)

    high = [e for e in entries if e.source in ("user_explicit", "disclosed")]
    high_share = (len(high) / len(entries)) if entries else 0.0
    warning = None
    if has_fabricated:
        warning = "fabricated_source_detected"
    elif high_share < 0.5:
        warning = "high_assumption_dependency"

    return AssumptionAudit(
        entries=entries,
        high_confidence_share=high_share,
        has_fabricated=has_fabricated,
        warning_label=warning,
    )
