"""Semantic tools — AI-friendly compositions on top of the raw MAYO endpoints.

These tools stitch multiple Foundation / Attendance / Payroll calls into a
single meaningful operation (e.g. a full employee profile) or provide a
cleaner default-driven interface than the underlying endpoint. They share the
same `@mcp.tool()` registration as the raw wrappers in `foundation_tools`,
`attendance_tools`, and `payroll_tools`.
"""

from typing import Optional

from pydantic import Field

from app import mcp
from connectors.rest_client import api_get, api_post
from tools._util import _val, filter_none, iso_to_year_month, today_iso


# ---------------------------------------------------------------------------
# Employee-centric aggregation
# ---------------------------------------------------------------------------

@mcp.tool()
def get_employee_profile(
    employee_number: str = Field(description="Target employee number (e.g. `A00384`)"),
    language: str = Field(default="zh-tw", description="Language code"),
) -> dict:
    """Aggregate one employee's master, work history, and education into a single profile.

    Calls PA (filtered by employee_number) plus the company-wide Working and
    Education exports, then filters the latter two down to the target employee.
    Useful when an assistant needs a complete picture without having to call
    three raw tools and join the results.
    """
    emp_no = employee_number
    lang = _val(language, "zh-tw")

    master = api_get(
        "export_pa_full",
        params={
            "language": lang,
            "employeeNumber": emp_no,
            "isContainChildDepartment": "true",
        },
    )
    working = api_get("export_working") or {}
    education = api_get("export_education") or {}

    return {
        "employee_number": emp_no,
        "master": master,
        "working_history": _filter_by_employee(working, emp_no),
        "education_history": _filter_by_employee(education, emp_no),
    }


def _filter_by_employee(payload: dict, employee_number: str) -> list:
    """Best-effort filter of a MAYO export payload down to one employee.

    MAYO export payloads vary in shape (top-level list, `{data: [...]}`,
    `{Data: [...]}`, etc.). This helper checks common shapes and matches
    on any field whose name looks like an employee number.
    """
    items = _extract_list(payload)
    if not items:
        return []
    keys = ("EmployeeNumber", "employeeNumber", "employee_number", "EmpNo", "empNo")
    out = []
    for item in items:
        if not isinstance(item, dict):
            continue
        for key in keys:
            if str(item.get(key, "")) == employee_number:
                out.append(item)
                break
    return out


def _extract_list(payload: dict) -> list:
    """Extract a list of records from a MAYO response of unknown shape."""
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []
    for key in ("Data", "data", "Items", "items", "Result", "result"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
    return []


# ---------------------------------------------------------------------------
# Organization snapshot
# ---------------------------------------------------------------------------

@mcp.tool()
def get_organization_snapshot_as_of(
    as_of_date: Optional[str] = Field(
        default=None,
        description="Snapshot date in `YYYY-MM-DD` format; defaults to today",
    ),
    dept_code: Optional[str] = Field(default=None, description="Root department code to query"),
) -> dict:
    """Capture the organization tree and active headcount as of a specific date.

    Combines `organization_tree` (OrgData) with `active_employees`
    (ActiveEmployeeData) so one call returns both the org hierarchy and the
    people staffed against it on that day.

    KNOWN ISSUE: Both underlying Report Center routes currently 404 on the
    PRE Foundation backend. This composite tool will light up once MAYO
    redeploys those endpoints.
    """
    date = _val(as_of_date) or today_iso()

    org = api_get(
        "organization_tree",
        params=filter_none({
            "queryDate": date,
            "deptCode": _val(dept_code),
            "isContainInEffective": "true",
        }),
    )
    people = api_get(
        "active_employees",
        params=filter_none({
            "EffectiveDate": date,
            "DeptCode": _val(dept_code),
        }),
    )

    return {
        "as_of_date": date,
        "dept_code": _val(dept_code),
        "organization": org,
        "active_employees": people,
    }


# ---------------------------------------------------------------------------
# Attendance summary
# ---------------------------------------------------------------------------

@mcp.tool()
def get_attendance_summary(
    start_date: str = Field(description="Range start in `YYYY-MM-DD` format"),
    end_date: str = Field(description="Range end in `YYYY-MM-DD` format"),
    include_abnormal: bool = Field(default=True, description="Include attendance exceptions"),
    include_overtime: bool = Field(default=True, description="Include overtime records"),
    include_leave: bool = Field(default=True, description="Include leave applications"),
) -> dict:
    """Build a consolidated attendance picture for a date range.

    Fans out to `attendance_history` plus optional `attendance_abnormal`,
    `overtime_records`, and `leave_history`, returning each section under a
    dedicated key.
    """
    body = {"startDate": start_date, "endDate": end_date}

    result: dict = {
        "start_date": start_date,
        "end_date": end_date,
        "history": api_post("attendance_history", json_body=body),
    }

    if _val(include_abnormal, True):
        result["abnormal"] = api_post("attendance_abnormal", json_body=body)
    if _val(include_overtime, True):
        result["overtime"] = api_post("overtime_records", json_body=body)
    if _val(include_leave, True):
        result["leave"] = api_post("leave_history", json_body=body)

    return result


# ---------------------------------------------------------------------------
# Convenience wrappers with ISO-friendly defaults
# ---------------------------------------------------------------------------

@mcp.tool()
def search_active_employees(
    as_of_date: Optional[str] = Field(
        default=None,
        description="Reference date in `YYYY-MM-DD` format; defaults to today",
    ),
    dept_code: Optional[str] = Field(default=None, description="Optional department code filter"),
) -> dict:
    """List active employees as of a date, defaulting to today when `as_of_date` is omitted.

    KNOWN ISSUE: Wraps `/ClientOut/ReportCenter/ActiveEmployeeData`, which
    currently returns 404 on the PRE Foundation backend.
    """
    date = _val(as_of_date) or today_iso()
    params = filter_none({
        "EffectiveDate": date,
        "DeptCode": _val(dept_code),
    })
    return api_get("active_employees", params=params)


@mcp.tool()
def get_monthly_payroll_report(
    year_month: str = Field(description="Target month in `YYYY-MM` format (e.g. `2025-01`)"),
) -> dict:
    """Get the salary and bonus distribution roster for a single month.

    Accepts ISO `YYYY-MM` (or `YYYY-MM-DD`, truncated) and converts to MAYO's
    required `YYYY/MM` format. Use the raw `get_salary_bonus_list` tool when
    you need a multi-month range.
    """
    ym = iso_to_year_month(year_month)
    params = {"startDate": ym, "endDate": ym}
    return api_get("salary_bonus_list", params=params)
