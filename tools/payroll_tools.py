"""Payroll (PY) tools — labor insurance, NHI, pension, and salary data.

Wraps the `/api/hrmlicense/PYClientOut_*` endpoints on the Payroll backend.
Callers pass dates in ISO `YYYY-MM-DD` (or `YYYY-MM` for monthly ranges);
this module converts to MAYO's expected `YYYY/MM/DD` or `YYYY/MM` format
under the hood.
"""

from typing import Optional

from pydantic import Field

from app import mcp
from connectors.rest_client import api_get
from tools._util import _val, filter_none, iso_to_slash_date, iso_to_year_month


@mcp.tool()
def get_monthly_labor_insurance(
    search_date: str = Field(description="Month reference date in `YYYY-MM-DD` format"),
    insurance_no: str = Field(description="Labor insurance unit number (e.g. `05363233`)"),
    language: str = Field(default="zh-tw", description="Language code"),
) -> dict:
    """Get the monthly labor insurance (勞保) detail list for an insurance unit.

    KNOWN ISSUE: This endpoint is marked as failing upstream in MAYO's own
    Postman collection. Expect a server-side error response until MAYO fixes it.
    """
    params = {
        "language": _val(language, "zh-tw"),
        "searchDate": iso_to_slash_date(search_date),
        "insuranceNo": insurance_no,
    }
    return api_get("monthly_labor_insurance", params=params)


@mcp.tool()
def get_monthly_nhi(
    search_date: str = Field(description="Month reference date in `YYYY-MM-DD` format"),
    insurance_no: str = Field(description="National Health Insurance unit number"),
    language: str = Field(default="zh-tw", description="Language code"),
) -> dict:
    """Get the monthly National Health Insurance (健保) detail list for a unit.

    KNOWN ISSUE: This endpoint is marked as failing upstream in MAYO's own
    Postman collection. Expect a server-side error response until MAYO fixes it.
    """
    params = {
        "language": _val(language, "zh-tw"),
        "searchDate": iso_to_slash_date(search_date),
        "insuranceNo": insurance_no,
    }
    return api_get("monthly_nhi", params=params)


@mcp.tool()
def get_monthly_labor_pension(
    search_date: str = Field(description="Month reference date in `YYYY-MM-DD` format"),
    insurance_no: str = Field(description="Labor pension unit number"),
    language: str = Field(default="zh-tw", description="Language code"),
) -> dict:
    """Get the monthly labor pension (勞退) detail list for a unit.

    KNOWN ISSUE: This endpoint is marked as failing upstream in MAYO's own
    Postman collection. Expect a server-side error response until MAYO fixes it.
    """
    params = {
        "language": _val(language, "zh-tw"),
        "searchDate": iso_to_slash_date(search_date),
        "insuranceNo": insurance_no,
    }
    return api_get("monthly_labor_pension", params=params)


@mcp.tool()
def get_salary_insurance_detail(
    search_date: str = Field(description="Reference date in `YYYY-MM-DD` format"),
    dept_code: Optional[str] = Field(default=None, description="Department code filter"),
    employee_number: Optional[str] = Field(default=None, description="Employee number filter"),
    is_have_retention: bool = Field(
        default=False,
        description="Include employees who are on retention (in-service-without-pay)",
    ),
    language: str = Field(default="zh-tw", description="Language code"),
) -> dict:
    """Get per-employee salary insurance contribution detail for a given date."""
    params = filter_none({
        "language": _val(language, "zh-tw"),
        "searchDate": search_date,
        "deptCode": _val(dept_code),
        "employeeNumber": _val(employee_number),
        "isHaveRetention": "true" if _val(is_have_retention, False) else "false",
    })
    return api_get("salary_insurance", params=params)


@mcp.tool()
def get_salary_bonus_list(
    start_month: str = Field(description="Range start month in `YYYY-MM` or `YYYY-MM-DD` format"),
    end_month: str = Field(description="Range end month in `YYYY-MM` or `YYYY-MM-DD` format"),
) -> dict:
    """Get the salary and bonus distribution roster across a month range.

    Accepts ISO-style `YYYY-MM` input (or a full `YYYY-MM-DD`, which is truncated
    to its month) and sends MAYO's expected `YYYY/MM` format internally.
    """
    params = {
        "startDate": iso_to_year_month(start_month),
        "endDate": iso_to_year_month(end_month),
    }
    return api_get("salary_bonus_list", params=params)
