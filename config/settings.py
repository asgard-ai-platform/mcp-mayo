"""Configuration for MAYO Apollo HRM backends.

MAYO exposes three independent backend domains that all share the same
`hrmlicense` authentication. Endpoint keys are tagged with their domain
so the URL builder can resolve the correct base URL.
"""

from auth.api_key import get_auth_headers

# -----------------------------------------------------------------------------
# Base URLs — pre-production environment (test env used for this MCP server).
# Production URLs are intentionally NOT wired up; flip these in a fork if you
# need production access and your credentials allow it.
# -----------------------------------------------------------------------------
BASE_URLS = {
    "foundation": "https://pre-linkup-be.mayohr.com",
    "attendance": "https://pre-pt-be.mayohr.com",
    "payroll": "https://pre-py-be.mayohr.com",
}

# Default page size for endpoints that support pagination (EmployeeChangeContent,
# OrgChangeContent). MAYO uses `pageSize` as the parameter name.
DEFAULT_PAGE_SIZE = 20

# -----------------------------------------------------------------------------
# Endpoint map — key -> (domain, path_template)
# -----------------------------------------------------------------------------
ENDPOINTS: dict[str, tuple[str, str]] = {
    # ----- Foundation (FD) -----
    "active_employees": ("foundation", "/api/hrmlicense/ClientOut/ReportCenter/ActiveEmployeeData"),
    "resigned_employees": ("foundation", "/api/hrmlicense/ClientOut/ReportCenter/ResignAndLeaveData"),
    "organization_tree": ("foundation", "/api/hrmlicense/ClientOut/ReportCenter/OrgData"),
    "export_om_and_pa": ("foundation", "/api/hrmlicense/ClientOut/OMandPA"),
    "export_employee": ("foundation", "/api/hrmlicense/ClientOut/Employee"),
    "export_department": ("foundation", "/api/hrmlicense/ClientOut/Department"),
    "export_employee_changes": ("foundation", "/api/hrmlicense/ClientOut/EmployeeChangeContent"),
    "export_org_changes": ("foundation", "/api/hrmlicense/ClientOut/OrgChangeContent"),
    "export_expatriation": ("foundation", "/api/hrmlicense/ClientOut/Expatriation"),
    "export_om_full": ("foundation", "/api/hrmlicense/ClientOut/OM"),
    "export_pa_full": ("foundation", "/api/hrmlicense/ClientOut/PA"),
    "export_working": ("foundation", "/api/hrmlicense/ClientOut/Working"),
    "export_education": ("foundation", "/api/hrmlicense/ClientOut/Education"),
    "export_pa_options": ("foundation", "/api/hrmlicense/ClientOut/PaOptions"),
    "export_company_custom_fields": ("foundation", "/api/hrmlicense/ClientOut/CompanyCustomFields"),
    # ----- Attendance (PT) -----
    "attendance_rules": ("attendance", "/api/hrmlicense/exportdata_attendance_rule"),
    "attendance_history": ("attendance", "/api/hrmlicense/exportdata_attendance_history"),
    "attendance_abnormal": ("attendance", "/api/hrmlicense/exportdata_attendance_abnormal"),
    "forgot_checkin": ("attendance", "/api/hrmlicense/exportdata_forgot_checkin_record"),
    "leave_history": ("attendance", "/api/hrmlicense/exportdata_leave_historyV2"),
    "employee_calendar": ("attendance", "/api/hrmlicense/exportdata_employee_calendar"),
    "overtime_records": ("attendance", "/api/hrmlicense/exportdata_overtime_record"),
    "trip_history": ("attendance", "/api/hrmlicense/exportdata_trip_history"),
    # ----- Payroll (PY) -----
    "monthly_labor_insurance": ("payroll", "/api/hrmlicense/PYClientOut_Insurance/MonthLabor"),
    "monthly_nhi": ("payroll", "/api/hrmlicense/PYClientOut_Insurance/MonthNHI"),
    "monthly_labor_pension": ("payroll", "/api/hrmlicense/PYClientOut_Insurance/MonthLaborPension"),
    "salary_insurance": ("payroll", "/api/hrmlicense/PYClientOut_Salary/SalaryInsurance"),
    "salary_bonus_list": ("payroll", "/api/hrmlicense/PYClientOut_Salary/SalaryBonusList"),
}


def get_headers() -> dict:
    """Return base HTTP headers including the `hrmlicense` auth header."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    headers.update(get_auth_headers())
    return headers


def get_url(endpoint_key: str, **path_params) -> str:
    """Resolve a MAYO endpoint key to a full URL.

    Args:
        endpoint_key: A key from ENDPOINTS.
        **path_params: Values to substitute into a path template (if any).

    Raises:
        KeyError: If the endpoint key is unknown.
    """
    domain, path = ENDPOINTS[endpoint_key]
    base = BASE_URLS[domain]
    if path_params:
        path = path.format(**path_params)
    return f"{base}{path}"
