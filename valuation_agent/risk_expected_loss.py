from __future__ import annotations

from typing import Iterable

from .assumption_validator import validate_risk_no_scenario_overlap
from .schemas import (
    SCENARIO_NAMES,
    ProjectAssumptions,
    RiskExpectedLoss,
    SourcedValue,
)


def calculate_expected_loss(risk: RiskExpectedLoss) -> dict[str, float]:
    """Fill in expected_loss_by_scenario = probability × loss for every scenario."""
    out: dict[str, float] = {}
    for scenario in SCENARIO_NAMES:
        prob = float(risk.probability_by_scenario.get(scenario, 0.0))
        loss_sv = risk.loss_by_scenario.get(scenario)
        loss = float(loss_sv.value) if isinstance(loss_sv, SourcedValue) else 0.0
        out[scenario] = prob * loss
    risk.expected_loss_by_scenario = out
    return out


def total_expected_loss_for_base_case(risks: Iterable[RiskExpectedLoss]) -> float:
    total = 0.0
    for risk in risks:
        if not risk.expected_loss_by_scenario:
            calculate_expected_loss(risk)
        total += risk.expected_loss_by_scenario.get("base", 0.0)
    return total


def total_expected_loss_by_scenario(
    risks: Iterable[RiskExpectedLoss],
) -> dict[str, float]:
    aggregate = {name: 0.0 for name in SCENARIO_NAMES}
    for risk in risks:
        if not risk.expected_loss_by_scenario:
            calculate_expected_loss(risk)
        for scenario, amount in risk.expected_loss_by_scenario.items():
            aggregate[scenario] = aggregate.get(scenario, 0.0) + amount
    return aggregate


def apply_risk_adjustment_to_base_npv(base_npv: float, total_expected_loss: float) -> float:
    """Cap the loss at base_npv so the report does not silently produce
    arbitrarily negative ‘risk-adjusted’ values when the loss exceeds NPV."""
    return base_npv - min(total_expected_loss, abs(base_npv) + base_npv)


def evaluate_risks(
    risks: list[RiskExpectedLoss],
    assumptions: ProjectAssumptions,
) -> dict[str, object]:
    """End-to-end: validate non-overlap, fill expected losses, and return a
    structured summary."""
    validate_risk_no_scenario_overlap(risks, assumptions)
    for risk in risks:
        calculate_expected_loss(risk)
    return {
        "risks": risks,
        "total_expected_loss_base": total_expected_loss_for_base_case(risks),
        "total_expected_loss_by_scenario": total_expected_loss_by_scenario(risks),
    }
