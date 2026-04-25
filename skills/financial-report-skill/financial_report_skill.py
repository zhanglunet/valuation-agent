import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from valuation_agent.storage import load_financial_statement  # noqa: E402


def main() -> None:
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    company_id = payload.get("company_id", "asiasoft_1675_hk")
    statement = load_financial_statement(company_id)
    print(json.dumps({"status": "ok", "data": statement.__dict__}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
