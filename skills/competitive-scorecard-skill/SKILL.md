---
name: competitive-scorecard-skill
description: Score the target company and competitors on the same 10-dim schema; output rank, strengths, weaknesses, and a relative-multiple premium suggestion.
license: internal
---

# competitive-scorecard-skill

## 输入

```json
{
  "target_company": "<target>",
  "target_scores": {"gateway_control": 80, "...": 0},
  "competitor_scores": {"<peer1>": {...}, "<peer2>": {...}},
  "industry": "ai_agent_platform"
}
```

## 调用

```bash
python3 competitive_scorecard_skill.py '{"target_company": "<target>", ...}'
```
