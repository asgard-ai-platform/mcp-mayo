# mcp-mayo — Design Spec

**Date:** 2026-04-17
**Status:** Approved
**Package name:** `mcp-mayo`

## Overview

`mcp-mayo` is an MCP (Model Context Protocol) server that wraps the MAYO Apollo HRM SaaS API (鼎恒數位 MAYO HR). It exposes people / attendance / payroll data as AI-callable tools via stdio JSON-RPC.

The reference material (Postman collection + Chinese DOCX specs) describes ~28 endpoints across three backend domains.

## Approach

**Layer 1 (Plan A — full coverage):** 28 thin wrappers, one per API endpoint, split across three tool modules by domain.

**Layer 2 (Plan C — semantic aggregations):** 5–6 high-level tools that compose Layer 1 calls into AI-friendly operations (e.g. one `get_employee_profile` call aggregates PA + Working + Education).

Both layers are exposed as MCP tools. Layer 2 is recommended for most AI use cases; Layer 1 is available when finer-grained control is needed.

## Backend topology

Three separate base URLs (PRE / test environment — production not used):

| Domain | Base URL | Style | Endpoints |
|---|---|---|---|
| Foundation (FD) | `https://pre-linkup-be.mayohr.com` | GET (+1 POST) | 15 |
| Attendance (PT) | `https://pre-pt-be.mayohr.com` | POST + JSON body | 8 |
| Payroll (PY) | `https://pre-py-be.mayohr.com` | GET | 5 |

## Auth

- **Scheme:** API key via HTTP header
- **Header name:** `hrmlicense` (literal — not `X-API-Key`)
- **Env var:** `MAYO_API_KEY`
- Same key used across all three domains

## Template decisions

| Template asset | Action |
|---|---|
| `auth/api_key.py` | Keep — modify for `hrmlicense` header + `MAYO_API_KEY` |
| `auth/bearer.py` / `oauth2.py` / `none.py` | Delete |
| `connectors/rest_client.py` | Keep — extend `get_url()` for multi-domain |
| `connectors/rss_client.py` / `scraper_client.py` / `mqtt_client.py` / `graphql_client.py` | Delete |
| `config/settings.py` | Rewrite: `BASE_URLS` dict keyed by domain; `ENDPOINTS` maps key → (domain, path) |
| `tools/sample_tools.py` | Delete, replace with 4 new tool modules |
| `scripts/init.py` | Keep (already served its purpose) |
| `pyproject.toml` | Rewrite metadata for `mcp-mayo` |

## File structure (post-implementation)

```
mcp-mayo/
├── app.py                       FastMCP("mcp-mayo")
├── mcp_server.py                imports 4 tool modules
├── pyproject.toml               mcp-mayo metadata + hatch build
├── .env.example                 MAYO_API_KEY
├── .mcp.json                    mcp-mayo stdio config
├── CLAUDE.md                    updated architecture diagram
├── CONTRIBUTING.md              updated with MAYO-specific examples
├── README.md / README.zh-TW.md  rewritten for MAYO
├── CHANGELOG.md                 0.1.0 initial release
├── auth/
│   ├── __init__.py
│   └── api_key.py               HEADER_NAME="hrmlicense"; ENV_VAR_NAME="MAYO_API_KEY"
├── config/
│   ├── __init__.py
│   └── settings.py              BASE_URLS, ENDPOINTS (keyed), helpers
├── connectors/
│   ├── __init__.py
│   └── rest_client.py           multi-domain URL resolution
├── tools/
│   ├── __init__.py
│   ├── foundation_tools.py      15 FD wrappers
│   ├── attendance_tools.py      8 PT wrappers
│   ├── payroll_tools.py         5 PY wrappers
│   └── semantic_tools.py        5 high-level aggregations
├── tests/
│   └── test_all_tools.py        E2E for all 33 tools
└── scripts/
    └── auth/
        └── test_connection.py   ping FD/PT/PY with MAYO_API_KEY
```

## Layer 1 — tool inventory (28)

### `tools/foundation_tools.py` (15)

| Tool | Endpoint | Method | Key params |
|---|---|---|---|
| `list_active_employees` | `/ClientOut/ReportCenter/ActiveEmployeeData` | GET | `effective_date`, `dept_code?` |
| `list_resigned_employees` | `/ClientOut/ReportCenter/ResignAndLeaveData` | GET | `start_date`, `end_date`, `dept_code?` |
| `get_organization_tree` | `/ClientOut/ReportCenter/OrgData` | GET | `query_date`, `dept_code?`, `include_ineffective?` |
| `export_org_and_employees` | `/ClientOut/OMandPA` | GET | `language` |
| `export_employees` | `/ClientOut/Employee` | GET | `language` |
| `export_departments` | `/ClientOut/Department` | GET | `language` |
| `export_employee_changes` | `/ClientOut/EmployeeChangeContent` | GET | `start_date`, `end_date`, `page_number`, `page_size`, `language` |
| `export_org_changes` | `/ClientOut/OrgChangeContent` | GET | `start_date`, `end_date`, `page_number`, `page_size`, `language` |
| `export_expatriations` | `/ClientOut/Expatriation` | GET | `language` |
| `export_organization_full` | `/ClientOut/OM` | GET | `language` |
| `export_employees_full` | `/ClientOut/PA` | GET | `language`, `employee_number?`, `department_code?`, many optional |
| `export_working_history` | `/ClientOut/Working` | GET | — |
| `export_education_history` | `/ClientOut/Education` | GET | — |
| `export_pa_options` | `/ClientOut/PaOptions` | POST | `language` |
| `export_company_custom_fields` | `/ClientOut/CompanyCustomFields` | GET | `language` |

