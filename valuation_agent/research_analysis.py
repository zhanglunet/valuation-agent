from __future__ import annotations

import json
from statistics import median

from .calculators import implied_pe, implied_ps
from .paths import CONFIG_DIR
from .public_data import enrich_payload_from_public_data


def _safe_div(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator


def _round(value: float | None, digits: int = 2) -> float | None:
    if value is None:
        return None
    return round(value, digits)


def _percentile(value: float | None, values: list[float]) -> float | None:
    if value is None or not values:
        return None
    below_or_equal = sum(1 for item in values if item <= value)
    return below_or_equal / len(values)


def _load_peer_groups() -> dict:
    path = CONFIG_DIR / "peer_groups.json"
    if not path.exists():
        return {"groups": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def _result_market_cap(result: dict) -> float | None:
    return result["market"].market_cap


def _result_revenue(result: dict) -> float | None:
    return result["normalized_financials"].revenue


def _result_profit(result: dict) -> float | None:
    normalized = result["normalized_financials"]
    return normalized.adjusted_net_profit or normalized.net_profit


def _result_ticker(result: dict) -> str:
    return result["company"].ticker


def _peer_record_from_payload(payload: dict) -> dict:
    enriched = enrich_payload_from_public_data(payload)
    market_cap = enriched.get("market_cap")
    revenue = enriched.get("revenue")
    profit = enriched.get("adjusted_net_profit") or enriched.get("net_profit")
    return {
        "ticker": enriched.get("ticker"),
        "company_name": enriched.get("company_name") or enriched.get("ticker"),
        "currency": enriched.get("currency"),
        "market_cap": market_cap,
        "revenue": revenue,
        "net_profit": profit,
        "net_margin": _safe_div(profit, revenue),
        "pe": implied_pe(market_cap, profit),
        "ps": implied_ps(market_cap, revenue),
        "source_url": enriched.get("market_source_url") or enriched.get("financial_source_url"),
    }


def select_peer_group(result: dict, query: str | None = None) -> dict:
    groups = _load_peer_groups().get("groups", {})
    ticker = _result_ticker(result)
    company_name = result["company"].company_name
    candidates = {ticker.lower(), company_name.lower()}
    if query:
        candidates.add(query.lower())

    for key, group in groups.items():
        tickers = {item.lower() for item in group.get("tickers", [])}
        aliases = {item.lower() for item in group.get("aliases", [])}
        if ticker.lower() in tickers or candidates.intersection(aliases):
            return {"key": key, **group}

    return {
        "key": "custom",
        "name": "未配置同行池",
        "tickers": [],
        "aliases": [],
    }


def peer_comparison(result: dict, query: str | None = None, peer_payloads: list[dict] | None = None, max_peers: int = 5) -> dict:
    target_market_cap = _result_market_cap(result)
    target_revenue = _result_revenue(result)
    target_profit = _result_profit(result)
    target = {
        "ticker": _result_ticker(result),
        "company_name": result["company"].company_name,
        "currency": result["company"].currency,
        "market_cap": target_market_cap,
        "revenue": target_revenue,
        "net_profit": target_profit,
        "net_margin": _safe_div(target_profit, target_revenue),
        "pe": implied_pe(target_market_cap, target_profit),
        "ps": implied_ps(target_market_cap, target_revenue),
    }

    group = select_peer_group(result, query=query)
    peer_records: list[dict] = []

    if peer_payloads is not None:
        peer_records = [_peer_record_from_payload(payload) for payload in peer_payloads]
    else:
        for ticker in group.get("tickers", [])[: max_peers + 1]:
            if ticker == target["ticker"]:
                continue
            try:
                peer_records.append(_peer_record_from_payload({"ticker": ticker}))
            except Exception as exc:  # External data is best-effort in 2.0.
                peer_records.append({"ticker": ticker, "company_name": ticker, "error": str(exc)})
            if len(peer_records) >= max_peers:
                break

    valid_pe = [item["pe"] for item in peer_records if isinstance(item.get("pe"), (int, float))]
    valid_ps = [item["ps"] for item in peer_records if isinstance(item.get("ps"), (int, float))]
    valid_margin = [item["net_margin"] for item in peer_records if isinstance(item.get("net_margin"), (int, float))]

    medians = {
        "pe": median(valid_pe) if valid_pe else None,
        "ps": median(valid_ps) if valid_ps else None,
        "net_margin": median(valid_margin) if valid_margin else None,
    }

    positioning = {
        "pe_percentile": _percentile(target["pe"], valid_pe),
        "ps_percentile": _percentile(target["ps"], valid_ps),
        "summary": _peer_positioning_summary(target, medians, peer_records),
    }

    return {
        "peer_group": {"key": group["key"], "name": group["name"]},
        "target": target,
        "peers": peer_records,
        "median": medians,
        "positioning": positioning,
    }


def _peer_positioning_summary(target: dict, medians: dict, peers: list[dict]) -> str:
    if not peers:
        return "当前未配置有效同行池，无法给出可靠可比公司结论。"

    observations = []
    if target.get("pe") is not None and medians.get("pe") is not None:
        if target["pe"] > medians["pe"] * 1.15:
            observations.append("目标公司 PE 高于同行中位数，需要由更高增长或更强盈利质量支撑。")
        elif target["pe"] < medians["pe"] * 0.85:
            observations.append("目标公司 PE 低于同行中位数，可能反映低估或市场对风险定价。")
        else:
            observations.append("目标公司 PE 接近同行中位数。")
    if target.get("ps") is not None and medians.get("ps") is not None:
        if target["ps"] > medians["ps"] * 1.15:
            observations.append("目标公司 PS 高于同行中位数，需关注收入增长和利润率是否匹配。")
        elif target["ps"] < medians["ps"] * 0.85:
            observations.append("目标公司 PS 低于同行中位数，需判断是否存在业务结构或增长折价。")
        else:
            observations.append("目标公司 PS 接近同行中位数。")
    return " ".join(observations) if observations else "同行数据不完整，暂无法形成倍数定位结论。"


def financial_quality(result: dict) -> dict:
    revenue = _result_revenue(result)
    profit = _result_profit(result)
    market_cap = _result_market_cap(result)
    net_margin = _safe_div(profit, revenue)
    earnings_yield = _safe_div(profit, market_cap)
    ps = implied_ps(market_cap, revenue)
    pe = implied_pe(market_cap, profit)

    flags = []
    if revenue is None:
        flags.append("revenue_missing")
    if profit is None:
        flags.append("profit_missing")
    if net_margin is not None:
        if net_margin < 0:
            flags.append("loss_making")
        elif net_margin < 0.05:
            flags.append("thin_margin")
        elif net_margin > 0.25:
            flags.append("high_margin")
    if pe is not None and pe > 40:
        flags.append("high_pe_requires_growth")
    if ps is not None and ps > 10:
        flags.append("high_ps_requires_margin_or_growth")

    return {
        "revenue": revenue,
        "net_profit": profit,
        "net_margin": net_margin,
        "earnings_yield": earnings_yield,
        "pe": pe,
        "ps": ps,
        "quality_flags": flags,
        "summary": _financial_quality_summary(net_margin, pe, ps, flags),
    }


def _financial_quality_summary(net_margin: float | None, pe: float | None, ps: float | None, flags: list[str]) -> str:
    parts = []
    if net_margin is None:
        parts.append("缺少利润或收入数据，盈利质量判断受限。")
    elif net_margin >= 0.2:
        parts.append("净利率较高，盈利质量对估值有一定支撑。")
    elif net_margin >= 0.08:
        parts.append("净利率处于中等水平，需要结合增长和同行估值判断。")
    elif net_margin >= 0:
        parts.append("净利率偏薄，估值需要更多依赖收入增长或未来利润率改善。")
    else:
        parts.append("当前亏损，PE 估值参考意义有限。")

    if "high_pe_requires_growth" in flags:
        parts.append("当前 PE 偏高，需要较强增长或利润率改善兑现。")
    if "high_ps_requires_margin_or_growth" in flags:
        parts.append("当前 PS 偏高，需要收入质量和利润转化能力支撑。")
    return "".join(parts)


def business_segment_analysis(result: dict) -> dict:
    company = result["company"]
    return {
        "segments": [],
        "segment_quality": "missing",
        "summary": "当前公开摘要接口未提供可靠业务分部数据，2.0 报告仅能提示需要从年报、公告或公司官网进一步验证。",
        "missing_fields": ["segment_revenue", "segment_growth", "segment_margin"],
        "industry_context": company.industry,
    }


def driver_analysis(result: dict, quality: dict, peer: dict) -> dict:
    drivers = []
    if quality.get("net_margin") is not None:
        drivers.append(
            {
                "name": "盈利能力变化",
                "horizon": "short_to_medium_term",
                "evidence": [f"当前净利率约 {_round(quality['net_margin'] * 100, 1)}%"],
                "monitoring_metrics": ["net_margin", "operating_margin"],
                "confidence": "medium",
            }
        )
    drivers.append(
        {
            "name": "收入增长持续性",
            "horizon": "medium_term",
            "evidence": ["当前报告已获取最近公开收入摘要，但仍需要多期增长率验证"],
            "monitoring_metrics": ["revenue_growth", "segment_revenue_growth"],
            "confidence": "medium",
        }
    )
    if peer.get("positioning", {}).get("summary"):
        drivers.append(
            {
                "name": "相对估值修复或压缩",
                "horizon": "short_to_medium_term",
                "evidence": [peer["positioning"]["summary"]],
                "monitoring_metrics": ["peer_pe_median", "peer_ps_median"],
                "confidence": "medium",
            }
        )
    return {"drivers": drivers}


def risk_and_refutation(result: dict, quality: dict, peer: dict) -> dict:
    risks = [
        {
            "risk": "公开数据口径差异或延迟",
            "impact": "自动估值倍数可能与交易所公告口径不一致",
            "early_warning_metrics": ["filing_update", "restatement"],
            "severity": "medium",
        },
        {
            "risk": "收入增长放缓",
            "impact": "PS 和 PE 估值同时承压",
            "early_warning_metrics": ["revenue_growth", "segment_revenue_growth"],
            "severity": "high",
        },
        {
            "risk": "利润率下滑",
            "impact": "隐含 PE 抬升，目标市值支撑减弱",
            "early_warning_metrics": ["net_margin", "gross_margin", "expense_ratio"],
            "severity": "high",
        },
    ]
    if quality.get("pe") is not None and quality["pe"] > 35:
        risks.append(
            {
                "risk": "估值倍数偏高",
                "impact": "一旦增长不及预期，估值回撤可能放大",
                "early_warning_metrics": ["forward_pe", "revenue_growth"],
                "severity": "high",
            }
        )

    refutation_tests = [
        {
            "hypothesis": "当前估值可以由盈利能力支撑",
            "would_be_wrong_if": "未来 12 个月净利率下滑且收入增速低于同行中位数。",
        },
        {
            "hypothesis": "相对估值合理",
            "would_be_wrong_if": "目标公司 PE/PS 高于同行中位数，但增长率和利润率没有明显优势。",
        },
    ]
    if peer.get("peer_group", {}).get("key") == "custom":
        refutation_tests.append(
            {
                "hypothesis": "同行比较充分",
                "would_be_wrong_if": "当前同行池缺失或弱相关，需要人工补充真正可比公司。",
            }
        )
    return {"risks": risks, "refutation_tests": refutation_tests}


def question_list(result: dict, segment: dict, peer: dict, quality: dict) -> dict:
    questions = []
    if segment.get("segment_quality") == "missing":
        questions.append(
            {
                "category": "business_segment",
                "question": "最新年度各业务分部收入、增速和利润率分别是多少？",
                "priority": "high",
            }
        )
    if peer.get("peer_group", {}).get("key") == "custom" or not peer.get("peers"):
        questions.append(
            {
                "category": "peer_comparison",
                "question": "应选择哪些业务模式、区域和规模最接近的上市公司作为可比公司？",
                "priority": "high",
            }
        )
    if "revenue_missing" in quality.get("quality_flags", []) or "profit_missing" in quality.get("quality_flags", []):
        questions.append(
            {
                "category": "financial_quality",
                "question": "最新收入、净利润和调整后利润的公司披露口径是什么？",
                "priority": "high",
            }
        )
    questions.append(
        {
            "category": "valuation_assumption",
            "question": "当前估值倍数应使用历史中位数、同行中位数还是未来盈利预测作为锚？",
            "priority": "medium",
        }
    )
    return {"questions": questions}


def deep_research_analysis(result: dict, query: str | None = None, peer_payloads: list[dict] | None = None) -> dict:
    peer = peer_comparison(result, query=query, peer_payloads=peer_payloads)
    quality = financial_quality(result)
    segment = business_segment_analysis(result)
    drivers = driver_analysis(result, quality, peer)
    risks = risk_and_refutation(result, quality, peer)
    questions = question_list(result, segment, peer, quality)
    return {
        "peer_comparison": peer,
        "financial_quality": quality,
        "business_segments": segment,
        "drivers": drivers,
        "risks": risks,
        "questions": questions,
    }
