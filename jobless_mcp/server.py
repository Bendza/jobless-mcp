"""
Jobless MCP server entry point.

Supports two transports, chosen via the JOBLESS_MCP_TRANSPORT env var:

- stdio (default)      → local subprocess mode, launched by Claude Desktop / Code
- http (streamable)    → hosted remote mode, deployed at mcp.jobless.dev

Both modes expose the same three tools defined in tools.py. The local
stdio mode reads the user's API key from JOBLESS_API_KEY. The hosted
HTTP mode reads it from the incoming Authorization header on each
request (the FastMCP Streamable HTTP transport handles that plumbing).

Run locally:
    pip install jobless-mcp
    JOBLESS_API_KEY=jbl_live_xxx jobless-mcp

Run as hosted HTTP server (inside Docker):
    JOBLESS_MCP_TRANSPORT=http PORT=8100 python -m jobless_mcp.server
"""

import os
import sys

from mcp.server.fastmcp import FastMCP

from .tools import register_tools


mcp = FastMCP(
    "jobless",
    instructions=(
        "Jobless gives you personalized job matches inside Claude. "
        "Call get_best_matches to fetch the user's top matches based on "
        "their stored Jobless resume (returns up to 10 per page). "
        "Call get_job to show full details for a specific job from those "
        "results. Call get_profile_status to check the user's tier, how "
        "many matches they have left today, or whether they have uploaded "
        "a resume yet. "
        "If get_best_matches returns error='no_resume', tell the user to "
        "visit the onboarding_url to upload their resume first. "
        "If it returns error='rate_limit_exceeded', tell them their free "
        "daily limit is hit and they can upgrade at the upgrade_url."
    ),
)
register_tools(mcp)


def main() -> None:
    """Console script entry point. Dispatches to stdio or HTTP transport."""
    transport = os.environ.get("JOBLESS_MCP_TRANSPORT", "stdio").lower().strip()

    if transport == "stdio":
        mcp.run(transport="stdio")
        return

    if transport == "http":
        host = os.environ.get("HOST", "0.0.0.0")
        try:
            port = int(os.environ.get("PORT", "8100"))
        except ValueError:
            print(
                f"Invalid PORT value: {os.environ.get('PORT')!r}",
                file=sys.stderr,
            )
            sys.exit(2)
        mcp.run(transport="streamable-http", host=host, port=port)
        return

    print(
        f"Unknown JOBLESS_MCP_TRANSPORT: {transport!r}. "
        "Use 'stdio' (default) or 'http'.",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
