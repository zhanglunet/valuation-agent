import argparse
import json

from .calculators import calculate_valuation
from .pipeline import run_company_analysis
from .reporting import generate_markdown_report


def cmd_generate_report(args: argparse.Namespace) -> None:
    path = generate_markdown_report(args.company, args.target_market_cap)
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
    report.add_argument("--company", default="asiasoft_1675_hk")
    report.add_argument("--target-market-cap", type=float, default=None)
    report.set_defaults(func=cmd_generate_report)

    analyze = sub.add_parser("analyze")
    analyze.add_argument("--company", default="asiasoft_1675_hk")
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
