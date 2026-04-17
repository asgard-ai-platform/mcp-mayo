# mcp-mayo

## Overview

MCP Server that wraps the MAYO Apollo HRM platform (Foundation, Attendance, Payroll) as AI-callable tools over stdio JSON-RPC 2.0. Part of the Asgard open-source ecosystem.

## Setup

```bash
uv sync
cp .env.example .env   # then set MAYO_API_KEY
```

## Run

```bash
uv run --env-file .env python mcp_server.py
```

## Test

```bash
uv run --env-file .env python scripts/auth/test_connection.py   # probes FD / PT / PY
uv run --env-file .env python tests/test_all_tools.py           # every registered tool
```

## Architecture

```
stdio (JSON-RPC 2.0)
  → mcp_server.py                     entry point; imports tool modules
    → app.py                          FastMCP("mcp-mayo") singleton
      → tools/
          foundation_tools.py           15 FD wrappers (pre-linkup-be)
          attendance_tools.py           8 PT wrappers (pre-pt-be)
          payroll_tools.py              5 PY wrappers (pre-py-be)
          semantic_tools.py             5 higher-level compositions
        → connectors/rest_client.py     retry + MayoAPIError
          → auth/api_key.py             hrmlicense header from MAYO_API_KEY
            → config/settings.py        BASE_URLS + ENDPOINTS (keyed by domain)
```

### Key patterns

- **Single auth credential** — `MAYO_API_KEY` is sent on the `hrmlicense` header for all three domains
- **Endpoint keys carry their domain** — `ENDPOINTS[key] = (domain, path)` so `get_url` resolves to the right base URL without tool code needing to know
- **Date conversion in the tool layer** — callers pass ISO, `tools/_util.py` converts to MAYO's format before the connector fires
- **Two-layer tool surface** — thin raw wrappers for completeness + semantic composites for AI ergonomics
- **Known-broken upstream endpoints stay exposed** — wrappers are marked `KNOWN ISSUE:` in docstrings so they work as soon as MAYO fixes the server

### Adding a new tool

1. Register the endpoint in `config/settings.py` under `ENDPOINTS` with its domain
2. Add the tool function to the matching `tools/*_tools.py`, decorated with `@mcp.tool()` and typed via Pydantic `Field()`
3. Use `_val()` from `tools/_util.py` for every optional parameter to avoid the FieldInfo pitfall
4. Route through `api_get` / `api_post` from `connectors/rest_client.py` — never call `requests` directly
5. If you created a brand new tool module, add its import to `mcp_server.py`
6. Add an E2E case to `tests/test_all_tools.py`

### Code conventions

- English for code, docstrings, tool descriptions, and commit messages
- Tools return `dict`
- `_val()` + `filter_none()` for optional params
- `iso_to_slash_date` / `iso_to_year_month` when an endpoint needs slash-separated dates
- No direct `requests` calls in tools
