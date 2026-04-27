import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from valuation_agent.agent_harness_valuation import (
    AGENT_DIMENSIONS,
    calculate_token_efficiency_modifier,
    evaluate_agent_harness,
    map_score_to_premium_band,
)


class AgentHarnessTests(unittest.TestCase):
    def test_token_modifier_clamped(self) -> None:
        self.assertAlmostEqual(calculate_token_efficiency_modifier(-50.0), 0.5)
        self.assertAlmostEqual(calculate_token_efficiency_modifier(50.0), 1.0)
        self.assertAlmostEqual(calculate_token_efficiency_modifier(150.0), 1.5)

    def test_premium_band_thresholds(self) -> None:
        self.assertEqual(map_score_to_premium_band(20.0), "discount")
        self.assertEqual(map_score_to_premium_band(50.0), "neutral")
        self.assertEqual(map_score_to_premium_band(70.0), "premium")
        self.assertEqual(map_score_to_premium_band(95.0), "platform_premium")

    def test_evaluate_full_record(self) -> None:
        scores = {dim: 80.0 for dim in AGENT_DIMENSIONS}
        result = evaluate_agent_harness(scores, token_cost_score=70.0)
        self.assertGreater(result.agent_value_score, 70.0)
        self.assertGreater(result.token_efficiency_modifier, 1.0)
        self.assertGreater(result.final_agent_score, result.agent_value_score)
        self.assertIn(result.valuation_premium_band, ("premium", "platform_premium"))

    def test_low_scores_yield_discount_band(self) -> None:
        scores = {dim: 20.0 for dim in AGENT_DIMENSIONS}
        result = evaluate_agent_harness(scores, token_cost_score=10.0)
        self.assertEqual(result.valuation_premium_band, "discount")


if __name__ == "__main__":
    unittest.main()
