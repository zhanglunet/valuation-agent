import unittest
from unittest.mock import patch

from valuation_agent.pipeline import run_payload_analysis
from valuation_agent.public_data import enrich_payload_from_public_data, resolve_alias


PUBLIC_PAYLOAD = {
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "exchange": "NASDAQ",
    "currency": "USD",
    "financial_currency": "USD",
    "share_price": 190,
    "market_cap": 2_850_000_000_000,
    "shares_outstanding": 15_000_000_000,
    "revenue": 380_000_000_000,
    "adjusted_net_profit": 95_000_000_000,
}


class PublicDataTests(unittest.TestCase):
    @patch("valuation_agent.public_data.lookup_public_company", return_value=PUBLIC_PAYLOAD)
    def test_enrich_from_company_name(self, _mock_lookup):
        enriched = enrich_payload_from_public_data({"company_name": "Apple"})
        self.assertEqual(enriched["ticker"], "AAPL")
        self.assertEqual(enriched["shares_outstanding"], 15_000_000_000)

    def test_resolve_chinese_alias(self):
        self.assertEqual(resolve_alias("腾讯"), "0700.HK")
        self.assertEqual(resolve_alias("苹果"), "AAPL")

    @patch("valuation_agent.public_data.lookup_public_company", return_value=PUBLIC_PAYLOAD)
    def test_run_payload_analysis_from_company_name_only(self, _mock_lookup):
        result = run_payload_analysis({"company_name": "Apple"})
        self.assertEqual(result["company"].ticker, "AAPL")
        self.assertEqual(result["valuation"].target_market_cap, 2_850_000_000_000)
        self.assertAlmostEqual(result["valuation"].target_share_price, 190)


if __name__ == "__main__":
    unittest.main()
