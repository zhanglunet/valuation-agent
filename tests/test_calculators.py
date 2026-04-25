import unittest

from valuation_agent.calculators import calculate_valuation, market_cap_to_price, required_net_profit, scenario_analysis


class CalculatorTests(unittest.TestCase):
    def test_market_cap_to_price(self):
        self.assertEqual(market_cap_to_price(20_000_000_000, 1_000_000_000), 20)

    def test_market_cap_to_price_rejects_zero_shares(self):
        with self.assertRaises(ValueError):
            market_cap_to_price(20_000_000_000, 0)

    def test_required_net_profit(self):
        self.assertEqual(required_net_profit(20_000_000_000, 20), 1_000_000_000)

    def test_calculate_valuation(self):
        result = calculate_valuation(
            target_market_cap=20_000_000_000,
            currency="HKD",
            shares_outstanding=950_000_000,
            revenue=8_640_000_000,
            net_profit=864_000_000,
        )
        self.assertAlmostEqual(result.target_share_price, 21.0526315789)
        self.assertAlmostEqual(result.implied_pe, 23.1481481481)
        self.assertAlmostEqual(result.implied_ps, 2.3148148148)

    def test_scenario_analysis(self):
        scenarios = {
            "base": {"label": "中性", "revenue_growth": 0.06, "net_margin": 0.08, "pe": 18, "ps": 1.2}
        }
        result = scenario_analysis(8_640_000_000, 950_000_000, scenarios, "HKD")
        self.assertEqual(len(result), 1)
        self.assertGreater(result[0]["target_share_price"], 0)


if __name__ == "__main__":
    unittest.main()
