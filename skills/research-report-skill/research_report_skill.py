import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from valuation_agent.reporting import generate_deep_markdown_report, generate_deep_markdown_report_from_payload, generate_markdown_report, generate_markdown_report_from_payload  # noqa: E402


def main() -> None:
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    company_id = payload.get("company_id")
    depth = payload.get("depth", "basic")
    if company_id:
        if depth == "deep":
            path = generate_deep_markdown_report(company_id, payload.get("target_market_cap"))
        else:
            path = generate_markdown_report(company_id, payload.get("target_market_cap"))
    else:
        if depth == "deep":
            path = generate_deep_markdown_report_from_payload(payload)
        else:
            path = generate_markdown_report_from_payload(payload)
    print(json.dumps({"status": "ok", "report_path": str(path)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
