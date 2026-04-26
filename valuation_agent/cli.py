import argparse
import json

from .calculators import calculate_valuation
from .pipeline import run_company_analysis
from .reporting import generate_deep_markdown_report, generate_deep_markdown_report_from_payload, generate_markdown_report, generate_markdown_report_from_payload


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
    }
    return {key: value for key, value in fields.items() if value is not None and value != ""}


def cmd_generate_report(args: argparse.Namespace) -> None:
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
    report.add_argument("--depth", choices=["basic", "deep"], default="basic")
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
