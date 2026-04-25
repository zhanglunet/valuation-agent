from __future__ import annotations

from pathlib import Path

from .paths import REPORTS_DIR
from .pipeline import run_company_analysis, run_payload_analysis


def money(value: float | None, unit: str = "亿") -> str:
    if value is None:
        return "缺失"
    if unit == "亿":
        return f"{value / 100_000_000:.2f} 亿"
    return f"{value:,.2f}"


def pct(value: float | None) -> str:
    if value is None:
        return "缺失"
    return f"{value * 100:.1f}%"


def multiple(value: float | None) -> str:
    if value is None:
        return "不可用"
    return f"{value:.1f}x"


def _fmt_price(value: float | None, currency: str) -> str:
    if value is None:
        return "缺失"
    return f"{value:.2f} {currency}/股"


def _build_report(result: dict) -> tuple[str, str]:
    company = result["company"]
    market = result["market"]
    normalized = result["normalized_financials"]
    valuation = result["valuation"]
    scenarios = result["scenarios"]

    target = valuation.target_market_cap
    current_market_cap = market.market_cap
    upside_to_target = None
    if current_market_cap and current_market_cap > 0:
        upside_to_target = target / current_market_cap - 1

    scenario_lines = []
    for item in scenarios:
        a = item["assumptions"]
        scenario_lines.append(
            "| {label} | {growth} | {margin} | {pe} | {ps} | {cap} | {price:.2f} |".format(
                label=item["label"],
                growth=pct(a["revenue_growth"]),
                margin=pct(a["net_margin"]),
                pe=multiple(a["pe"]),
                ps=multiple(a["ps"]),
                cap=money(item["blended_market_cap"]),
                price=item["target_share_price"],
            )
        )

    required_lines = [
        f"- 若目标 PE 为 {pe_label}，需要净利润约 {money(value)} {company.currency}。"
        for pe_label, value in valuation.required_net_profit_at_pe.items()
    ]

    warnings = valuation.warnings + normalized.warnings
    warning_text = "\n".join(f"- {item}" for item in warnings) if warnings else "- 暂无关键计算警告。"

    market_source_label = "seed/用户输入数据"
    content = f"""# {company.company_name}估值分析报告

## 1. 核心结论

以目标市值 {money(target)} {company.currency} 测算，基于总股本 {market.shares_outstanding / 100_000_000:.2f} 亿股，对应目标股价约 **{valuation.target_share_price:.2f} {company.currency}/股**。

在当前{market_source_label}下，目标市值隐含 PE 为 **{multiple(valuation.implied_pe)}**，隐含 PS 为 **{multiple(valuation.implied_ps)}**。相较当前市值 {money(current_market_cap)} {company.currency}，目标市值对应空间约 **{pct(upside_to_target)}**。

## 2. 当前市场表现

- 股票代码：{company.ticker}
- 上市地：{company.exchange}
- 行情日期：{market.trade_date}
- 当前股价：{_fmt_price(market.share_price, market.currency)}
- 当前市值：{money(market.market_cap)} {market.currency}
- 总股本：{market.shares_outstanding / 100_000_000:.2f} 亿股
- 数据来源：{market.source_url}

## 3. 目标市值倒推

- 目标市值：{money(target)} {company.currency}
- 目标股价：{valuation.target_share_price:.2f} {company.currency}/股
- 计算公式：目标股价 = 目标市值 / 总股本

## 4. 财务基本面

- 报告期：{normalized.period}
- 标准化币种：{normalized.currency}
- 收入：{money(normalized.revenue)} {normalized.currency}
- 净利润：{money(normalized.net_profit)} {normalized.currency}
- 经调整净利润：{money(normalized.adjusted_net_profit)} {normalized.currency}
- 数据来源：{normalized.source_url}

## 5. 隐含估值倍数

- 隐含 PE：{multiple(valuation.implied_pe)}
- 隐含 PS：{multiple(valuation.implied_ps)}

## 6. 达成目标市值所需利润

{chr(10).join(required_lines)}

## 7. 三情景分析

| 情景 | 收入增速 | 净利率 | PE | PS | 综合市值 | 对应股价 |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(scenario_lines)}

## 8. 关键驱动因素

- 收入增长能否恢复或保持稳定。
- AI、云服务、BSS/OSS 等业务能否贡献新增收入。
- 经调整净利率能否改善。
- 港股软件和企业数字化板块估值能否修复。
- 公司现金流和分红、回购等股东回报政策。

## 9. 主要风险

- 公开数据存在延迟，本报告 1.0 使用 seed 数据。
- 若利润低于假设，目标市值所需估值倍数会明显抬升。
- 若行业估值中枢下移，目标股价区间需下修。
- 汇率变动会影响人民币财务数据折算后的港币估值。

## 10. 计算警告

{warning_text}

## 11. 免责声明

本报告基于公开信息、用户输入或 seed 示例数据生成，仅用于研究分析和系统开发验证，不构成任何投资建议。
"""
    return company.company_id, content


def _write_report(result: dict, output_path: Path | None = None) -> Path:
    company_id, content = _build_report(result)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = output_path or REPORTS_DIR / f"{company_id}_valuation_report.md"
    path.write_text(content, encoding="utf-8")
    return path


def generate_markdown_report(company_id: str, target_market_cap: float | None = None, output_path: Path | None = None) -> Path:
    return _write_report(run_company_analysis(company_id, target_market_cap), output_path)


def generate_markdown_report_from_payload(payload: dict, output_path: Path | None = None) -> Path:
    return _write_report(run_payload_analysis(payload), output_path)
