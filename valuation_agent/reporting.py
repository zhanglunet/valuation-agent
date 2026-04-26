from __future__ import annotations

from pathlib import Path

from .paths import REPORTS_DIR
from .pipeline import run_company_analysis, run_payload_analysis
from .research_analysis import deep_research_analysis


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

    market_source_label = "公开数据 / 用户输入 / seed 示例数据"
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
- 核心业务、产品或服务能否贡献新增收入。
- 经调整净利率或经营效率能否改善。
- 所在行业估值中枢和市场风险偏好能否改善。
- 公司现金流和分红、回购等股东回报政策。

## 9. 主要风险

- 公开数据存在延迟，需以交易所公告和公司最新披露为准。
- 若利润低于假设，目标市值所需估值倍数会明显抬升。
- 若行业估值中枢下移，目标股价区间需下修。
- 汇率变动会影响人民币财务数据折算后的港币估值。

## 10. 计算警告

{warning_text}

## 11. 免责声明

本报告基于公开信息、用户输入或 seed 示例数据生成，仅用于研究分析和系统开发验证，不构成任何投资建议。
"""
    return company.company_id, content


def _fmt_money_inline(value: float | None, currency: str) -> str:
    if value is None:
        return "缺失"
    return f"{money(value)} {currency}"


def _fmt_multiple_inline(value: float | None) -> str:
    return multiple(value)


def _fmt_pct_inline(value: float | None) -> str:
    return pct(value)


def _peer_table(peer: dict, currency: str) -> str:
    rows = [
        "| 公司 | 代码 | 市值 | PE | PS | 净利率 | 可比原因 | 备注 |",
        "|---|---|---:|---:|---:|---:|---|---|",
    ]
    target = peer["target"]
    rows.append(
        "| {name} | {ticker} | {cap} | {pe} | {ps} | {margin} | 目标公司 | 目标公司 |".format(
            name=target.get("company_name"),
            ticker=target.get("ticker"),
            cap=_fmt_money_inline(target.get("market_cap"), currency),
            pe=_fmt_multiple_inline(target.get("pe")),
            ps=_fmt_multiple_inline(target.get("ps")),
            margin=_fmt_pct_inline(target.get("net_margin")),
        )
    )
    for item in peer.get("peers", []):
        rows.append(
            "| {name} | {ticker} | {cap} | {pe} | {ps} | {margin} | {reason} | {note} |".format(
                name=item.get("company_name") or item.get("ticker"),
                ticker=item.get("ticker"),
                cap=_fmt_money_inline(item.get("market_cap"), item.get("currency") or currency),
                pe=_fmt_multiple_inline(item.get("pe")),
                ps=_fmt_multiple_inline(item.get("ps")),
                margin=_fmt_pct_inline(item.get("net_margin")),
                reason=item.get("reason", ""),
                note=item.get("error", ""),
            )
        )
    return "\n".join(rows)


def _bullet_lines(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- 暂无。"


def _segment_lines(segments: dict) -> str:
    rows = []
    for item in segments.get("segments", []):
        metrics = "、".join(item.get("monitoring_metrics", []))
        rows.append(f"- **{item['name']}**（{item.get('role', 'unknown')}）：{item.get('description', '')} 跟踪指标：{metrics}。")
    return "\n".join(rows) if rows else "- 暂无可靠业务分部数据。"


def _history_table(history: dict, currency: str) -> str:
    revenue = {row["as_of_date"]: row["value"] for row in history.get("revenue_history", [])}
    profit = {row["as_of_date"]: row["value"] for row in history.get("net_profit_history", [])}
    dates = sorted(set(revenue) | set(profit))
    if not dates:
        return "- 暂无多期财务数据。"
    rows = [
        "| 日期 | 收入 | 净利润 | 净利率 |",
        "|---|---:|---:|---:|",
    ]
    for item_date in dates[-5:]:
        revenue_value = revenue.get(item_date)
        profit_value = profit.get(item_date)
        rows.append(
            f"| {item_date} | {_fmt_money_inline(revenue_value, currency)} | {_fmt_money_inline(profit_value, currency)} | {_fmt_pct_inline(profit_value / revenue_value if revenue_value and profit_value is not None else None)} |"
        )
    return "\n".join(rows)


def _build_deep_report(result: dict, query: str | None = None, peer_payloads: list[dict] | None = None) -> tuple[str, str]:
    company = result["company"]
    market = result["market"]
    normalized = result["normalized_financials"]
    valuation = result["valuation"]
    scenarios = result["scenarios"]
    analysis = deep_research_analysis(result, query=query, peer_payloads=peer_payloads)
    peer = analysis["peer_comparison"]
    quality = analysis["financial_quality"]
    segments = analysis["business_segments"]
    drivers = analysis["drivers"]["drivers"]
    risks = analysis["risks"]["risks"]
    refutations = analysis["risks"]["refutation_tests"]
    questions = analysis["questions"]["questions"]

    scenario_rows = []
    for item in scenarios:
        a = item["assumptions"]
        scenario_rows.append(
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

    driver_lines = []
    for item in drivers:
        evidence = ("；".join(item.get("evidence", [])) or "待验证").rstrip("。.")
        metrics = "、".join(item.get("monitoring_metrics", []))
        driver_lines.append(f"- **{item['name']}**（{item['horizon']}）：{evidence}。跟踪指标：{metrics}。")

    risk_lines = [
        f"- **{item['risk']}**（{item['severity']}）：{item['impact']}。预警指标：{'、'.join(item['early_warning_metrics'])}。"
        for item in risks
    ]
    refutation_lines = [
        f"- 如果“{item['hypothesis']}”，则需要警惕：{item['would_be_wrong_if']}"
        for item in refutations
    ]
    question_lines = [
        f"- [{item['priority']}] {item['category']}：{item['question']}"
        for item in questions
    ]

    missing_segment = _bullet_lines(segments.get("missing_fields", []))
    segment_detail = _segment_lines(segments)
    history = quality.get("history", {})
    history_table = _history_table(history, company.currency)
    missing_items = []
    missing_items.extend(segments.get("missing_fields", []))
    if history.get("history_quality") == "missing":
        missing_items.append("financial_history")
    if not peer.get("peers"):
        missing_items.append("peer_group")
    missing_table = _bullet_lines(sorted(set(missing_items)))
    content = f"""# {company.company_name}深度投研估值分析报告

