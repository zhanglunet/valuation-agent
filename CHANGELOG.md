# Changelog

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
