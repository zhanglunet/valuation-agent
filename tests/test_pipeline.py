import unittest

from valuation_agent.pipeline import run_company_analysis
from valuation_agent.reporting import generate_markdown_report


class PipelineTests(unittest.TestCase):
    def test_run_company_analysis(self):
        result = run_company_analysis("asiasoft_1675_hk")
        self.assertEqual(result["company"].ticker, "1675.HK")
        self.assertGreater(result["valuation"].target_share_price, 0)
        self.assertEqual(len(result["scenarios"]), 3)

    def test_generate_report(self):
        path = generate_markdown_report("asiasoft_1675_hk")
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        self.assertIn("亚信科技估值分析报告", text)
        self.assertIn("不构成任何投资建议", text)


if __name__ == "__main__":
    unittest.main()
