from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path
from typing import TypeVar

from .paths import CONFIG_DIR, SEED_DIR
from .schemas import CompanyProfile, FinancialStatement, MarketSnapshot

T = TypeVar("T")


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _pick_dataclass_fields(cls: type[T], data: dict) -> dict:
    names = {field.name for field in fields(cls)}
    return {key: value for key, value in data.items() if key in names}


def load_company(company_id: str) -> CompanyProfile:
    data = load_json(CONFIG_DIR / "companies.json")
    companies = data.get("companies", {})
    if company_id not in companies:
        raise KeyError(f"unknown company_id: {company_id}")
    return CompanyProfile(**_pick_dataclass_fields(CompanyProfile, companies[company_id]))


def load_assumptions() -> dict:
    return load_json(CONFIG_DIR / "assumptions.json")


def load_seed(company_id: str) -> dict:
    path = SEED_DIR / f"{company_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"seed data not found: {path}")
    return load_json(path)


def load_market_snapshot(company_id: str) -> MarketSnapshot:
    seed = load_seed(company_id)
    return MarketSnapshot(**_pick_dataclass_fields(MarketSnapshot, seed["market_snapshot"]))


def load_financial_statement(company_id: str) -> FinancialStatement:
    seed = load_seed(company_id)
    return FinancialStatement(**_pick_dataclass_fields(FinancialStatement, seed["financial_statement"]))
