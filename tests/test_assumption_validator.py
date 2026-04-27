import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from valuation_agent.assumption_validator import (
    DoubleAttributionError,
    MissingSourceError,
    RiskOverlapError,
    ScenarioProbabilityError,
    build_assumption_audit,
    validate_project_assumptions,
    validate_risk_no_scenario_overlap,
)
from valuation_agent.schemas import (
    ProjectCaseAssumptions,
    RiskExpectedLoss,
    SourcedValue,
)
from tests._v3_fixtures import make_basic_assumptions, _sv


class AssumptionValidatorTests(unittest.TestCase):
    def test_basic_assumptions_validate_clean(self) -> None:
        assumptions = make_basic_assumptions()
        validate_project_assumptions(assumptions)  # should not raise

    def test_fabricated_source_is_rejected(self) -> None:
        assumptions = make_basic_assumptions()
        assumptions.base_case.discount_rate = SourcedValue(0.12, "fabricated")  # type: ignore[arg-type]
        with self.assertRaises(MissingSourceError):
            validate_project_assumptions(assumptions)

    def test_scenario_probabilities_must_sum_to_one(self) -> None:
        assumptions = make_basic_assumptions()
        assumptions.scenarios["base"].scenario_probability = 0.99
        with self.assertRaises(ScenarioProbabilityError):
            validate_project_assumptions(assumptions)

    def test_double_attribution_detected(self) -> None:
        assumptions = make_basic_assumptions(
            owner_share=0.5,
            attribution_method="project_level_via_value_attribution",
        )
        with self.assertRaises(DoubleAttributionError):
            validate_project_assumptions(assumptions)

    def test_risk_scenario_overlap_detected(self) -> None:
        assumptions = make_basic_assumptions()
        risk = RiskExpectedLoss(
            risk_name="compliance_blocker",  # already in very_bear scenario activated_risks
            category="compliance",
            probability_by_scenario={"base": 0.2},
            loss_by_scenario={"base": _sv(10.0)},
        )
        with self.assertRaises(RiskOverlapError):
            validate_risk_no_scenario_overlap([risk], assumptions)

    def test_audit_flags_high_dependency(self) -> None:
        assumptions = make_basic_assumptions()
        # Mark all revenue and gross_margin and owner_share fields as L4 analogy
        # so high-confidence (L1+L2) share drops below 50%.
        for line in assumptions.base_case.revenue_lines:
            for y, sv in line.base_values.items():
                line.base_values[y] = SourcedValue(sv.value, "analogy")  # type: ignore[arg-type]
            line.owner_share = SourcedValue(line.owner_share.value, "analogy")  # type: ignore[arg-type]
            if line.gross_margin is not None:
                line.gross_margin = SourcedValue(line.gross_margin.value, "analogy")  # type: ignore[arg-type]
        audit = build_assumption_audit(assumptions)
        self.assertEqual(audit.warning_label, "high_assumption_dependency")
        self.assertGreater(len(audit.entries), 0)

    def test_audit_no_warning_when_user_explicit(self) -> None:
        assumptions = make_basic_assumptions()
        audit = build_assumption_audit(assumptions)
        self.assertIsNone(audit.warning_label)
        self.assertGreater(audit.high_confidence_share, 0.5)
        self.assertFalse(audit.has_fabricated)


if __name__ == "__main__":
    unittest.main()
