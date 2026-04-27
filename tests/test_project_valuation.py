import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from valuation_agent.project_valuation import (
    build_project_cashflow,
    calculate_irr,
    calculate_moic,
    calculate_npv,
    calculate_payback,
)
from tests._v3_fixtures import make_basic_assumptions


class CashflowMathTests(unittest.TestCase):
    def test_irr_returns_none_when_all_positive(self) -> None:
        self.assertIsNone(calculate_irr([1.0, 1.0, 1.0]))

    def test_irr_returns_none_when_all_negative(self) -> None:
        self.assertIsNone(calculate_irr([-1.0, -1.0, -1.0]))

    def test_irr_solves_simple_case(self) -> None:
        irr = calculate_irr([-100.0, 60.0, 60.0, 60.0])
        self.assertIsNotNone(irr)
        self.assertGreater(irr, 0.30)
        self.assertLess(irr, 0.40)

    def test_moic_basic(self) -> None:
        self.assertAlmostEqual(calculate_moic([-100.0, 50.0, 100.0]), 1.5, places=4)

    def test_moic_returns_none_with_no_investment(self) -> None:
        self.assertIsNone(calculate_moic([10.0, 20.0]))

    def test_payback_returns_none_when_never_recovered(self) -> None:
        self.assertIsNone(calculate_payback([-100.0, 30.0, 30.0]))

    def test_payback_fractional(self) -> None:
        # Outflow 100 at t=0, recovers 60+60=120 by t=2 (partway through year 2).
        pb = calculate_payback([-100.0, 60.0, 60.0])
        self.assertIsNotNone(pb)
        self.assertGreater(pb, 1.0)
        self.assertLess(pb, 2.0)

    def test_npv_zero_rate(self) -> None:
        self.assertAlmostEqual(calculate_npv([-100.0, 50.0, 60.0], 0.0), 10.0, places=6)


class BuildCashflowTests(unittest.TestCase):
    def test_five_scenarios_produce_distinct_npvs(self) -> None:
        assumptions = make_basic_assumptions()
        result = build_project_cashflow(assumptions)
        self.assertEqual(len(result.by_scenario), 5)
        npvs = [sc.npv for sc in result.by_scenario.values()]
        self.assertGreater(npvs[-1], npvs[0])  # very_bull >= very_bear

    def test_probability_weighted_npv_within_range(self) -> None:
        assumptions = make_basic_assumptions()
        result = build_project_cashflow(assumptions)
        npvs = [sc.npv for sc in result.by_scenario.values()]
        self.assertGreaterEqual(result.probability_weighted_npv, min(npvs))
        self.assertLessEqual(result.probability_weighted_npv, max(npvs))

    def test_owner_share_reduces_revenue(self) -> None:
        full = build_project_cashflow(make_basic_assumptions(owner_share=1.0))
        half = build_project_cashflow(make_basic_assumptions(owner_share=0.5))
        full_rev = sum(full.by_scenario["base"].annual_revenue.values())
        half_rev = sum(half.by_scenario["base"].annual_revenue.values())
        self.assertAlmostEqual(half_rev * 2.0, full_rev, places=4)

    def test_risk_adjustment_subtracts_from_base_npv(self) -> None:
        assumptions = make_basic_assumptions()
        clean = build_project_cashflow(assumptions, base_total_expected_loss=0.0)
        adjusted = build_project_cashflow(assumptions, base_total_expected_loss=20.0)
        self.assertAlmostEqual(
            clean.risk_adjusted_base_npv - adjusted.risk_adjusted_base_npv,
            20.0,
            places=4,
        )


if __name__ == "__main__":
    unittest.main()
