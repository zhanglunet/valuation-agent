from __future__ import annotations

import json
from pathlib import Path

from .paths import CONFIG_DIR
from .schemas import AgentHarnessScore


AGENT_DIMENSIONS: tuple[str, ...] = (
    "model_intelligence",
    "harness_quality",
    "skill_surface",
    "identity_security_control",
    "workflow_ownership",
    "outcome_pricing_ability",
)

DEFAULT_AGENT_WEIGHTS: dict[str, float] = {
    "model_intelligence": 0.15,
    "harness_quality": 0.20,
    "skill_surface": 0.15,
    "identity_security_control": 0.15,
    "workflow_ownership": 0.20,
    "outcome_pricing_ability": 0.15,
}


def load_agent_weights() -> dict[str, float]:
    path = CONFIG_DIR / "agent_harness_weights.json"
    if path.exists():
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        return {dim: float(data.get(dim, DEFAULT_AGENT_WEIGHTS[dim])) for dim in AGENT_DIMENSIONS}
    return dict(DEFAULT_AGENT_WEIGHTS)


def calculate_token_efficiency_modifier(token_cost_score: float) -> float:
    """token_cost_score is on a 0-100 scale where higher means cheaper /
    better cached / smarter routed. The modifier maps that to [0.5, 1.5]
    linearly: 0 -> 0.5, 50 -> 1.0, 100 -> 1.5."""
    score = max(0.0, min(100.0, token_cost_score))
    return 0.5 + (score / 100.0)


def map_score_to_premium_band(final_score: float) -> str:
    if final_score < 40:
        return "discount"
    if final_score < 60:
        return "neutral"
    if final_score < 80:
        return "premium"
    return "platform_premium"


def evaluate_agent_harness(
    scores: dict[str, float],
    token_cost_score: float = 50.0,
    weights: dict[str, float] | None = None,
) -> AgentHarnessScore:
    """Score a project on the six core agent/harness dimensions and return
    the weighted final score after applying the token-cost modifier."""
    weights = weights or load_agent_weights()
    sanitized = {
        name: max(0.0, min(100.0, float(scores.get(name, 0.0))))
        for name in AGENT_DIMENSIONS
    }
    agent_value_score = sum(sanitized[name] * weights[name] for name in AGENT_DIMENSIONS)
    modifier = calculate_token_efficiency_modifier(token_cost_score)
    final = agent_value_score * modifier
    final = max(0.0, min(150.0, final))
    band = map_score_to_premium_band(final)
    explanation = [
        f"Agent value score = {agent_value_score:.1f}/100 (六维加权)",
        f"Token cost score = {token_cost_score:.0f}, modifier = {modifier:.2f}",
        f"Final agent score = {final:.1f} -> band = {band}",
    ]
    return AgentHarnessScore(
        model_intelligence=sanitized["model_intelligence"],
        harness_quality=sanitized["harness_quality"],
        skill_surface=sanitized["skill_surface"],
        identity_security_control=sanitized["identity_security_control"],
        workflow_ownership=sanitized["workflow_ownership"],
        outcome_pricing_ability=sanitized["outcome_pricing_ability"],
        weights=dict(weights),
        agent_value_score=agent_value_score,
        token_cost_efficiency=token_cost_score,
        token_efficiency_modifier=modifier,
        final_agent_score=final,
        valuation_premium_band=band,  # type: ignore[arg-type]
        explanation=explanation,
    )
