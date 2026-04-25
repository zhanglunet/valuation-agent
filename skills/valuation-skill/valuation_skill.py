import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from valuation_agent.calculators import calculate_valuation, normalize_financials  # noqa: E402
from valuation_agent.public_data import enrich_payload_from_public_data  # noqa: E402
from valuation_agent.storage import load_assumptions, load_company, load_financial_statement, load_market_snapshot  # noqa: E402


def main() -> None:
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    company_id = payload.get("company_id")

    if company_id:
        company = load_company(company_id)
        market = load_market_snapshot(company_id)
        statement = load_financial_statement(company_id)
        assumptions = load_assumptions()
        normalized = normalize_financials(statement, company.currency, assumptions["fx_rates"])
        result = calculate_valuation(
            target_market_cap=payload.get("target_market_cap") or company.default_target_market_cap,
            currency=company.currency,
            shares_outstanding=market.shares_outstanding,
            revenue=normalized.revenue,
            net_profit=normalized.adjusted_net_profit or normalized.net_profit,
        )
    else:
        payload = enrich_payload_from_public_data(payload)
        result = calculate_valuation(
            target_market_cap=payload.get("target_market_cap") or payload["market_cap"],
            currency=payload.get("currency", "HKD"),
            shares_outstanding=payload["shares_outstanding"],
            revenue=payload.get("revenue"),
            net_profit=payload.get("net_profit"),
        )

    print(json.dumps({"status": "ok", "data": result.to_dict()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
