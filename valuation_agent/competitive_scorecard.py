from __future__ import annotations

import json
from pathlib import Path

from .paths import CONFIG_DIR
from .schemas import (
    CompetitiveScoreResult,
    CompetitorScorecard,
    ControlDimension,
)
from .strategic_control import CONTROL_DIMENSIONS, DEFAULT_CONTROL_WEIGHTS


def load_industry_weights(industry: str) -> dict[str, float]:
    path = CONFIG_DIR / "competitive_scorecards.json"
    if path.exists():
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        if industry in data:
            return {
                dim: float(data[industry].get("weights", {}).get(dim, DEFAULT_CONTROL_WEIGHTS[dim]))
                for dim in CONTROL_DIMENSIONS
            }
    return dict(DEFAULT_CONTROL_WEIGHTS)


def _scorecard(
    company: str,
    scores: dict[str, float],
    weights: dict[str, float],
) -> CompetitorScorecard:
    dims: list[ControlDimension] = []
    weighted = 0.0
    for name in CONTROL_DIMENSIONS:
        s = max(0.0, min(100.0, float(scores.get(name, 0.0))))
        w = float(weights.get(name, DEFAULT_CONTROL_WEIGHTS.get(name, 0.0)))
        dims.append(ControlDimension(name=name, score=s, weight=w))
        weighted += s * w
    return CompetitorScorecard(company=company, dimensions=dims, weighted_score=weighted)


def score_competitors(
    target_company: str,
    target_scores: dict[str, float],
    competitor_scores: dict[str, dict[str, float]],
    industry: str = "default",
    weights: dict[str, float] | None = None,
) -> CompetitiveScoreResult:
    weights = weights or load_industry_weights(industry)
    target_card = _scorecard(target_company, target_scores, weights)
    competitor_cards = [
        _scorecard(name, scores, weights) for name, scores in competitor_scores.items()
    ]

    everyone = [target_card] + competitor_cards
    everyone_sorted = sorted(everyone, key=lambda c: c.weighted_score, reverse=True)
    rankings = [c.company for c in everyone_sorted]

    strengths: list[str] = []
    weaknesses: list[str] = []
    if competitor_cards:
        peer_avg_by_dim = {
            dim_name: (
                sum(
                    next(d for d in c.dimensions if d.name == dim_name).score
                    for c in competitor_cards
                )
                / len(competitor_cards)
            )
            for dim_name in CONTROL_DIMENSIONS
        }
        for tdim in target_card.dimensions:
            avg = peer_avg_by_dim[tdim.name]
            diff = tdim.score - avg
            if diff >= 10:
                strengths.append(f"{tdim.name}: 领先竞争者平均 {diff:.0f} 分")
            elif diff <= -10:
                weaknesses.append(f"{tdim.name}: 落后竞争者平均 {abs(diff):.0f} 分")

    # Premium suggestion: difference vs peer median, scaled and bounded.
    premium_suggestion = 0.0
    if competitor_cards:
        peer_scores = sorted(c.weighted_score for c in competitor_cards)
        median = peer_scores[len(peer_scores) // 2]
        rel = (target_card.weighted_score - median) / 100.0
        premium_suggestion = max(-0.2, min(0.3, rel))

    explanation = [
        f"目标公司 {target_company} 加权评分 {target_card.weighted_score:.1f}",
        f"竞争者数 {len(competitor_cards)}，目标公司排名 {rankings.index(target_company) + 1}/{len(rankings)}",
        (
            f"按相对位次建议估值倍数 {'+' if premium_suggestion >= 0 else ''}{premium_suggestion*100:.1f}%。"
            "注：此建议供 reporting 参考，不直接叠加到 strategic_control 的四因子溢价。"
        ),
    ]

    return CompetitiveScoreResult(
        target_company=target_company,
        target_scorecard=target_card,
        competitor_scorecards=competitor_cards,
        rankings=rankings,
        target_strengths=strengths,
        target_weaknesses=weaknesses,
        multiple_premium_suggestion=premium_suggestion,
        explanation=explanation,
    )
