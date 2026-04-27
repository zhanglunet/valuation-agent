import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from valuation_agent.reporting_v3 import (
    generate_project_report,
    generate_strategic_report,
)
from valuation_agent.strategic_control import CONTROL_DIMENSIONS


def _basic_project_payload() -> dict:
    return {
        "base_case": {
            "project_name": "<project>",
            "start_year": 2026,
            "years": [2026, 2027, 2028, 2029, 2030],
            "tax_rate": {"value": 0.25, "source": "user_explicit"},
            "discount_rate": {"value": 0.15, "source": "user_explicit"},
            "revenue_lines": [
                {
                    "name": "subscription_fee",
                    "category": "subscription",
                    "base_values": {
                        "2026": {"value": 50.0, "source": "user_explicit"},
                        "2027": {"value": 80.0, "source": "user_explicit"},
                        "2028": {"value": 120.0, "source": "user_explicit"},
                        "2029": {"value": 180.0, "source": "user_explicit"},
                        "2030": {"value": 240.0, "source": "user_explicit"},
                    },
                    "owner_share": {"value": 1.0, "source": "user_explicit"},
                    "gross_margin": {"value": 0.55, "source": "user_explicit"},
                }
            ],
            "cost_lines": [],
            "capex_lines": [
                {
                    "name": "platform_buildout",
                    "category": "capex",
                    "base_values": {
                        "2026": {"value": 100.0, "source": "user_explicit"},
                    },
                }
            ],
        },
        "scenarios": {
            "very_bear": {"scenario_probability": 0.10, "revenue_multiplier": {"subscription_fee": 0.5}},
            "bear": {"scenario_probability": 0.20, "revenue_multiplier": {"subscription_fee": 0.75}},
            "base": {"scenario_probability": 0.40, "revenue_multiplier": {"subscription_fee": 1.0}},
            "bull": {"scenario_probability": 0.20, "revenue_multiplier": {"subscription_fee": 1.20}},
            "very_bull": {"scenario_probability": 0.10, "revenue_multiplier": {"subscription_fee": 1.50}},
        },
        "attribution_method": "row_level_via_owner_share",
    }


class ReportingV3Tests(unittest.TestCase):
    def test_strategic_report_renders_to_disk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "strategic.md"
            scores = {dim: 70.0 for dim in CONTROL_DIMENSIONS}
            path = generate_strategic_report(
                company_name="<TestCo>",
                control_scores=scores,
                project_strategic_weight=0.6,
                project_revenue_share=0.10,
                narrative_amplification=2.0,
                output_path=out,
            )
            content = path.read_text(encoding="utf-8")
            self.assertIn("战略投研报告", content)
            self.assertIn("战略控制点初评", content)

    def test_project_report_includes_all_required_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "project.md"
            payload = _basic_project_payload()
            scores = {dim: 70.0 for dim in CONTROL_DIMENSIONS}
            agent_scores = {
                "model_intelligence": 80.0,
                "harness_quality": 85.0,
                "skill_surface": 70.0,
                "identity_security_control": 75.0,
                "workflow_ownership": 80.0,
                "outcome_pricing_ability": 60.0,
            }
            path = generate_project_report(
                company_name="<TestCo>",
                project_payload=payload,
                control_scores=scores,
                agent_scores=agent_scores,
                token_cost_score=70.0,
                enable_agent_section=True,
                output_path=out,
            )
            content = path.read_text(encoding="utf-8")
            for marker in (
                "项目假设审计表",
                "五年经营模型",
                "FCF / IRR / MOIC",
                "五情景分析",
                "风险期望损失",
                "价值归属",
                "战略控制点评分",
                "Agent / Harness 估值框架",
                "竞争情报评分",
                "对公司整体估值的影响",
            ):
                self.assertIn(marker, content, f"missing section: {marker}")

    def test_project_report_omits_agent_section_when_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "project.md"
            payload = _basic_project_payload()
            path = generate_project_report(
                company_name="<TestCo>",
                project_payload=payload,
                enable_agent_section=False,
                output_path=out,
            )
            content = path.read_text(encoding="utf-8")
            self.assertNotIn("Agent / Harness 估值框架", content)


if __name__ == "__main__":
    unittest.main()
