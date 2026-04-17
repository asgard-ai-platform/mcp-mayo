"""API key authentication for MAYO Apollo.

MAYO expects the license key on a header literally named `hrmlicense`
(not `X-API-Key`). The same key authenticates all three backend domains
(Foundation, Attendance, Payroll).
"""

import os

ENV_VAR_NAME = "MAYO_API_KEY"
HEADER_NAME = "hrmlicense"


def _get_api_key() -> str:
    """Return the MAYO license key from the environment.

    Raises:
        RuntimeError: If MAYO_API_KEY is not set.
    """
    key = os.environ.get(ENV_VAR_NAME)
    if not key:
        raise RuntimeError(
            f"Missing MAYO API key. Set the {ENV_VAR_NAME} environment variable.\n"
            f"  export {ENV_VAR_NAME}=your_hrmlicense_token_here"
        )
    return key


def get_auth_headers() -> dict:
    """Return the `hrmlicense` header for MAYO API requests."""
    return {HEADER_NAME: _get_api_key()}
