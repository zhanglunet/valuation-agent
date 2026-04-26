import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from valuation_agent.pipeline import run_company_analysis, run_payload_analysis  # noqa: E402


def main() -> None:
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    company_id = payload.get("company_id")
    if company_id:
        analysis = run_company_analysis(company_id, payload.get("target_market_cap"))
    else:
        analysis = run_payload_analysis(payload)
    print(json.dumps({"status": "ok", "data": analysis["scenarios"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
