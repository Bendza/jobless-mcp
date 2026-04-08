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
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from .client import JoblessClient


def register_tools(mcp: FastMCP) -> None:
    """Register Jobless tools with the given FastMCP instance.

    Called once at server startup from server.py. A single JoblessClient
    is created per tool call because the API key may be session-scoped
    in hosted HTTP mode (different users hitting the same process).
    """

    @mcp.tool()
    def get_best_matches(limit: int = 10, page: int = 1) -> dict[str, Any]:
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
        limit = max(1, min(limit, 20))
        page = max(1, page)
        client = JoblessClient()
        try:
            return client.get(
                "/jobs/best-matches/",
                params={"page_size": limit, "page": page},
            )
        finally:
            client.close()

    @mcp.tool()
    def get_job(job_id: str) -> dict[str, Any]:
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
        client = JoblessClient()
        try:
            return client.get(f"/jobs/{job_id}/")
        finally:
            client.close()

    @mcp.tool()
    def get_profile_status() -> dict[str, Any]:
        """
        Get the current user's Jobless profile state and MCP usage.

        Use this to check:
        - Whether the user has uploaded a resume yet (`has_resume`)
        - Their current tier (`tier`: free / pro / ultimate)
        - How many matches they have left today (`matches_remaining_today`)
        - When the daily limit resets (`resets_at`)

        Useful at the start of a conversation or when the user asks "how am I
        doing?", "what tier am I on?", or "how many matches do I have left?".

        If `has_resume` is false, direct the user to `onboarding_url` to upload
        their resume before calling `get_best_matches`.

        Returns:
            Dict with `has_resume`, `tier`, `matches_used_today`,
            `matches_remaining_today`, `resets_at`, `upgrade_url`, `onboarding_url`.
        """
        client = JoblessClient()
        try:
            return client.get("/user/mcp/status/")
        finally:
            client.close()
