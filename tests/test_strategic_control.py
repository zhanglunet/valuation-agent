import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from valuation_agent.strategic_control import (
    CONTROL_DIMENSIONS,
    evaluate_strategic_control,
    map_control_score_to_premium,
)


class StrategicControlTests(unittest.TestCase):
    def test_perfect_score_with_tiny_revenue_share_caps_premium(self) -> None:
        # 100/100 score, 1% revenue share, narrative=1.0 -> premium <= 1%
        premium = map_control_score_to_premium(100.0, 1.0, 0.01, 1.0)
        self.assertLessEqual(premium, 0.011)

    def test_premium_amplifies_with_narrative(self) -> None:
        low = map_control_score_to_premium(100.0, 1.0, 0.10, 1.0)
        high = map_control_score_to_premium(100.0, 1.0, 0.10, 3.0)
        self.assertAlmostEqual(high, low * 3.0, places=4)

    def test_factors_bounded(self) -> None:
        # Excessive amplification > 3.0 should be clamped.
        capped = map_control_score_to_premium(100.0, 1.0, 1.0, 100.0)
        natural = map_control_score_to_premium(100.0, 1.0, 1.0, 3.0)
        self.assertAlmostEqual(capped, natural, places=4)

    def test_evaluate_returns_full_record(self) -> None:
        scores = {dim: 80.0 for dim in CONTROL_DIMENSIONS}
        record = evaluate_strategic_control(
            scores=scores,
            project_strategic_weight=0.6,
            project_revenue_share=0.10,
            narrative_amplification=2.0,
        )
        self.assertEqual(len(record.dimensions), 10)
        self.assertGreater(record.weighted_score, 70.0)
        self.assertGreater(record.valuation_premium, 0.0)
        self.assertTrue(record.explanation)


if __name__ == "__main__":
    unittest.main()
