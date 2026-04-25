import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from valuation_agent.storage import load_financial_statement  # noqa: E402


def main() -> None:
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    company_id = payload.get("company_id")
    if company_id:
        data = load_financial_statement(company_id).__dict__
    else:
        data = {
            "period": payload.get("period", "user_input"),
            "currency": payload.get("financial_currency") or payload.get("currency", "HKD"),
            "unit": payload.get("unit", "yuan"),
            "revenue": payload.get("revenue"),
            "gross_profit": payload.get("gross_profit"),
            "operating_profit": payload.get("operating_profit"),
            "net_profit": payload.get("net_profit"),
            "adjusted_net_profit": payload.get("adjusted_net_profit"),
            "ebitda": payload.get("ebitda"),
            "operating_cash_flow": payload.get("operating_cash_flow"),
            "cash": payload.get("cash"),
            "debt": payload.get("debt"),
            "source_url": payload.get("source_url", "user_input"),
        }
    print(json.dumps({"status": "ok", "data": data}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
