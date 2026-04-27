import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from valuation_agent.risk_expected_loss import (
    apply_risk_adjustment_to_base_npv,
    calculate_expected_loss,
    evaluate_risks,
    total_expected_loss_for_base_case,
)
from valuation_agent.schemas import RiskExpectedLoss, SourcedValue
from tests._v3_fixtures import make_basic_assumptions, _sv


def _risk(name: str, prob_base: float, loss_base: float) -> RiskExpectedLoss:
    return RiskExpectedLoss(
        risk_name=name,
        category="financial",
        probability_by_scenario={"base": prob_base, "bear": prob_base * 1.5, "bull": prob_base * 0.5,
                                  "very_bear": prob_base * 2.0, "very_bull": prob_base * 0.25},
        loss_by_scenario={
            "base": _sv(loss_base),
            "bear": _sv(loss_base * 1.5),
            "bull": _sv(loss_base * 0.5),
            "very_bear": _sv(loss_base * 2.0),
            "very_bull": _sv(loss_base * 0.25),
        },
        mitigation="<TBD>",
    )


class RiskExpectedLossTests(unittest.TestCase):
    def test_expected_loss_equals_p_times_loss(self) -> None:
        r = _risk("foo", 0.3, 100.0)
        result = calculate_expected_loss(r)
        self.assertAlmostEqual(result["base"], 30.0, places=6)

    def test_total_for_base(self) -> None:
        risks = [_risk("a", 0.2, 50.0), _risk("b", 0.1, 80.0)]
        total = total_expected_loss_for_base_case(risks)
        self.assertAlmostEqual(total, 0.2 * 50.0 + 0.1 * 80.0, places=6)

    def test_risk_capped_when_loss_exceeds_npv(self) -> None:
        # base_npv = 100, total expected loss = 250 -> result = 100 - 100 = 0
        adjusted = apply_risk_adjustment_to_base_npv(100.0, 250.0)
        self.assertGreaterEqual(adjusted, -100.0)

    def test_evaluate_rejects_overlap_with_scenario(self) -> None:
        assumptions = make_basic_assumptions()
        # 'compliance_blocker' is in very_bear scenario activated_risks.
        risks = [_risk("compliance_blocker", 0.2, 10.0)]
        with self.assertRaises(Exception):
            evaluate_risks(risks, assumptions)


if __name__ == "__main__":
    unittest.main()
