# MCP Mayo

[![PyPI version](https://img.shields.io/pypi/v/mcp-mayo)](https://pypi.org/project/mcp-mayo/)
[![Python](https://img.shields.io/pypi/pyversions/mcp-mayo)](https://pypi.org/project/mcp-mayo/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-compatible-blue)](https://modelcontextprotocol.io/)
[![GitHub stars](https://img.shields.io/github/stars/asgard-ai-platform/mcp-mayo)](https://github.com/asgard-ai-platform/mcp-mayo/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/asgard-ai-platform/mcp-mayo)](https://github.com/asgard-ai-platform/mcp-mayo/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/asgard-ai-platform/mcp-mayo)](https://github.com/asgard-ai-platform/mcp-mayo/commits/main)

MCP Server for [MAYO Apollo](https://www.mayohr.com/) — exposes the HRM platform's Foundation (人事), Attendance (差勤), and Payroll (薪資勞健保) APIs as AI-callable tools via the [Model Context Protocol](https://modelcontextprotocol.io/).

[繁體中文](README.zh-TW.md) · Part of the [Asgard AI Platform](https://github.com/asgard-ai-platform) open-source ecosystem.

## What This Does

- **33 tools** — 28 thin wrappers around every MAYO Apollo endpoint plus 5 semantic compositions
- **Three backend domains** — Foundation, Attendance, Payroll — served from one MCP server with a single `hrmlicense` API key
- **Date-format normalization** — callers use ISO `YYYY-MM-DD` / `YYYY-MM`; the server converts to each endpoint's expected format internally
- **Semantic aggregations** — one-call helpers like `get_employee_profile`, `get_organization_snapshot_as_of`, `get_attendance_summary`
- **Typed with Pydantic** — every parameter has a description the AI can see
- **E2E test runner** — exercises every registered tool against the live PRE environment

## Quick Start

### Install

Requires Python 3.10+, `uv` (recommended) or `pip`, and a MAYO-issued `hrmlicense` API key with read access to the FD / PT / PY backends you plan to call.

From PyPI (once published):

```bash
uv add mcp-mayo
# or
pip install mcp-mayo
```

From source (current state):

```bash
git clone https://github.com/asgard-ai-platform/mcp-mayo.git
cd mcp-mayo
uv sync
cp .env.example .env
# Edit .env and set MAYO_API_KEY
```

Set your API key:

```bash
export MAYO_API_KEY=your_hrmlicense_token
```

| Env var | Required | Purpose |
|---|---|---|
| `MAYO_API_KEY` | Yes | The token value placed on the `hrmlicense` header; authenticates Foundation, Attendance, and Payroll in a single credential |

Run the server directly to verify it starts:

```bash
uv run --env-file .env python mcp_server.py
```

### Use with Claude Code

Add the server via the Claude CLI:

```bash
claude mcp add --transport stdio mayo -e MAYO_API_KEY=your_hrmlicense_token -- uvx mcp-mayo
```

Or, when working from a local clone, `.mcp.json`:

```json
{
  "mcpServers": {
    "mayo": {
      "command": "uv",
      "args": ["run", "mcp-mayo"],
      "cwd": "${PWD}",
      "env": {
        "PYTHONPATH": "${PWD}",
        "MAYO_API_KEY": "${MAYO_API_KEY}"
      }
    }
  }
}
```

### Use with Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mayo": {
      "command": "uvx",
      "args": ["mcp-mayo"],
      "env": {
        "MAYO_API_KEY": "your_hrmlicense_token"
      }
    }
  }
}
```

### Use with other MCP clients

Cursor and any other MCP-compatible client: point it at `uvx mcp-mayo` with `MAYO_API_KEY` in its environment.

## Tools (33)

### Semantic (5) — recommended for AI use

| Tool | What it does |
|---|---|
| `get_employee_profile` | One employee's PA + work history + education in a single call |
| `get_organization_snapshot_as_of` | Org tree + active headcount for a date |
| `get_attendance_summary` | History + abnormal + overtime + leave fan-out over a range |
| `search_active_employees` | `list_active_employees` with today as default |
| `get_monthly_payroll_report` | Single-month salary/bonus roster using ISO `YYYY-MM` |

### Foundation (FD) — 15

`list_active_employees` ¹, `list_resigned_employees` ¹, `get_organization_tree` ¹, `export_organization_with_employees`, `export_employees`, `export_departments`, `export_organization_full`, `export_employees_full`, `export_expatriations`, `export_working_history`, `export_education_history`, `export_employee_changes`, `export_organization_changes`, `export_pa_options`, `export_company_custom_fields`

### Attendance (PT) — 8

`get_attendance_rules`, `get_attendance_history`, `get_attendance_abnormal`, `get_forgot_checkin_records`, `get_leave_history`, `get_employee_calendar`, `get_overtime_records`, `get_trip_history` ²

### Payroll (PY) — 5

`get_monthly_labor_insurance` ², `get_monthly_nhi` ², `get_monthly_labor_pension` ², `get_salary_insurance_detail`, `get_salary_bonus_list`

¹ The three `/ClientOut/ReportCenter/*` routes (plus the two semantic wrappers `search_active_employees` and `get_organization_snapshot_as_of` that depend on them) currently return 404 on the PRE Foundation backend. The tools stay exposed so they work the moment MAYO redeploys these endpoints.

² Flagged as failing upstream in MAYO's own Postman collection. Same story — tool stays, docstring carries a `KNOWN ISSUE` note.

## Usage Examples

### "Who was active in department C030010 yesterday?"

> **You:** 昨天 C030010 部門還在職的人列一下

**AI calls:**

```
search_active_employees(
  dept_code = "C030010",
)
```

**Result:** `SUCCESS` — returns the active-employee list from the Foundation backend with today as the effective date.

### "Give me A00384's full profile"

> **You:** 給我員編 A00384 的完整資料

**AI calls:**

```
get_employee_profile(
  employee_number = "A00384",
)
```

**Result:** `SUCCESS` — aggregates `/PA`, `/Working`, and `/Education`, locally filtered to A00384.

### "Attendance picture for the first week of September"

> **You:** 9/1 到 9/7 的出勤統計，含異常跟加班

**AI calls:**

```
get_attendance_summary(
  start_date = "2025-09-01",
  end_date   = "2025-09-07",
)
```

**Result:** `SUCCESS` — returns history, abnormal, overtime, and leave sections for the range.

### "January salary roster"

> **You:** 2025-01 的薪資發放清冊

**AI calls:**

```
get_monthly_payroll_report(
  year_month = "2025-01",
)
```

**Result:** `SUCCESS` — converts to `2025/01` under the hood and calls SalaryBonusList.

## Architecture

```
stdio (JSON-RPC 2.0)
  → mcp_server.py                 entry point; imports tool modules
    → app.py                      FastMCP("mcp-mayo") singleton
      → tools/                    @mcp.tool() decorated functions
          foundation_tools.py       15 FD wrappers
          attendance_tools.py       8 PT wrappers
          payroll_tools.py          5 PY wrappers
          semantic_tools.py         5 high-level compositions
        → connectors/rest_client.py  retry + multi-domain URL resolution
          → auth/api_key.py          builds {"hrmlicense": <MAYO_API_KEY>}
            → config/settings.py     BASE_URLS + ENDPOINTS (keyed by domain)
```

## Testing

```bash
uv run --env-file .env python scripts/auth/test_connection.py   # probes FD / PT / PY
uv run --env-file .env python tests/test_all_tools.py           # runs every tool
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).
