from __future__ import annotations

import argparse
import json
from pathlib import Path

from .calculators import calculate_valuation
from .pipeline import run_company_analysis
from .reporting import generate_deep_markdown_report, generate_deep_markdown_report_from_payload, generate_markdown_report, generate_markdown_report_from_payload
from .reporting_v3 import generate_project_report, generate_strategic_report


def _payload_from_args(args: argparse.Namespace) -> dict:
    fields = {
        "query": args.query,
        "ticker": args.ticker,
        "company_name": args.company_name,
        "exchange": args.exchange,
        "currency": args.currency,
        "financial_currency": args.financial_currency,
        "shares_outstanding": args.shares_outstanding,
        "share_price": args.share_price,
        "market_cap": args.market_cap,
        "revenue": args.revenue,
        "net_profit": args.net_profit,
        "adjusted_net_profit": args.adjusted_net_profit,
        "target_market_cap": args.target_market_cap,
        "period": args.period,
        "unit": args.unit,
        "refresh": args.refresh,
    }
    return {key: value for key, value in fields.items() if value is not None and value != ""}


def _load_json_arg(value: str | None) -> dict | list | None:
    if not value:
        return None
    p = Path(value)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return json.loads(value)


def cmd_generate_report(args: argparse.Namespace) -> None:
    if args.depth in ("strategic", "project", "agent"):
        company_name = args.query or args.company_name or args.company or "<company>"
        if args.depth == "strategic":
            scores = _load_json_arg(args.control_scores) or None
            path = generate_strategic_report(
                company_name=company_name,
                control_scores=scores,
                project_strategic_weight=args.project_strategic_weight,
                project_revenue_share=args.project_revenue_share,
                narrative_amplification=args.narrative_amplification,
            )
            print(json.dumps({"status": "ok", "report_path": str(path), "depth": args.depth}, ensure_ascii=False, indent=2))
            return

        project_payload = _load_json_arg(args.project_assumptions)
        if not isinstance(project_payload, dict):
            raise SystemExit(
                "depth=project|agent requires --project-assumptions pointing to a JSON file or string"
            )
        risks_payload = _load_json_arg(args.risks)
        partners_payload = _load_json_arg(args.partners)
        control_scores = _load_json_arg(args.control_scores)
        competitive_payload = _load_json_arg(args.competitive)
        agent_scores = _load_json_arg(args.agent_scores)
        path = generate_project_report(
            company_name=company_name,
            project_payload=project_payload,
            risks_payload=risks_payload if isinstance(risks_payload, list) else None,
            partners_payload=partners_payload if isinstance(partners_payload, list) else None,
            control_scores=control_scores if isinstance(control_scores, dict) else None,
            competitive_payload=competitive_payload if isinstance(competitive_payload, dict) else None,
            agent_scores=agent_scores if isinstance(agent_scores, dict) else None,
            token_cost_score=args.token_cost_score,
            project_strategic_weight=args.project_strategic_weight,
            project_revenue_share=args.project_revenue_share,
            narrative_amplification=args.narrative_amplification,
            multiple=args.multiple,
            enable_agent_section=(args.depth == "agent"),
        )
        print(json.dumps({"status": "ok", "report_path": str(path), "depth": args.depth}, ensure_ascii=False, indent=2))
        return

    if args.company:
        if args.depth == "deep":
            path = generate_deep_markdown_report(args.company, args.target_market_cap)
        else:
            path = generate_markdown_report(args.company, args.target_market_cap)
    else:
        payload = _payload_from_args(args)
        if args.depth == "deep":
            path = generate_deep_markdown_report_from_payload(payload)
        else:
            path = generate_markdown_report_from_payload(payload)
    print(json.dumps({"status": "ok", "report_path": str(path)}, ensure_ascii=False, indent=2))


