import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from valuation_agent.pipeline import run_payload_analysis  # noqa: E402
from valuation_agent.research_analysis import peer_comparison  # noqa: E402


def main() -> None:
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    result = run_payload_analysis(payload)
    data = peer_comparison(
        result,
        query=payload.get("query") or payload.get("company_name") or payload.get("ticker"),
        peer_payloads=payload.get("peer_payloads"),
    )
    print(json.dumps({"status": "ok", "data": data}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
