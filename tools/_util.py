"""Shared helpers for MAYO tool implementations."""

from pydantic.fields import FieldInfo


def _val(v, default=None):
    """Resolve a parameter value, handling Pydantic FieldInfo defaults from direct calls.

    When MCP tools are invoked directly (e.g., from the E2E test runner) rather
    than via the MCP protocol, Pydantic `Field(default=X)` arguments arrive as
    `FieldInfo` instances instead of their declared defaults. This helper
    normalizes both to the intended default.
    """
    if v is None or isinstance(v, FieldInfo):
        return default
    return v


def iso_to_slash_date(date_str: str | None) -> str | None:
    """Convert `YYYY-MM-DD` to `YYYY/MM/DD`.

    Used by PY Insurance endpoints (MonthLabor, MonthNHI, MonthLaborPension).
    """
    if date_str is None:
        return None
    return date_str.replace("-", "/")


def iso_to_year_month(date_str: str | None) -> str | None:
    """Convert `YYYY-MM-DD` or `YYYY-MM` to `YYYY/MM`.

    Used by the SalaryBonusList endpoint.
    """
    if date_str is None:
        return None
    parts = date_str.split("-")
    if len(parts) < 2:
        return date_str
    return f"{parts[0]}/{parts[1]}"


def filter_none(params: dict) -> dict:
    """Return a new dict with keys whose value is None removed."""
    return {k: v for k, v in params.items() if v is not None}


def today_iso() -> str:
    """Return today's date as `YYYY-MM-DD`."""
    from datetime import date

    return date.today().isoformat()