def cmd_analyze(args: argparse.Namespace) -> None:
    result = run_company_analysis(args.company, args.target_market_cap)
    payload = {
        "company": result["company"].__dict__,
        "market": result["market"].__dict__,
        "normalized_financials": result["normalized_financials"].__dict__,
        "valuation": result["valuation"].to_dict(),
        "scenarios": result["scenarios"],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def cmd_valuation(args: argparse.Namespace) -> None:
    result = calculate_valuation(
        target_market_cap=args.target_market_cap,
        currency=args.currency,
        shares_outstanding=args.shares_outstanding,
        revenue=args.revenue,
        net_profit=args.net_profit,
    )
    print(json.dumps({"status": "ok", "data": result.to_dict()}, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="valuation-agent")
    sub = parser.add_subparsers(required=True)

    report = sub.add_parser("generate-report")
    report.add_argument("--company", default=None, help="Configured seed company_id. Optional when explicit company metrics are provided.")
    report.add_argument("--query", default=None, help="Company name, abbreviation, or ticker to resolve from public data.")
    report.add_argument("--ticker", default=None)
    report.add_argument("--company-name", default=None)
    report.add_argument("--exchange", default=None)
    report.add_argument("--currency", default=None)
    report.add_argument("--financial-currency", default=None)
    report.add_argument("--shares-outstanding", type=float, default=None)
    report.add_argument("--share-price", type=float, default=None)
    report.add_argument("--market-cap", type=float, default=None)
    report.add_argument("--revenue", type=float, default=None)
    report.add_argument("--net-profit", type=float, default=None)
    report.add_argument("--adjusted-net-profit", type=float, default=None)
    report.add_argument("--period", default=None)
    report.add_argument("--unit", default=None)
    report.add_argument("--target-market-cap", type=float, default=None)
    report.add_argument(
        "--depth",
        choices=["basic", "deep", "strategic", "project", "agent"],
        default="basic",
        help=(
            "basic|deep -> v2 report; "
            "strategic -> v3 company-only skeleton; "
            "project -> v3 company+project skeleton; "
            "agent -> project skeleton + Agent/Harness subsection"
        ),
    )
    report.add_argument("--refresh", action="store_true")
    report.add_argument("--project-assumptions", default=None,
                        help="Path or JSON string for ProjectAssumptions (depth=project|agent)")
    report.add_argument("--risks", default=None,
                        help="Path or JSON string for risk-matrix list")
    report.add_argument("--partners", default=None,
                        help="Path or JSON string for partner_shares list")
    report.add_argument("--control-scores", default=None,
                        help="Path or JSON string for 10-dim control scores")
    report.add_argument("--competitive", default=None,
                        help="Path or JSON string for competitor scorecards")
    report.add_argument("--agent-scores", default=None,
                        help="Path or JSON string for 6-dim agent/harness scores")
    report.add_argument("--token-cost-score", type=float, default=50.0,
                        help="0-100; higher = cheaper / better routed")
    report.add_argument("--project-strategic-weight", type=float, default=0.5)
    report.add_argument("--project-revenue-share", type=float, default=0.05)
    report.add_argument("--narrative-amplification", type=float, default=1.5)
    report.add_argument("--multiple", type=float, default=10.0,
                        help="PE/PS multiple used to translate NPV contribution to market-cap uplift")
    report.set_defaults(func=cmd_generate_report)

    analyze = sub.add_parser("analyze")
    analyze.add_argument("--company", required=True)
    analyze.add_argument("--target-market-cap", type=float, default=None)
    analyze.set_defaults(func=cmd_analyze)

    valuation = sub.add_parser("valuation")
    valuation.add_argument("--target-market-cap", type=float, required=True)
    valuation.add_argument("--shares-outstanding", type=float, required=True)
    valuation.add_argument("--revenue", type=float, default=None)
    valuation.add_argument("--net-profit", type=float, default=None)
    valuation.add_argument("--currency", default="HKD")
    valuation.set_defaults(func=cmd_valuation)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