### `tools/attendance_tools.py` (8)

| Tool | Endpoint | Method | Key params (JSON body) |
|---|---|---|---|
| `get_attendance_rules` | `/exportdata_attendance_rule` | POST | `searchDate` |
| `get_attendance_history` | `/exportdata_attendance_history` | POST | `startDate`, `endDate` |
| `get_attendance_abnormal` | `/exportdata_attendance_abnormal` | POST | `startDate`, `endDate` |
| `get_forgot_checkin_records` | `/exportdata_forgot_checkin_record` | POST | `startDate`, `endDate` |
| `get_leave_history` | `/exportdata_leave_historyV2` | POST | `startDate`, `endDate` |
| `get_employee_calendar` | `/exportdata_employee_calendar` | POST | `startDate`, `endDate` |
| `get_overtime_records` | `/exportdata_overtime_record` | POST | `startDate`, `endDate` |
| `get_trip_history` | `/exportdata_trip_history` | POST | `startDate`, `endDate` — **KNOWN ISSUE** |

### `tools/payroll_tools.py` (5)

| Tool | Endpoint | Method | Key params |
|---|---|---|---|
| `get_monthly_labor_insurance` | `/PYClientOut_Insurance/MonthLabor` | GET | `search_date` (YYYY/MM/DD), `insurance_no`, `language` — **KNOWN ISSUE** |
| `get_monthly_nhi` | `/PYClientOut_Insurance/MonthNHI` | GET | same — **KNOWN ISSUE** |
| `get_monthly_labor_pension` | `/PYClientOut_Insurance/MonthLaborPension` | GET | same — **KNOWN ISSUE** |
| `get_salary_insurance_detail` | `/PYClientOut_Salary/SalaryInsurance` | GET | `search_date`, `dept_code?`, `employee_number?`, `is_have_retention?` |
| `get_salary_bonus_list` | `/PYClientOut_Salary/SalaryBonusList` | GET | `start_month` (YYYY/MM), `end_month` (YYYY/MM) |

Tools targeting `[報錯]` endpoints will include `**KNOWN ISSUE:**` in their docstring so the AI knows it may fail server-side.

## Layer 2 — semantic tools (5)

`tools/semantic_tools.py`:

1. **`get_employee_profile(employee_number, language="zh-tw")`** — aggregates `/PA` + `/Working` + `/Education` filtered to one employee, returns single merged profile
2. **`get_organization_snapshot(as_of_date=None, language="zh-tw")`** — wraps `/OMandPA` with ISO-date input; if `as_of_date` omitted, uses today
3. **`get_attendance_summary(start_date, end_date, include_abnormal=True, include_overtime=True)`** — fans out to `/attendance_history` + optional `/abnormal` + `/overtime`, returns consolidated summary
4. **`search_active_employees(as_of_date=None, dept_code=None)`** — cleaner wrapper over `/ActiveEmployeeData` with ISO dates and today default
5. **`get_monthly_payroll_report(year_month)`** — accepts `YYYY-MM`, calls `/SalaryBonusList` with correct `YYYY/MM` format under the hood

## Date handling

All tools accept ISO `YYYY-MM-DD` from callers. Internal helpers convert to the API's expected format:

- `_iso_to_slash_date("2025-09-01")` → `"2025/09/01"` for PY Insurance
- `_iso_to_year_month("2025-09-01")` → `"2025/09"` for SalaryBonusList

## Error handling

- Reuse `ServiceAPIError` → rename to `MayoAPIError`
- Non-2xx responses bubble up with status + body
- Transient (timeout / connection) errors retry with exponential backoff (already in `rest_client.py`)
- Known-issue endpoints return upstream error verbatim — don't swallow

## Optional field handling

MAYO endpoints accept `null` / omitted query params for optional filters. Pattern B applies: only include a parameter in the dict if it's non-None. Use the standard `_val()` helper from the skill's Common Pitfalls guide to resolve `FieldInfo` defaults for direct calls.

## Env vars

Single variable:
```
MAYO_API_KEY=<hrmlicense-token-value>
```

The PRE environment key from the Postman collection is used for development and CI/E2E testing.

## Dependencies

No new dependencies beyond the template baseline:
- `requests>=2.31.0`
- `mcp>=1.0.0`
