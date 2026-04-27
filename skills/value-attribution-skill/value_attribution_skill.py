import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from valuation_agent.project_valuation import build_project_cashflow  # noqa: E402
from valuation_agent.reporting_v3 import _to_assumptions, _to_partners  # noqa: E402
from valuation_agent.value_attribution import evaluate_value_attribution  # noqa: E402


def _load(value):
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    p = Path(value)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return json.loads(value)


def main() -> None:
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    project_payload = _load(payload.get("project_payload"))
    partners_payload = _load(payload.get("partners_payload")) or []
    multiple = float(payload.get("multiple", 10.0))
    if not isinstance(project_payload, dict):
        print(json.dumps({"status": "error", "message": "project_payload required"}, ensure_ascii=False))
        sys.exit(1)

    assumptions = _to_assumptions(project_payload)
    cashflow = build_project_cashflow(assumptions)
    partners = _to_partners(partners_payload) if isinstance(partners_payload, list) else []
    result = evaluate_value_attribution(assumptions, cashflow, partner_shares=partners, multiple=multiple)
    print(json.dumps({"status": "ok", "data": result.to_dict()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
