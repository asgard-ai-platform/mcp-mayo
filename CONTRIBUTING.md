# Contributing to mcp-mayo

Thanks for contributing! This document covers setup, conventions, and how to add new tools.

## Setup

```bash
git clone https://github.com/asgard-ai-platform/mcp-mayo.git
cd mcp-mayo
uv sync
cp .env.example .env
# Set MAYO_API_KEY to a valid hrmlicense token
```

## Adding a new tool

1. **Pick a module** in `tools/`:
   - `foundation_tools.py` for Foundation (FD) endpoints
   - `attendance_tools.py` for Attendance (PT) endpoints
   - `payroll_tools.py` for Payroll (PY) endpoints
   - `semantic_tools.py` for higher-level compositions that fan out across the above

2. **Register the endpoint** in `config/settings.py`:

   ```python
   ENDPOINTS = {
       # ... existing
       "my_new_endpoint": ("foundation", "/api/hrmlicense/ClientOut/MyNewEndpoint"),
   }
   ```

3. **Write the tool**:

   ```python
   from app import mcp
   from pydantic import Field
   from connectors.rest_client import api_get
   from tools._util import _val, filter_none

   @mcp.tool()
   def my_new_tool(
       query_date: str = Field(description="Reference date in `YYYY-MM-DD` format"),
       dept_code: str | None = Field(default=None, description="Optional department filter"),
   ) -> dict:
       """One-line summary shown in tools/list; expand below with 2-3 sentences of detail."""
       params = filter_none({
           "queryDate": query_date,
           "deptCode": _val(dept_code),
       })
       return api_get("my_new_endpoint", params=params)
   ```

4. **If you created a new tool module**, add its import to `mcp_server.py` so the decorator runs on startup.

5. **Add an E2E test case** in `tests/test_all_tools.py`.

6. **Verify** with:

   ```bash
   uv run --env-file .env python tests/test_all_tools.py
   ```

## Code conventions

- **English** for all code, docstrings, tool descriptions, and commit messages (Chinese is fine in conversation but not in the repo)
- **Always** use `api_get` / `api_post` from `connectors.rest_client` — never call `requests` directly in tool code
- Use `_val()` from `tools._util` for every `Field(default=...)` parameter to neutralize the Pydantic FieldInfo pitfall when tools are invoked directly
- Use `filter_none()` to drop `None` values before sending query params
- Date inputs: accept ISO `YYYY-MM-DD` / `YYYY-MM` and convert internally with `iso_to_slash_date` / `iso_to_year_month` helpers when the endpoint needs slash format
- Tools return `dict` (MCP serializes them to JSON)
- Mark a tool with `KNOWN ISSUE:` in its docstring if it wraps an endpoint that MAYO has flagged as failing upstream

## Pull requests

1. Fork and branch (`git checkout -b feat/my-change`)
2. Run the connection test and E2E suite before pushing
3. Open a PR with a clear description and any relevant test output
