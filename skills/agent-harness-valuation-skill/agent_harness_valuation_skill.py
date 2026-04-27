import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from valuation_agent.agent_harness_valuation import evaluate_agent_harness  # noqa: E402


def main() -> None:
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    scores = payload.get("agent_scores") or {}
    token_cost = float(payload.get("token_cost_score", 50.0))
    record = evaluate_agent_harness(scores, token_cost_score=token_cost)
    print(json.dumps({"status": "ok", "data": record.to_dict()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
