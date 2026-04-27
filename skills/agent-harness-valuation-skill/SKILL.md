---
name: agent-harness-valuation-skill
description: Score an AI Agent / Harness project on six core dimensions and apply a token-cost modifier (0.5–1.5). Maps the final score to a discount/neutral/premium/platform_premium band.
license: internal
---

# agent-harness-valuation-skill

## 输入

```json
{
  "agent_scores": {
    "model_intelligence": 80, "harness_quality": 85, "skill_surface": 70,
    "identity_security_control": 75, "workflow_ownership": 80,
    "outcome_pricing_ability": 60
  },
  "token_cost_score": 70
}
```

## 调用

```bash
python3 agent_harness_valuation_skill.py '{"agent_scores": {...}, "token_cost_score": 70}'
```
