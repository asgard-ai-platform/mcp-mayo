#!/usr/bin/env python3
"""Entry point for the mcp-mayo server.

Side-effect imports below trigger `@mcp.tool()` registration in each module.
"""

import tools.foundation_tools  # noqa: F401
import tools.attendance_tools  # noqa: F401
import tools.payroll_tools  # noqa: F401
import tools.semantic_tools  # noqa: F401

from app import mcp


def main():
    mcp.run()  # stdio transport


if __name__ == "__main__":
    main()
