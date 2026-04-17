#!/usr/bin/env python3
"""Verify that MAYO_API_KEY is set and all three MAYO backends are reachable.

Usage:
    uv run --env-file .env python scripts/auth/test_connection.py
"""

import os
import sys

sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)

import requests

from auth.api_key import HEADER_NAME
from config.settings import BASE_URLS, get_headers, get_url


REQUIRED_ENV = ["MAYO_API_KEY"]

# A cheap probe per domain.  We pick lightweight list-style endpoints.
PROBE_ENDPOINTS = [
    ("foundation", "export_company_custom_fields", {"language": "zh-tw"}),
    ("attendance", "attendance_rules", None),  # POST; smoke test only
    ("payroll", "salary_bonus_list", {"startDate": "2025/01", "endDate": "2025/01"}),
]


def check_env_vars() -> bool:
    print("Checking environment variables...")
    missing = [var for var in REQUIRED_ENV if not os.environ.get(var)]
    if missing:
        print("  FAIL: Missing environment variables:")
        for var in missing:
            print(f"    - {var}")
        return False
    print(f"  OK: {HEADER_NAME} header will be sent from MAYO_API_KEY.")
    return True


def check_domain(domain: str, endpoint_key: str, params: dict | None) -> bool:
    base = BASE_URLS[domain]
    print(f"\nProbing {domain} ({base})...")
    try:
        headers = get_headers()
        url = get_url(endpoint_key)
        # Use GET for smoke-testing even on POST endpoints; a 405 still means we
        # reached the server with valid auth.
        response = requests.get(url, headers=headers, params=params, timeout=15)
        print(f"  Status: {response.status_code}")

        if response.status_code in (200, 201):
            print("  OK: Reachable and authorized.")
            return True
        if response.status_code == 401:
            print("  FAIL: Unauthorized — check that MAYO_API_KEY is the correct hrmlicense token.")
            return False
        if response.status_code == 403:
            print("  FAIL: Forbidden — your key may not have access to this domain.")
            return False
        if response.status_code == 405:
            print("  OK: Method not allowed is expected for POST-only endpoints; auth accepted.")
            return True
        print(f"  WARN: Unexpected status {response.status_code}")
        print(f"  Response: {response.text[:300]}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"  FAIL: Cannot connect to {base}")
        return False
    except requests.exceptions.Timeout:
        print("  FAIL: Connection timed out.")
        return False
    except Exception as exc:
        print(f"  FAIL: {exc}")
        return False


def main():
    print("=" * 60)
    print("mcp-mayo — Connection Test")
    print("=" * 60)

    if not check_env_vars():
        print("\nFix the missing environment variables and try again.")
        sys.exit(1)

    results = [check_domain(d, e, p) for d, e, p in PROBE_ENDPOINTS]
    if not all(results):
        print("\nOne or more domains failed. See output above.")
        sys.exit(1)

    print("\nAll domains reachable. Ready to use.")


if __name__ == "__main__":
    main()
