"""Attendance (PT) tools — clock-in, leave, overtime, and business-trip records.

Wraps the `/api/hrmlicense/exportdata_*` endpoints on the Attendance backend.
All PT endpoints are POST with a JSON body containing date parameters.
"""

from pydantic import Field

from app import mcp
from connectors.rest_client import api_post


@mcp.tool()
def get_attendance_rules(
    search_date: str = Field(description="Reference date in `YYYY-MM-DD` format"),
) -> dict:
    """Get each employee's base attendance configuration as of a given date.

    Returns the shift, rest-day rule, and attendance-group information that
    applies to every active employee on `search_date`.
    """
    body = {"searchDate": search_date}
    return api_post("attendance_rules", json_body=body)


@mcp.tool()
def get_attendance_history(
    start_date: str = Field(description="Range start in `YYYY-MM-DD` format"),
    end_date: str = Field(description="Range end in `YYYY-MM-DD` format"),
) -> dict:
    """Get raw clock-in / clock-out records across all employees within a date range."""
    body = {"startDate": start_date, "endDate": end_date}
    return api_post("attendance_history", json_body=body)


@mcp.tool()
def get_attendance_abnormal(
    start_date: str = Field(description="Range start in `YYYY-MM-DD` format"),
    end_date: str = Field(description="Range end in `YYYY-MM-DD` format"),
) -> dict:
    """Get attendance exceptions (late, early leave, missed punch, etc.) within a date range."""
    body = {"startDate": start_date, "endDate": end_date}
    return api_post("attendance_abnormal", json_body=body)


@mcp.tool()
def get_forgot_checkin_records(
    start_date: str = Field(description="Range start in `YYYY-MM-DD` format"),
    end_date: str = Field(description="Range end in `YYYY-MM-DD` format"),
) -> dict:
    """Get manually-added or corrected clock-in records within a date range."""
    body = {"startDate": start_date, "endDate": end_date}
    return api_post("forgot_checkin", json_body=body)


@mcp.tool()
def get_leave_history(
    start_date: str = Field(description="Range start in `YYYY-MM-DD` format"),
    end_date: str = Field(description="Range end in `YYYY-MM-DD` format"),
) -> dict:
    """Get approved and pending leave applications within a date range (leave_historyV2)."""
    body = {"startDate": start_date, "endDate": end_date}
    return api_post("leave_history", json_body=body)


@mcp.tool()
def get_employee_calendar(
    start_date: str = Field(description="Range start in `YYYY-MM-DD` format"),
    end_date: str = Field(description="Range end in `YYYY-MM-DD` format"),
) -> dict:
    """Get each employee's assigned shift calendar (work day / rest day / holiday) for a range."""
    body = {"startDate": start_date, "endDate": end_date}
    return api_post("employee_calendar", json_body=body)


@mcp.tool()
def get_overtime_records(
    start_date: str = Field(description="Range start in `YYYY-MM-DD` format"),
    end_date: str = Field(description="Range end in `YYYY-MM-DD` format"),
) -> dict:
    """Get approved overtime records within a date range."""
    body = {"startDate": start_date, "endDate": end_date}
    return api_post("overtime_records", json_body=body)


@mcp.tool()
def get_trip_history(
    start_date: str = Field(description="Range start in `YYYY-MM-DD` format"),
    end_date: str = Field(description="Range end in `YYYY-MM-DD` format"),
) -> dict:
    """Get business trip / field-work records within a date range.

    KNOWN ISSUE: This endpoint is marked as failing upstream in MAYO's own
    Postman collection. Expect a server-side error response until MAYO fixes it.
    """
    body = {"startDate": start_date, "endDate": end_date}
    return api_post("trip_history", json_body=body)
