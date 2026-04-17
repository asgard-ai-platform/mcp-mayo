# Changelog

All notable changes to mcp-mayo are documented here.

## [0.1.0] — 2026-04-17

### Added

- Initial release
- Foundation (FD) domain: 15 tools wrapping `/api/hrmlicense/ClientOut/*`
- Attendance (PT) domain: 8 tools wrapping `/api/hrmlicense/exportdata_*`
- Payroll (PY) domain: 5 tools wrapping `/api/hrmlicense/PYClientOut_*`
- 5 semantic tools composing the above (employee profile, org snapshot, attendance summary, today-default active search, monthly payroll report)
- Multi-domain REST connector with per-endpoint domain resolution
- `hrmlicense` header-based API key auth via single `MAYO_API_KEY` env var
- Date-format normalization helpers (`YYYY-MM-DD` ↔ `YYYY/MM/DD` / `YYYY/MM`)
- Connection test script covering all three backend domains
- E2E runner for every registered tool
- English and Traditional Chinese READMEs

### Verified (PRE environment)

- Connection test probes all three backends successfully with a valid `hrmlicense` key
- 24 / 33 tools return real data in E2E
- 9 tools labelled `KNOWN ISSUE` — 4 already flagged by MAYO as upstream failures (trip_history + three monthly insurance endpoints) and 5 tied to the `/ClientOut/ReportCenter/*` routes that currently 404 on the PRE Foundation backend
