import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from valuation_agent.assumption_validator import DoubleAttributionError
from valuation_agent.project_valuation import build_project_cashflow
from valuation_agent.schemas import PartnerShare, SourcedValue
from valuation_agent.value_attribution import (
    calculate_market_cap_uplift,
    calculate_partner_split,
    evaluate_value_attribution,
)
from tests._v3_fixtures import make_basic_assumptions


class ValueAttributionTests(unittest.TestCase):
    def test_partner_split_proportional(self) -> None:
        pool = {2026: 100.0, 2027: 200.0}
        partners = [
            PartnerShare(role="listed_company", share_ratio=SourcedValue(0.6, "user_explicit")),
            PartnerShare(role="model_vendor", share_ratio=SourcedValue(0.4, "user_explicit")),
        ]
        split = calculate_partner_split(pool, partners)
        self.assertAlmostEqual(split["listed_company"][2026], 60.0)
        self.assertAlmostEqual(split["model_vendor"][2027], 80.0)

    def test_row_level_attribution_matches_owner_share(self) -> None:
        # owner_share=0.5, so target revenue should be half of project pool.
        assumptions = make_basic_assumptions(owner_share=0.5)
        cashflow = build_project_cashflow(assumptions)
        attribution = evaluate_value_attribution(assumptions, cashflow, multiple=10.0)
        target_rev = sum(attribution.target_company_revenue.values())
        pool_rev = sum(attribution.total_project_revenue.values())
        # In row-level method, project pool == target revenue (already split).
        self.assertAlmostEqual(target_rev, pool_rev, places=6)
        self.assertAlmostEqual(attribution.attribution_ratio, 1.0, places=6)

    def test_project_level_attribution_uses_partner_share(self) -> None:
        assumptions = make_basic_assumptions(
            owner_share=1.0,
            attribution_method="project_level_via_value_attribution",
        )
        cashflow = build_project_cashflow(assumptions)
        partners = [
            PartnerShare(role="listed_company", share_ratio=SourcedValue(0.4, "user_explicit")),
            PartnerShare(role="model_vendor", share_ratio=SourcedValue(0.6, "user_explicit")),
        ]
        attribution = evaluate_value_attribution(
            assumptions, cashflow, partner_shares=partners, multiple=10.0
        )
        self.assertAlmostEqual(attribution.attribution_ratio, 0.4, places=6)

    def test_market_cap_uplift_multiplies_npv(self) -> None:
        self.assertAlmostEqual(calculate_market_cap_uplift(100.0, 12.0), 1200.0, places=6)

    def test_double_attribution_blocks_calculation(self) -> None:
        # owner_share != 1 with project-level method must fail validation.
        assumptions = make_basic_assumptions(
            owner_share=0.5,
            attribution_method="project_level_via_value_attribution",
        )
        with self.assertRaises(DoubleAttributionError):
            build_project_cashflow(assumptions)


if __name__ == "__main__":
    unittest.main()
