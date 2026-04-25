import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from valuation_agent.storage import load_market_snapshot  # noqa: E402
from valuation_agent.public_data import enrich_payload_from_public_data  # noqa: E402


def main() -> None:
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    company_id = payload.get("company_id")
    if company_id:
        data = load_market_snapshot(company_id).__dict__
    else:
        payload = enrich_payload_from_public_data(payload)
        ticker = payload["ticker"]
        shares_outstanding = payload.get("shares_outstanding")
        share_price = payload.get("share_price")
        market_cap = payload.get("market_cap")
        if market_cap is None and shares_outstanding is not None and share_price is not None:
            market_cap = shares_outstanding * share_price
        data = {
            "ticker": ticker,
            "trade_date": payload.get("trade_date", "user_input"),
            "currency": payload.get("currency", "HKD"),
            "share_price": share_price,
            "market_cap": market_cap,
            "shares_outstanding": shares_outstanding,
            "volume": payload.get("volume"),
            "source_url": payload.get("source_url", "user_input"),
        }
    print(json.dumps({"status": "ok", "data": data}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
