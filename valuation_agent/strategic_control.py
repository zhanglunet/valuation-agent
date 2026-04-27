from __future__ import annotations

import json
from pathlib import Path

from .paths import CONFIG_DIR
from .schemas import ControlDimension, StrategicControlScore


CONTROL_DIMENSIONS: tuple[str, ...] = (
    "gateway_control",
    "data_security",
    "agent_lifecycle",
    "industry_knowhow",
    "channel_access",
    "technology",
    "system_integration",
    "retention",
    "resource_mobilization",
    "repeatable_methodology",
)

DEFAULT_CONTROL_WEIGHTS: dict[str, float] = {
    "gateway_control": 0.15,
    "data_security": 0.15,
    "agent_lifecycle": 0.15,
    "industry_knowhow": 0.10,
    "channel_access": 0.10,
    "technology": 0.08,
    "system_integration": 0.08,
    "retention": 0.07,
    "resource_mobilization": 0.06,
    "repeatable_methodology": 0.06,
}


def load_control_weights() -> dict[str, float]:
    path = CONFIG_DIR / "strategic_control_weights.json"
    if path.exists():
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        return {dim: float(data.get(dim, DEFAULT_CONTROL_WEIGHTS[dim])) for dim in CONTROL_DIMENSIONS}
    return dict(DEFAULT_CONTROL_WEIGHTS)


def score_strategic_control(
    scores: dict[str, float],
    weights: dict[str, float] | None = None,
    evidence: dict[str, list[str]] | None = None,
) -> tuple[list[ControlDimension], float]:
    """Score each control dimension on a 0-100 scale and return the weighted
    aggregate. Missing dimensions default to 0 (penalize unknown control)."""
    weights = weights or load_control_weights()
    evidence = evidence or {}
    dims: list[ControlDimension] = []
    weighted = 0.0
    for name in CONTROL_DIMENSIONS:
        score = float(scores.get(name, 0.0))
        score = max(0.0, min(100.0, score))
        weight = float(weights.get(name, DEFAULT_CONTROL_WEIGHTS.get(name, 0.0)))
        weighted += score * weight
        dims.append(ControlDimension(
            name=name,
            score=score,
            weight=weight,
            evidence=evidence.get(name, []),
        ))
    return dims, weighted


def map_control_score_to_premium(
    weighted_score: float,
    project_strategic_weight: float,
    project_revenue_share: float,
    narrative_amplification: float,
) -> float:
    """Four-factor mapping from control-point score to company-level premium.

    See V3_DESIGN_AND_DEV_PLAN section 3.2:
        premium = (weighted_score / 100)
                  × project_strategic_weight
                  × project_revenue_share
                  × narrative_amplification

    All intermediate factors are bounded so a 100-score project that
    represents 1% of revenue cannot inflate company-level multiples.
    """
    score_norm = max(0.0, min(1.0, weighted_score / 100.0))
    sw = max(0.0, min(1.0, project_strategic_weight))
    rs = max(0.0, min(1.0, project_revenue_share))
    na = max(1.0, min(3.0, narrative_amplification))
    return score_norm * sw * rs * na


def explain_control_score(
    dims: list[ControlDimension],
    weighted_score: float,
    project_strategic_weight: float,
    project_revenue_share: float,
    narrative_amplification: float,
    valuation_premium: float,
) -> list[str]:
    sorted_dims = sorted(dims, key=lambda d: d.score * d.weight, reverse=True)
    top = sorted_dims[:3]
    bottom = sorted_dims[-2:]
    lines = [
        f"加权控制点评分 {weighted_score:.1f}/100。",
        "Top 三个贡献维度：" + "、".join(f"{d.name}={d.score:.0f}" for d in top) + "。",
        "最弱两个维度：" + "、".join(f"{d.name}={d.score:.0f}" for d in bottom) + "。",
        (
            f"四因子映射：score_norm={weighted_score/100:.2f} × "
            f"strategic_weight={project_strategic_weight:.2f} × "
            f"revenue_share={project_revenue_share:.3f} × "
            f"narrative_amp={narrative_amplification:.1f} "
            f"=> 公司估值溢价系数 {valuation_premium:.4f}。"
        ),
    ]
    return lines


def evaluate_strategic_control(
    scores: dict[str, float],
    project_strategic_weight: float,
    project_revenue_share: float,
    narrative_amplification: float,
    weights: dict[str, float] | None = None,
    evidence: dict[str, list[str]] | None = None,
) -> StrategicControlScore:
    dims, weighted = score_strategic_control(scores, weights, evidence)
    premium = map_control_score_to_premium(
        weighted, project_strategic_weight, project_revenue_share, narrative_amplification
    )
    explanation = explain_control_score(
        dims, weighted, project_strategic_weight, project_revenue_share,
        narrative_amplification, premium,
    )
    return StrategicControlScore(
        dimensions=dims,
        weighted_score=weighted,
        project_strategic_weight=project_strategic_weight,
        project_revenue_share=project_revenue_share,
        narrative_amplification=narrative_amplification,
        valuation_premium=premium,
        explanation=explanation,
    )
