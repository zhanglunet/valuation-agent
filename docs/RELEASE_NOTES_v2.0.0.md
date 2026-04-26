# Valuation Agent v2.0.0 Release Notes

Release date: 2026-04-26

## Highlights

- Formalized `--depth deep` as the main 2.0 research workflow.
- Users only need to provide a listed company name, abbreviation, or ticker.
- Added public data cache and `--refresh` support.
- Added peer comparison with curated peer reasons and median PE/PS/net margin.
- Added business segment profiles and missing-field tracking.
- Added multi-period financial history analysis, CAGR, margin trend, and share count change.
- Added configurable risk rules and refutation tests.
- Added dynamic scenario margins based on the company's actual profitability.

## Example

```bash
python3 -m valuation_agent.cli generate-report --query 腾讯 --depth deep
python3 -m valuation_agent.cli generate-report --query 腾讯 --depth deep --refresh
```

## Validation

- Unit tests: `22 passed`
- Real public-data smoke test: Tencent deep research report generated successfully.

## Notes

The system is for research assistance and product validation only. Public data may be delayed or use different reporting definitions, so formal investment research should verify exchange announcements, annual reports, and company filings.
