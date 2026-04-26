# Changelog

## v2.0.0 - 2026-04-26

### Added

- Added public data JSON cache under `data/raw/` with `--refresh` support.
- Added business segment profiles for representative listed companies.
- Added configurable risk rules.
- Added peer comparison reasons and cleaner peer median filtering.
- Added multi-period financial history analysis, CAGR, margin trend, and share count change.
- Added deep report sections for business segments, financial trend tables, missing items, peer reasons, and risk/refutation checks.
- Added dynamic scenario margins based on the company's current profitability.
- Added tests for cache, business profiles, financial history, risk rules, and dynamic scenarios.

### Changed

- Promoted deep research mode from beta to the 2.0 formal implementation.
- Updated Skills and CLI docs for `depth=deep` and `refresh`.
- Improved `scenario-analysis-skill` to use the same dynamic scenario logic as the core pipeline.

### Known Limitations

- Business segment details are profile-based and still require annual report verification.
- Peer groups are curated and should be expanded by industry.
- Public data depends on Yahoo Finance endpoints and should be verified against official filings.

## v2.0.0-beta.1 - 2026-04-26

### Added

- Added `--depth deep` deep research report mode.
- Added `config/peer_groups.json`.
- Added `valuation_agent/research_analysis.py`.
- Added first working peer comparison analysis.
- Added financial quality analysis.
- Added growth driver analysis.
- Added risk and refutation analysis.
- Added research question list generation.
- Added deep research Markdown report template.
- Added tests for research analysis.

### Changed

- Upgraded `peer-comparison-skill` from placeholder to working beta implementation.
- Upgraded `research-report-skill` to support `depth=deep`.
- Updated version to `2.0.0-beta.1`.

### Known Limitations

- Business segment analysis is still a missing-data prompt rather than full extraction.
- Peer groups are manually curated and limited.
- Public data depends on Yahoo Finance endpoints and should be verified against official filings.

## v1.0.0 - 2026-04-26

### Added

- First formal release of Valuation Agent.
- Company name / alias / ticker based lookup.
- Chinese alias mapping via `config/company_aliases.json`.
- Public market data lookup using Yahoo Finance public endpoints.
- Market snapshot extraction.
- Financial summary extraction.
- PE / PS valuation.
- Market-cap-to-share-price calculation.
- Required net profit by target PE.
- Bear / base / bull scenario analysis.
- Markdown report generation.
- Hermes Skills wrappers.
- Feishu / Hermes installation documentation.
- Unit and integration tests.

### Known Limitations

- Peer comparison is still a placeholder.
- Business segment analysis is not implemented.
- Financial quality analysis is not implemented.
- DCF and EV/EBITDA are not implemented.
- DOCX / PPTX export is not implemented.
