import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from valuation_agent.competitive_scorecard import score_competitors
from valuation_agent.strategic_control import CONTROL_DIMENSIONS


class CompetitiveScorecardTests(unittest.TestCase):
    def test_target_leads_when_higher_scores(self) -> None:
        target_scores = {dim: 80.0 for dim in CONTROL_DIMENSIONS}
        peer_a = {dim: 50.0 for dim in CONTROL_DIMENSIONS}
        peer_b = {dim: 60.0 for dim in CONTROL_DIMENSIONS}
        result = score_competitors(
            target_company="<target>",
            target_scores=target_scores,
            competitor_scores={"<a>": peer_a, "<b>": peer_b},
            industry="default",
        )
        self.assertEqual(result.rankings[0], "<target>")
        self.assertGreater(result.multiple_premium_suggestion, 0.0)

    def test_target_lags_when_lower_scores(self) -> None:
        target_scores = {dim: 30.0 for dim in CONTROL_DIMENSIONS}
        peer_a = {dim: 70.0 for dim in CONTROL_DIMENSIONS}
        result = score_competitors(
            target_company="<target>",
            target_scores=target_scores,
            competitor_scores={"<a>": peer_a},
            industry="default",
        )
        self.assertNotEqual(result.rankings[0], "<target>")
        self.assertLess(result.multiple_premium_suggestion, 0.0)

    def test_strengths_and_weaknesses_reported(self) -> None:
        target_scores = {dim: 50.0 for dim in CONTROL_DIMENSIONS}
        target_scores["gateway_control"] = 95.0
        target_scores["retention"] = 10.0
        peer_a = {dim: 60.0 for dim in CONTROL_DIMENSIONS}
        result = score_competitors(
            target_company="<target>",
            target_scores=target_scores,
            competitor_scores={"<a>": peer_a},
            industry="default",
        )
        self.assertTrue(any("gateway_control" in s for s in result.target_strengths))
        self.assertTrue(any("retention" in w for w in result.target_weaknesses))


if __name__ == "__main__":
    unittest.main()
