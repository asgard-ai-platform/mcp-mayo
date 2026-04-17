"""REST client for MAYO Apollo APIs with retry on transient failures.

MAYO endpoints are split across three backend domains (Foundation,
Attendance, Payroll). The target domain is resolved by `config.settings.get_url`
from the endpoint key, so callers only need to know the key.
"""

import time

import requests

from config.settings import get_headers, get_url


class MayoAPIError(Exception):
    """Raised when the MAYO API returns a non-2xx response or is unreachable."""

    def __init__(self, status_code: int, message: str, endpoint: str = ""):
        self.status_code = status_code
        self.message = message
        self.endpoint = endpoint
        super().__init__(f"[{status_code}] {endpoint}: {message}")


def api_request(
    method: str,
    endpoint_key: str,
    params: dict | None = None,
    json_body: dict | None = None,
    path_params: dict | None = None,
    retries: int = 3,
    timeout: int = 60,
) -> dict:
    """Make an HTTP request against MAYO with exponential backoff on transient errors.

    Args:
        method: HTTP method (GET or POST).
        endpoint_key: A key from config.settings.ENDPOINTS.
        params: Query string parameters.
        json_body: Request body for POST.
        path_params: Values to substitute into the path template.
        retries: Number of retry attempts for timeout / connection errors.
        timeout: Per-request timeout in seconds.

    Raises:
        MayoAPIError: On non-2xx responses or after all retries are exhausted.
    """
    url = get_url(endpoint_key, **(path_params or {}))
    headers = get_headers()

    for attempt in range(retries):
        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=params,
                json=json_body,
                timeout=timeout,
            )

            if response.status_code >= 400:
                raise MayoAPIError(
                    status_code=response.status_code,
                    message=response.text[:500],
                    endpoint=endpoint_key,
                )

            # MAYO responses are JSON; treat empty body as empty dict.
            if not response.content:
                return {}
            try:
                return response.json()
            except ValueError:
                return {"raw": response.text}

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if attempt < retries - 1:
                time.sleep(2**attempt)
            else:
                raise MayoAPIError(
                    status_code=0,
                    message="Request failed after all retries (timeout/connection error)",
                    endpoint=endpoint_key,
                )


def api_get(
    endpoint_key: str,
    params: dict | None = None,
    path_params: dict | None = None,
    retries: int = 3,
) -> dict:
    """Convenience wrapper for GET requests."""
    return api_request("GET", endpoint_key, params=params, path_params=path_params, retries=retries)


def api_post(
    endpoint_key: str,
    json_body: dict | None = None,
    params: dict | None = None,
    path_params: dict | None = None,
    retries: int = 3,
) -> dict:
    """Convenience wrapper for POST requests."""
    return api_request(
        "POST", endpoint_key, params=params, json_body=json_body, path_params=path_params, retries=retries
    )
