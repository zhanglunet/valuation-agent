import unittest

from valuation_agent.pipeline import run_company_analysis, run_payload_analysis
from valuation_agent.reporting import generate_markdown_report, generate_markdown_report_from_payload


class PipelineTests(unittest.TestCase):
    def test_run_company_analysis(self):
        result = run_company_analysis("sample_listed_company")
        self.assertEqual(result["company"].ticker, "0000.HK")
        self.assertGreater(result["valuation"].target_share_price, 0)
        self.assertEqual(len(result["scenarios"]), 3)

    def test_run_payload_analysis_for_any_listed_company(self):
        result = run_payload_analysis(
            {
                "ticker": "0700.HK",
                "company_name": "腾讯控股",
                "exchange": "HKEX",
                "currency": "HKD",
                "target_market_cap": 4_000_000_000_000,
                "shares_outstanding": 9_500_000_000,
                "share_price": 420,
                "revenue": 650_000_000_000,
                "adjusted_net_profit": 180_000_000_000,
            }
        )
        self.assertEqual(result["company"].ticker, "0700.HK")
        self.assertAlmostEqual(result["valuation"].target_share_price, 421.0526315789)

    def test_scenarios_use_company_margin_when_available(self):
        result = run_payload_analysis(
            {
                "ticker": "AAPL",
                "company_name": "Apple Inc.",
                "exchange": "NASDAQ",
                "currency": "USD",
                "target_market_cap": 3_000_000_000_000,
                "shares_outstanding": 15_000_000_000,
                "share_price": 190,
                "revenue": 400_000_000_000,
                "adjusted_net_profit": 100_000_000_000,
            }
        )
        margins = {item["key"]: item["assumptions"]["net_margin"] for item in result["scenarios"]}
        self.assertAlmostEqual(margins["base"], 0.25)
        self.assertGreater(margins["bull"], margins["base"])
        self.assertLess(margins["bear"], margins["base"])

    def test_generate_report(self):
        path = generate_markdown_report("sample_listed_company")
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        self.assertIn("示例上市公司估值分析报告", text)
        self.assertIn("不构成任何投资建议", text)

    def test_generate_report_from_payload(self):
        path = generate_markdown_report_from_payload(
            {
                "ticker": "0700.HK",
                "company_name": "腾讯控股",
                "exchange": "HKEX",
                "currency": "HKD",
                "target_market_cap": 4_000_000_000_000,
                "shares_outstanding": 9_500_000_000,
                "share_price": 420,
                "revenue": 650_000_000_000,
                "adjusted_net_profit": 180_000_000_000,
            }
        )
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        self.assertIn("腾讯控股估值分析报告", text)
        self.assertIn("0700.HK", text)


if __name__ == "__main__":
    unittest.main()
