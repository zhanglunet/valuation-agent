import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from valuation_agent.competitive_scorecard import score_competitors  # noqa: E402


def main() -> None:
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    result = score_competitors(
        target_company=payload.get("target_company", "<target>"),
        target_scores=payload.get("target_scores") or {},
        competitor_scores=payload.get("competitor_scores") or {},
        industry=payload.get("industry", "default"),
    )
    print(json.dumps({"status": "ok", "data": result.to_dict()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
