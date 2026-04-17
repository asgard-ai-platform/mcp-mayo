"""Foundation (FD) tools — people and organization master data.

Wraps the `/api/hrmlicense/ClientOut/...` endpoints on the Foundation backend.
All tools are thin, 1:1 wrappers around their underlying endpoint; higher-level
aggregations live in `tools.semantic_tools`.
"""

from typing import Optional

from pydantic import Field

from app import mcp
from connectors.rest_client import api_get, api_post
from tools._util import _val, filter_none


# ---------------------------------------------------------------------------
# Report Center endpoints
# ---------------------------------------------------------------------------

@mcp.tool()
def list_active_employees(
    effective_date: str = Field(description="Effective date in `YYYY-MM-DD` format"),
    dept_code: Optional[str] = Field(
        default=None,
        description="Optional department code filter; omit to include all departments",
    ),
) -> dict:
    """List active employees as of a given date, optionally scoped to a department.

    KNOWN ISSUE: The `/ClientOut/ReportCenter/ActiveEmployeeData` route returns
    404 on the PRE Foundation backend. The tool is kept for when MAYO
    deploys the Report Center endpoints to this environment.
    """
    params = filter_none({
        "EffectiveDate": effective_date,
        "DeptCode": _val(dept_code),
    })
    return api_get("active_employees", params=params)


@mcp.tool()
def list_resigned_employees(
    start_date: str = Field(description="Start date in `YYYY-MM-DD` format"),
    end_date: str = Field(description="End date in `YYYY-MM-DD` format"),
    dept_code: Optional[str] = Field(default=None, description="Optional department code filter"),
) -> dict:
    """List employees who resigned or took leave within a date range.

    KNOWN ISSUE: The `/ClientOut/ReportCenter/ResignAndLeaveData` route returns
    404 on the PRE Foundation backend. The tool is kept for when MAYO
    deploys the Report Center endpoints to this environment.
    """
    params = filter_none({
        "StartDate": start_date,
        "EndDate": end_date,
        "DeptCode": _val(dept_code),
    })
    return api_get("resigned_employees", params=params)


@mcp.tool()
def get_organization_tree(
    query_date: str = Field(description="Snapshot date in `YYYY-MM-DD` format"),
    dept_code: Optional[str] = Field(default=None, description="Root department code to query from"),
    include_ineffective: bool = Field(
        default=True,
        description="Include departments that are not effective on the snapshot date",
    ),
) -> dict:
    """Get the organization hierarchy as of a specific date.

    KNOWN ISSUE: The `/ClientOut/ReportCenter/OrgData` route returns 404 on
    the PRE Foundation backend. The tool is kept for when MAYO deploys
    the Report Center endpoints to this environment.
    """
    params = filter_none({
        "queryDate": query_date,
        "deptCode": _val(dept_code),
        "isContainInEffective": "true" if _val(include_ineffective, True) else "false",
    })
    return api_get("organization_tree", params=params)


# ---------------------------------------------------------------------------
# Effective-data exports
# ---------------------------------------------------------------------------

@mcp.tool()
def export_organization_with_employees(
    language: str = Field(default="zh-tw", description="Language code, e.g. `zh-tw`, `en-us`"),
) -> dict:
    """Export effective organization units together with their employees (OM + PA)."""
    params = {"language": _val(language, "zh-tw")}
    return api_get("export_om_and_pa", params=params)


@mcp.tool()
def export_employees(
    language: str = Field(default="zh-tw", description="Language code"),
) -> dict:
    """Export effective employee master data (core fields only)."""
    params = {"language": _val(language, "zh-tw")}
    return api_get("export_employee", params=params)


@mcp.tool()
def export_departments(
    language: str = Field(default="zh-tw", description="Language code"),
) -> dict:
    """Export effective department master data (core fields only)."""
    params = {"language": _val(language, "zh-tw")}
    return api_get("export_department", params=params)


@mcp.tool()
def export_organization_full(
    language: str = Field(default="zh-tw", description="Language code"),
) -> dict:
    """Export effective organization master data with all fields (OM endpoint)."""
    params = {"language": _val(language, "zh-tw")}
    return api_get("export_om_full", params=params)


