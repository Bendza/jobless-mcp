"""
MCP tool definitions for Jobless.

Three read-only tools exposed to Claude clients:
- get_best_matches: personalized job matches from the user's Jobless profile
- get_job: full details for a specific job
- get_profile_status: tier, daily usage, and resume upload state

Each tool is a thin translator — it converts MCP tool arguments into
HTTP calls against api.jobless.dev and returns the JSON body verbatim.
Errors are surfaced as structured dicts so Claude can explain them to
the user.

API key resolution supports both transports:
- **stdio (local)**: Read from JOBLESS_API_KEY env var at client construction
- **streamable-http (hosted)**: Extract from per-request Authorization header
  via the FastMCP Context object. Each user sends their own Bearer token.
"""

import os
from typing import Any

from mcp.server.fastmcp import Context, FastMCP

from .client import JoblessClient


# Module-level fallback for stdio mode where ctx has no HTTP request.
_ENV_API_KEY = os.environ.get("JOBLESS_API_KEY", "")


def _resolve_api_key(ctx: Context | None) -> str | None:
    """
    Resolve the caller's Jobless API key.

    In hosted HTTP mode, the MCP server receives each request with the
    user's Bearer token in the Authorization header. We pull it off the
    underlying Starlette request via the FastMCP Context.

    In stdio mode there's no HTTP request, so we fall back to the
    JOBLESS_API_KEY environment variable set by the user's Claude client
    config.
    """
    if ctx is not None:
        try:
            request = ctx.request_context.request
            auth = request.headers.get("authorization", "") if request else ""
            if auth and auth.lower().startswith("bearer "):
                return auth[7:].strip() or None
        except Exception:
            # Stdio mode, or a FastMCP version without request access —
            # fall through to env var.
            pass
    return _ENV_API_KEY or None


def _missing_auth_error() -> dict[str, Any]:
    return {
        "error": "missing_auth",
        "message": (
            "No Jobless API key was provided. Generate one at "
            "https://jobless.dev/mcp and add it to your MCP client config as "
            "'Authorization: Bearer <your key>'."
        ),
    }


def register_tools(mcp: FastMCP) -> None:
    """Register all Jobless tools with the given FastMCP instance."""

    @mcp.tool()
    def get_best_matches(
        limit: int = 10,
        page: int = 1,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """
        Get the user's top personalized job matches from their Jobless profile.

        Returns up to `limit` jobs ranked by dual-KNN similarity to the user's
        stored resume (role intent + technical skills). Free tier: 100 calls
        per day. Pro tier: unlimited + ColBERT semantic reranking.

        If the user has not uploaded a resume yet, the response contains
        `error: "no_resume"` and `onboarding_url` — tell the user to visit
        the URL to upload their resume, then call this tool again.

        If the user has hit their daily limit, the response contains
        `error: "rate_limit_exceeded"` and `upgrade_url` — tell the user
        they can upgrade for unlimited matches.

        Args:
            limit: Number of jobs to return (1-20, default 10). Larger values
                burn more of the user's context window without adding much
                value — 10 is a good default.
            page: Page number for pagination (default 1). Use page=2, page=3
                etc. to see more matches after the first page.

        Returns:
            On success: dict with `matches` (list of job dicts with id, title,
            company, location, url, score), `total_matches`, `page`, `page_size`,
            plus MCP metadata `tier`, `matches_used_today`, `matches_remaining_today`.
            On error: dict with `error` key and a human-readable `message`.
        """
        api_key = _resolve_api_key(ctx)
        if not api_key:
            return _missing_auth_error()

        limit = max(1, min(limit, 20))
        page = max(1, page)
        client = JoblessClient(api_key=api_key)
        try:
            return client.get(
                "/jobs/best-matches/",
                params={"page_size": limit, "page": page},
            )
        finally:
            client.close()

    @mcp.tool()
    def get_job(job_id: str, ctx: Context | None = None) -> dict[str, Any]:
        """
        Get full details for a specific job by its ID.

        Use this after `get_best_matches` when the user asks for more
        information about a job in the results (e.g., "tell me more about #2").
        Returns the full role description, required skills, seniority,
        location details, and application URL.

        Args:
            job_id: The UUID of the job (from an `id` field in `get_best_matches` results).

        Returns:
            On success: dict with `id`, `title`, `company`, `location`,
            `role_summary`, `technical_skills`, `seniority_score`, `url`, and more.
            On error: dict with `error` key and `message`.
        """
        if not job_id:
            return {
                "error": "invalid_argument",
                "message": "job_id is required and must be a non-empty string.",
            }

        api_key = _resolve_api_key(ctx)
        if not api_key:
            return _missing_auth_error()

        client = JoblessClient(api_key=api_key)
        try:
            return client.get(f"/jobs/{job_id}/")
        finally:
            client.close()

    @mcp.tool()
    def get_profile_status(ctx: Context | None = None) -> dict[str, Any]:
        """
        Get the current user's Jobless profile state and MCP usage.

        Use this to check whether the user has uploaded a resume yet, what
        tier they're on, and how many free matches they have left today.
        Useful at the start of a conversation or when the user asks
        "how am I doing?" or "what tier am I on?".

        Returns:
            Dict with `has_resume`, `tier`, `matches_used_today`,
            `matches_remaining_today`, `resets_at`, `upgrade_url`, `onboarding_url`.
        """
        api_key = _resolve_api_key(ctx)
        if not api_key:
            return _missing_auth_error()

        client = JoblessClient(api_key=api_key)
        try:
            return client.get("/user/mcp/status/")
        finally:
            client.close()
