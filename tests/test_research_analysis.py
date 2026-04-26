import unittest

from valuation_agent.pipeline import run_payload_analysis
from valuation_agent.reporting import generate_deep_markdown_report_from_payload
from valuation_agent.research_analysis import (
    business_segment_analysis,
    deep_research_analysis,
    financial_history_analysis,
    financial_quality,
    peer_comparison,
    risk_and_refutation,
)


TARGET_PAYLOAD = {
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "exchange": "NASDAQ",
    "currency": "USD",
    "target_market_cap": 3_000_000_000_000,
    "shares_outstanding": 15_000_000_000,
    "share_price": 190,
    "market_cap": 2_850_000_000_000,
    "revenue": 380_000_000_000,
    "adjusted_net_profit": 95_000_000_000,
    "financial_history": {
        "annualTotalRevenue": [
            {"as_of_date": "2022-12-31", "value": 300_000_000_000},
            {"as_of_date": "2023-12-31", "value": 340_000_000_000},
            {"as_of_date": "2024-12-31", "value": 380_000_000_000},
        ],
        "annualNetIncome": [
            {"as_of_date": "2022-12-31", "value": 75_000_000_000},
            {"as_of_date": "2023-12-31", "value": 82_000_000_000},
            {"as_of_date": "2024-12-31", "value": 95_000_000_000},
        ],
        "trailingDilutedAverageShares": [
            {"as_of_date": "2022-12-31", "value": 16_000_000_000},
            {"as_of_date": "2024-12-31", "value": 15_000_000_000},
        ],
    },
}

PEER_PAYLOADS = [
    {
        "ticker": "MSFT",
        "company_name": "Microsoft",
        "currency": "USD",
        "market_cap": 3_200_000_000_000,
        "shares_outstanding": 7_400_000_000,
        "revenue": 250_000_000_000,
        "adjusted_net_profit": 90_000_000_000,
    },
    {
        "ticker": "GOOGL",
        "company_name": "Alphabet",
        "currency": "USD",
        "market_cap": 2_200_000_000_000,
        "shares_outstanding": 12_000_000_000,
        "revenue": 330_000_000_000,
        "adjusted_net_profit": 85_000_000_000,
    },
]


class ResearchAnalysisTests(unittest.TestCase):
    def test_financial_quality(self):
        result = run_payload_analysis(TARGET_PAYLOAD)
        quality = financial_quality(result)
        self.assertAlmostEqual(quality["net_margin"], 0.25)
        self.assertIn("summary", quality)
        self.assertEqual(quality["history"]["history_quality"], "available")

    def test_financial_history_analysis(self):
        history = financial_history_analysis(TARGET_PAYLOAD["financial_history"])
        self.assertGreater(history["revenue_cagr"], 0)
        self.assertGreater(history["profit_cagr"], 0)
        self.assertLess(history["share_count_change"], 0)
        self.assertEqual(len(history["margin_trend"]), 3)

    def test_business_profile_for_configured_company(self):
        result = run_payload_analysis(TARGET_PAYLOAD)
        segments = business_segment_analysis(result)
        self.assertEqual(segments["segment_quality"], "profile")
        self.assertTrue(segments["segments"])

    def test_peer_comparison_with_explicit_peers(self):
        result = run_payload_analysis(TARGET_PAYLOAD)
        peers = peer_comparison(result, query="Apple", peer_payloads=PEER_PAYLOADS)
        self.assertEqual(peers["peer_group"]["key"], "us_big_tech")
        self.assertEqual(len(peers["peers"]), 2)
        self.assertIsNotNone(peers["median"]["pe"])

    def test_deep_research_analysis(self):
        result = run_payload_analysis(TARGET_PAYLOAD)
        analysis = deep_research_analysis(result, query="Apple", peer_payloads=PEER_PAYLOADS)
        self.assertIn("peer_comparison", analysis)
        self.assertIn("financial_quality", analysis)
        self.assertIn("risks", analysis)
        self.assertTrue(analysis["questions"]["questions"])

    def test_configured_risk_rules_trigger(self):
        payload = dict(TARGET_PAYLOAD)
        payload["market_cap"] = 5_000_000_000_000
        result = run_payload_analysis(payload)
        quality = financial_quality(result)
        risks = risk_and_refutation(result, quality, {"peer_group": {"key": "custom"}})
        risk_names = [item["risk"] for item in risks["risks"]]
        self.assertIn("估值倍数偏高", risk_names)
        self.assertEqual(risk_names.count("估值倍数偏高"), 1)

    def test_deep_report_generation(self):
        payload = dict(TARGET_PAYLOAD)
        payload["peer_payloads"] = PEER_PAYLOADS
        path = generate_deep_markdown_report_from_payload(payload)
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        self.assertIn("深度投研估值分析报告", text)
        self.assertIn("可比公司分析", text)
        self.assertIn("风险与反证", text)


if __name__ == "__main__":
    unittest.main()
