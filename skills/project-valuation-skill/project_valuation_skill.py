import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from valuation_agent.project_valuation import build_project_cashflow  # noqa: E402
from valuation_agent.reporting_v3 import _to_assumptions, _to_risks  # noqa: E402
from valuation_agent.risk_expected_loss import evaluate_risks  # noqa: E402


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
    if not isinstance(project_payload, dict):
        print(json.dumps({"status": "error", "message": "project_payload required"}, ensure_ascii=False))
        sys.exit(1)
    assumptions = _to_assumptions(project_payload)

    risks_payload = _load(payload.get("risks_payload")) or []
    risks = _to_risks(risks_payload) if isinstance(risks_payload, list) else []
    summary = evaluate_risks(risks, assumptions) if risks else {"total_expected_loss_base": 0.0}

    cashflow = build_project_cashflow(
        assumptions,
        base_total_expected_loss=summary["total_expected_loss_base"],
    )
    print(json.dumps({"status": "ok", "data": cashflow.to_dict()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