@mcp.tool()
def export_employees_full(
    language: str = Field(default="zh-tw", description="Language code"),
    employee_number: Optional[str] = Field(default=None, description="Filter to a specific employee"),
    department_code: Optional[str] = Field(default=None, description="Filter to a specific department"),
    is_contain_child_department: bool = Field(
        default=True,
        description="Include child departments when filtering by `department_code`",
    ),
    start_date: Optional[str] = Field(
        default=None,
        description="Start of effective date range (`YYYY-MM-DD`) for PA changes",
    ),
    end_date: Optional[str] = Field(
        default=None,
        description="End of effective date range (`YYYY-MM-DD`) for PA changes",
    ),
    working_status: Optional[str] = Field(
        default=None,
        description="Filter by working status code (e.g. `A01`, `A13`)",
    ),
    bank_details: Optional[str] = Field(
        default=None,
        description="Set to `1` to include bank account details in the response",
    ),
) -> dict:
    """Export effective employee data with every PA field. Supports many optional filters."""
    params = filter_none({
        "language": _val(language, "zh-tw"),
        "employeeNumber": _val(employee_number),
        "departmentCode": _val(department_code),
        "isContainChildDepartment": "true" if _val(is_contain_child_department, True) else "false",
        "startDate": _val(start_date),
        "endDate": _val(end_date),
        "workingStatus": _val(working_status),
        "bankDetails": _val(bank_details),
    })
    return api_get("export_pa_full", params=params)


@mcp.tool()
def export_expatriations(
    language: str = Field(default="zh-tw", description="Language code"),
) -> dict:
    """Export effective employee expatriation (外派/派駐) assignments."""
    params = {"language": _val(language, "zh-tw")}
    return api_get("export_expatriation", params=params)


@mcp.tool()
def export_working_history() -> dict:
    """Export all employees' work-experience records."""
    return api_get("export_working")


@mcp.tool()
def export_education_history() -> dict:
    """Export all employees' education records."""
    return api_get("export_education")


# ---------------------------------------------------------------------------
# Change logs
# ---------------------------------------------------------------------------

@mcp.tool()
def export_employee_changes(
    start_date: str = Field(description="Range start in `YYYY-MM-DD` format"),
    end_date: str = Field(description="Range end in `YYYY-MM-DD` format"),
    page_number: int = Field(default=1, description="Page number (1-indexed)"),
    page_size: int = Field(default=20, description="Records per page"),
    language: str = Field(default="zh-tw", description="Language code"),
) -> dict:
    """Export employee change orders within a date range (paginated)."""
    params = {
        "language": _val(language, "zh-tw"),
        "pageSize": _val(page_size, 20),
        "pageNumber": _val(page_number, 1),
        "startDate": start_date,
        "endDate": end_date,
    }
    return api_get("export_employee_changes", params=params)


@mcp.tool()
def export_organization_changes(
    start_date: str = Field(description="Range start in `YYYY-MM-DD` format"),
    end_date: str = Field(description="Range end in `YYYY-MM-DD` format"),
    page_number: int = Field(default=1, description="Page number (1-indexed)"),
    page_size: int = Field(default=20, description="Records per page"),
    language: str = Field(default="zh-tw", description="Language code"),
) -> dict:
    """Export organization change orders within a date range (paginated)."""
    params = {
        "language": _val(language, "zh-tw"),
        "pageSize": _val(page_size, 20),
        "pageNumber": _val(page_number, 1),
        "startDate": start_date,
        "endDate": end_date,
    }
    return api_get("export_org_changes", params=params)


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------

@mcp.tool()
def export_pa_options(
    language: str = Field(default="zh-tw", description="Language code"),
) -> dict:
    """Export reference code tables used by the People+ (PA) module."""
    params = {"language": _val(language, "zh-tw")}
    return api_post("export_pa_options", params=params)


@mcp.tool()
def export_company_custom_fields(
    language: str = Field(default="zh-tw", description="Language code"),
) -> dict:
    """Export the custom field definitions configured by the tenant."""
    params = {"language": _val(language, "zh-tw")}
    return api_get("export_company_custom_fields", params=params)