## 1. 核心结论

基于当前公开数据，{company.company_name}（{company.ticker}）当前市值约 **{_fmt_money_inline(market.market_cap, company.currency)}**，对应股价 **{_fmt_price(market.share_price, company.currency)}**。

当前市值隐含 PE 为 **{multiple(valuation.implied_pe)}**，隐含 PS 为 **{multiple(valuation.implied_ps)}**。2.0 深度分析的核心判断是：估值能否站住，需要同时看盈利质量、业务分部增长、同行估值位置和风险反证，而不能只看单一 PE/PS。

## 2. 公司与市场概览

- 公司：{company.company_name}
- 股票代码：{company.ticker}
- 上市地：{company.exchange}
- 币种：{company.currency}
- 行情日期：{market.trade_date}
- 当前股价：{_fmt_price(market.share_price, company.currency)}
- 当前市值：{_fmt_money_inline(market.market_cap, company.currency)}
- 总股本：{market.shares_outstanding / 100_000_000:.2f} 亿股
- 行情来源：{market.source_url}

## 3. 业务分部拆解

{segments['summary']}

业务分部初版：

{segment_detail}

当前缺失的关键分部字段：

{missing_segment}

需要人工进一步核验：最新年报或公告中的分部收入、分部利润、增长率、毛利率，以及管理层对核心业务和新业务的表述。

## 4. 财务质量分析

- 收入：{_fmt_money_inline(normalized.revenue, company.currency)}
- 净利润 / 经调整净利润：{_fmt_money_inline(quality.get('net_profit'), company.currency)}
- 净利率：{_fmt_pct_inline(quality.get('net_margin'))}
- 盈利收益率：{_fmt_pct_inline(quality.get('earnings_yield'))}
- PE：{multiple(quality.get('pe'))}
- PS：{multiple(quality.get('ps'))}

判断：{quality['summary']}

质量标记：{", ".join(quality.get("quality_flags", [])) or "暂无显著异常标记"}

多期财务趋势：

{history_table}

- 收入 CAGR：{_fmt_pct_inline(history.get('revenue_cagr'))}
- 净利润 CAGR：{_fmt_pct_inline(history.get('profit_cagr'))}
- 股本变化：{_fmt_pct_inline(history.get('share_count_change'))}

## 5. 增长驱动因素

{chr(10).join(driver_lines)}

## 6. 可比公司分析

同行组：**{peer['peer_group']['name']}**

{_peer_table(peer, company.currency)}

同行中位数：

- PE 中位数：{multiple(peer['median'].get('pe'))}
- PS 中位数：{multiple(peer['median'].get('ps'))}
- 净利率中位数：{pct(peer['median'].get('net_margin'))}

定位判断：{peer['positioning']['summary']}

## 7. 估值分析与交叉验证

- 目标市值 / 当前市值：{_fmt_money_inline(valuation.target_market_cap, company.currency)}
- 对应股价：{valuation.target_share_price:.2f} {company.currency}/股
- 隐含 PE：{multiple(valuation.implied_pe)}
- 隐含 PS：{multiple(valuation.implied_ps)}

不同 PE 假设下所需净利润：

{chr(10).join(f"- {pe}：{_fmt_money_inline(value, company.currency)}" for pe, value in valuation.required_net_profit_at_pe.items())}

## 8. 情景与敏感性分析

| 情景 | 收入增速 | 净利率 | PE | PS | 综合市值 | 对应股价 |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(scenario_rows)}

## 9. 风险与反证

核心风险：

{chr(10).join(risk_lines)}

反证测试：

{chr(10).join(refutation_lines)}

## 10. 待验证问题清单

{chr(10).join(question_lines)}

## 11. 数据来源与免责声明

- 行情数据：{market.source_url}
- 财务数据：{normalized.source_url}

关键缺失项：

{missing_table}

本报告基于公开信息、用户输入或 seed 示例数据生成，仅用于研究分析和系统开发验证，不构成任何投资建议。自动获取的公开数据可能存在延迟、缺失或口径差异，正式投研应以交易所公告和公司披露为准。
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


def generate_deep_markdown_report(company_id: str, target_market_cap: float | None = None, output_path: Path | None = None) -> Path:
    result = run_company_analysis(company_id, target_market_cap)
    company_id_out, content = _build_deep_report(result)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = output_path or REPORTS_DIR / f"{company_id_out}_deep_research_report.md"
    path.write_text(content, encoding="utf-8")
    return path


def generate_deep_markdown_report_from_payload(payload: dict, output_path: Path | None = None) -> Path:
    result = run_payload_analysis(payload)
    company_id, content = _build_deep_report(result, query=payload.get("query") or payload.get("company_name"), peer_payloads=payload.get("peer_payloads"))
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = output_path or REPORTS_DIR / f"{company_id}_deep_research_report.md"
    path.write_text(content, encoding="utf-8")
    return path
