import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from valuation_agent.calculators import normalize_financials, scenario_analysis  # noqa: E402
from valuation_agent.public_data import enrich_payload_from_public_data  # noqa: E402
from valuation_agent.storage import load_assumptions, load_company, load_financial_statement, load_market_snapshot  # noqa: E402


def main() -> None:
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    assumptions = load_assumptions()
    company_id = payload.get("company_id")
    if company_id:
        company = load_company(company_id)
        market = load_market_snapshot(company_id)
        statement = load_financial_statement(company_id)
        currency = company.currency
        normalized = normalize_financials(statement, currency, assumptions["fx_rates"])
        base_revenue = normalized.revenue
        shares_outstanding = market.shares_outstanding
    else:
        payload = enrich_payload_from_public_data(payload)
        currency = payload.get("currency", "HKD")
        base_revenue = payload["revenue"]
        shares_outstanding = payload["shares_outstanding"]
    scenarios = payload.get("scenarios") or assumptions["scenario_defaults"]
    result = scenario_analysis(base_revenue, shares_outstanding, scenarios, currency)
    print(json.dumps({"status": "ok", "data": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
