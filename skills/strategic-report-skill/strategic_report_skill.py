import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from valuation_agent.reporting_v3 import (  # noqa: E402
    generate_project_report,
    generate_strategic_report,
)


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
    company_name = payload.get("company_name", "<company>")
    depth = payload.get("depth", "strategic")

    if depth == "strategic":
        scores = _load(payload.get("control_scores"))
        path = generate_strategic_report(
            company_name=company_name,
            control_scores=scores if isinstance(scores, dict) else None,
            project_strategic_weight=float(payload.get("project_strategic_weight", 0.5)),
            project_revenue_share=float(payload.get("project_revenue_share", 0.05)),
            narrative_amplification=float(payload.get("narrative_amplification", 1.5)),
        )
    else:
        project_payload = _load(payload.get("project_payload"))
        if not isinstance(project_payload, dict):
            print(json.dumps({"status": "error", "message": "project_payload required"}, ensure_ascii=False))
            sys.exit(1)
        risks = _load(payload.get("risks_payload"))
        partners = _load(payload.get("partners_payload"))
        control = _load(payload.get("control_scores"))
        competitive = _load(payload.get("competitive"))
        agents = _load(payload.get("agent_scores"))
        path = generate_project_report(
            company_name=company_name,
            project_payload=project_payload,
            risks_payload=risks if isinstance(risks, list) else None,
            partners_payload=partners if isinstance(partners, list) else None,
            control_scores=control if isinstance(control, dict) else None,
            competitive_payload=competitive if isinstance(competitive, dict) else None,
            agent_scores=agents if isinstance(agents, dict) else None,
            token_cost_score=float(payload.get("token_cost_score", 50.0)),
            project_strategic_weight=float(payload.get("project_strategic_weight", 0.5)),
            project_revenue_share=float(payload.get("project_revenue_share", 0.05)),
            narrative_amplification=float(payload.get("narrative_amplification", 1.5)),
            multiple=float(payload.get("multiple", 10.0)),
            enable_agent_section=(depth == "agent"),
        )
    print(json.dumps({"status": "ok", "report_path": str(path), "depth": depth}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
