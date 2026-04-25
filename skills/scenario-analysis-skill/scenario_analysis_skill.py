import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from valuation_agent.calculators import normalize_financials, scenario_analysis  # noqa: E402
from valuation_agent.storage import load_assumptions, load_company, load_financial_statement, load_market_snapshot  # noqa: E402


def main() -> None:
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    company_id = payload.get("company_id", "asiasoft_1675_hk")
    company = load_company(company_id)
    market = load_market_snapshot(company_id)
    statement = load_financial_statement(company_id)
    assumptions = load_assumptions()
    normalized = normalize_financials(statement, company.currency, assumptions["fx_rates"])
    scenarios = payload.get("scenarios") or assumptions["scenario_defaults"]
    result = scenario_analysis(normalized.revenue, market.shares_outstanding, scenarios, company.currency)
    print(json.dumps({"status": "ok", "data": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
