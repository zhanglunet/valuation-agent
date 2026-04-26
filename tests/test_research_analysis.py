import unittest

from valuation_agent.pipeline import run_payload_analysis
from valuation_agent.reporting import generate_deep_markdown_report_from_payload
from valuation_agent.research_analysis import deep_research_analysis, financial_quality, peer_comparison


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
