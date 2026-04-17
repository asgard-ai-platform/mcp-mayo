#!/usr/bin/env python3
"""E2E test runner for every registered mcp-mayo tool.

Runs each tool against the live MAYO PRE environment using credentials from
MAYO_API_KEY. Tools that map to endpoints MAYO has flagged as broken upstream
are still exercised so the failure mode is visible, but their failures don't
count against the overall pass/fail total.

Usage:
    uv run --env-file .env python tests/test_all_tools.py
"""

import asyncio
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import tool modules to register every @mcp.tool().
import tools.foundation_tools as ft  # noqa: F401
import tools.attendance_tools as at  # noqa: F401
import tools.payroll_tools as pt  # noqa: F401
import tools.semantic_tools as st  # noqa: F401

from app import mcp


# Known-broken upstream endpoints — their failures are logged but not counted.
KNOWN_ISSUE_TESTS = {
    "get_trip_history",
    "get_monthly_labor_insurance",
    "get_monthly_nhi",
    "get_monthly_labor_pension",
    # /ClientOut/ReportCenter/* currently 404 on the PRE Foundation backend.
    "list_active_employees",
    "list_resigned_employees",
    "get_organization_tree",
    "search_active_employees",
    "get_organization_snapshot_as_of",
}


results: list[tuple[str, str, str]] = []  # (status, name, note)


def run_test(name: str, fn, **kwargs) -> None:
    print(f"\n{'=' * 60}")
    print(f"TEST: {name}")
    print(f"{'=' * 60}")
    try:
        result = fn(**kwargs)
        if isinstance(result, dict):
            for key, value in result.items():
                preview = str(value)
                if len(preview) > 100:
                    preview = preview[:100] + "..."
                print(f"    {key}: {preview}")
        print("  PASS")
        results.append(("PASS", name, ""))
    except Exception as exc:
        note = "known-issue" if name in KNOWN_ISSUE_TESTS else ""
        status = "KNOWN" if note else "FAIL"
        print(f"  {status}: {exc}")
        if status == "FAIL":
            traceback.print_exc()
        results.append((status, name, note))


def main() -> None:
    tools_list = asyncio.run(mcp.list_tools())
    print(f"Registered tools: {len(tools_list)}")
    for tool in tools_list:
        desc = tool.description[:80] if tool.description else "no description"
        print(f"  - {tool.name}: {desc}")

    print(f"\n{'#' * 60}")
    print("RUNNING E2E TESTS")
    print(f"{'#' * 60}")

    # ------------------------------------------------------------------
    # Foundation (FD)
    # ------------------------------------------------------------------
    run_test("list_active_employees", ft.list_active_employees, effective_date="2025-09-19")
    run_test(
        "list_resigned_employees",
        ft.list_resigned_employees,
        start_date="2025-09-01",
        end_date="2025-09-30",
    )
    run_test(
        "get_organization_tree",
        ft.get_organization_tree,
        query_date="2025-09-19",
    )
    run_test("export_organization_with_employees", ft.export_organization_with_employees)
    run_test("export_employees", ft.export_employees)
    run_test("export_departments", ft.export_departments)
    run_test("export_organization_full", ft.export_organization_full)
    run_test("export_employees_full", ft.export_employees_full)
    run_test("export_expatriations", ft.export_expatriations)
    run_test("export_working_history", ft.export_working_history)
    run_test("export_education_history", ft.export_education_history)
    run_test(
        "export_employee_changes",
        ft.export_employee_changes,
        start_date="2020-01-01",
        end_date="2020-01-31",
    )
    run_test(
        "export_organization_changes",
        ft.export_organization_changes,
        start_date="2020-01-01",
        end_date="2020-01-31",
    )
    run_test("export_pa_options", ft.export_pa_options)
    run_test("export_company_custom_fields", ft.export_company_custom_fields)

    # ------------------------------------------------------------------
    # Attendance (PT)
    # ------------------------------------------------------------------
    run_test("get_attendance_rules", at.get_attendance_rules, search_date="2025-09-01")
    run_test(
        "get_attendance_history",
        at.get_attendance_history,
        start_date="2025-09-01",
        end_date="2025-09-01",
    )
    run_test(
        "get_attendance_abnormal",
        at.get_attendance_abnormal,
        start_date="2025-09-01",
        end_date="2025-09-07",
    )
    run_test(
        "get_forgot_checkin_records",
        at.get_forgot_checkin_records,
        start_date="2025-09-01",
        end_date="2025-09-01",
    )
    run_test(
        "get_leave_history",
        at.get_leave_history,
        start_date="2025-09-01",
        end_date="2025-09-30",
    )
    run_test(
        "get_employee_calendar",
        at.get_employee_calendar,
        start_date="2025-09-01",
        end_date="2025-09-30",
    )
    run_test(
        "get_overtime_records",
        at.get_overtime_records,
        start_date="2025-01-01",
        end_date="2025-06-30",
    )
    run_test(
        "get_trip_history",
        at.get_trip_history,
        start_date="2025-09-01",
        end_date="2025-09-30",
    )

    # ------------------------------------------------------------------
    # Payroll (PY)
    # ------------------------------------------------------------------
    run_test(
        "get_monthly_labor_insurance",
        pt.get_monthly_labor_insurance,
        search_date="2022-06-01",
        insurance_no="05363233",
    )
    run_test(
        "get_monthly_nhi",
        pt.get_monthly_nhi,
        search_date="2022-06-01",
        insurance_no="05363233",
    )
    run_test(
        "get_monthly_labor_pension",
        pt.get_monthly_labor_pension,
        search_date="2022-06-01",
        insurance_no="77778888",
    )
    run_test(
        "get_salary_insurance_detail",
        pt.get_salary_insurance_detail,
        search_date="2025-02-04",
        dept_code="C030010",
        employee_number="A00384",
    )
    run_test(
        "get_salary_bonus_list",
        pt.get_salary_bonus_list,
        start_month="2025-01",
        end_month="2025-01",
    )

    # ------------------------------------------------------------------
    # Semantic
    # ------------------------------------------------------------------
    run_test("search_active_employees", st.search_active_employees)
    run_test("get_organization_snapshot_as_of", st.get_organization_snapshot_as_of)
    run_test(
        "get_attendance_summary",
        st.get_attendance_summary,
        start_date="2025-09-01",
        end_date="2025-09-07",
    )
    run_test(
        "get_monthly_payroll_report",
        st.get_monthly_payroll_report,
        year_month="2025-01",
    )
    run_test(
        "get_employee_profile",
        st.get_employee_profile,
        employee_number="A00384",
    )

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print(f"\n{'#' * 60}")
    print("TEST SUMMARY")
    print(f"{'#' * 60}")

    passed = sum(1 for s, *_ in results if s == "PASS")
    failed = sum(1 for s, *_ in results if s == "FAIL")
    known = sum(1 for s, *_ in results if s == "KNOWN")

    for status, name, note in results:
        icon = {"PASS": "+", "FAIL": "X", "KNOWN": "~"}[status]
        suffix = f" ({note})" if note else ""
        print(f"  [{icon}] {name}{suffix}")

    print(
        f"\nTotal: {len(results)} | Passed: {passed} | Failed: {failed} | Known issues: {known}"
    )

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
