import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from valuation_agent.strategic_control import evaluate_strategic_control  # noqa: E402


def main() -> None:
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    scores = payload.get("control_scores") or {}
    record = evaluate_strategic_control(
        scores=scores,
        project_strategic_weight=float(payload.get("project_strategic_weight", 0.5)),
        project_revenue_share=float(payload.get("project_revenue_share", 0.05)),
        narrative_amplification=float(payload.get("narrative_amplification", 1.5)),
    )
    print(json.dumps({"status": "ok", "data": record.to_dict()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
