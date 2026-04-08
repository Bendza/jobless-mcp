"""
Thin httpx wrapper around the Jobless REST API.

The MCP server layer translates tool calls into HTTPS requests against
api.jobless.dev. This module handles auth, error mapping, and response
normalization so the tool functions stay tiny.
"""

import os
from typing import Any

import httpx


DEFAULT_BASE_URL = "https://api.jobless.dev"
DEFAULT_TIMEOUT = 30.0


class JoblessClient:
    """Synchronous httpx client for the Jobless REST API.

    The API key is read from the `JOBLESS_API_KEY` environment variable
    unless passed explicitly. The base URL defaults to https://api.jobless.dev
    but can be overridden with `JOBLESS_API_BASE` for local development or
    self-hosted deployments.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        resolved_key = api_key or os.environ.get("JOBLESS_API_KEY", "")
        if not resolved_key:
            raise ValueError(
                "JOBLESS_API_KEY is not set. Generate one at https://jobless.dev/mcp "
                "and add it to your MCP client config."
            )

        resolved_base = (
            base_url
            or os.environ.get("JOBLESS_API_BASE", DEFAULT_BASE_URL)
        ).rstrip("/")

        self.api_key = resolved_key
        self.base_url = resolved_base
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "jobless-mcp/0.1.0",
            },
            timeout=timeout,
        )

    def get(self, path: str, params: dict | None = None) -> dict[str, Any]:
        """GET a path and return the parsed JSON body (or a structured error dict)."""
        try:
            resp = self._client.get(path, params=params or {})
        except httpx.RequestError as exc:
            return {
                "error": "network_error",
                "message": f"Could not reach Jobless API: {exc}. Try again in a moment.",
            }
        return self._handle(resp)

    def _handle(self, resp: httpx.Response) -> dict[str, Any]:
        """Map an httpx Response into either the JSON body or a structured error dict.

        Error format is stable so the MCP tool layer can forward it verbatim
        to Claude, which then surfaces the message to the user.
        """
        if resp.status_code == 401:
            return {
                "error": "unauthorized",
                "message": (
                    "Invalid or revoked API key. Generate a new one at "
                    "https://jobless.dev/mcp"
                ),
            }
        if resp.status_code == 403:
            return {
                "error": "forbidden",
                "message": "This operation is not available on your current plan.",
                "upgrade_url": "https://jobless.dev/dashboard/premium",
            }
        if resp.status_code == 404:
            return {
                "error": "not_found",
                "message": "The requested resource was not found.",
            }
        if resp.status_code == 429:
            try:
                body = resp.json()
            except Exception:
                body = {}
            return {
                "error": "rate_limit_exceeded",
                "message": body.get(
                    "detail",
                    "You've hit the Jobless free tier daily limit. "
                    "Upgrade to Pro at https://jobless.dev/dashboard/premium "
                    "for unlimited matches.",
                ),
                "upgrade_url": "https://jobless.dev/dashboard/premium",
            }
        if resp.status_code >= 500:
            return {
                "error": "server_error",
                "message": f"Jobless server error ({resp.status_code}). Try again in a moment.",
            }

        # 2xx — return the JSON body as-is (includes MCP metadata fields
        # like `tier`, `matches_remaining_today`, or the `no_resume` error
        # surfaced by BestMatchedJobsView at the application level).
        try:
            return resp.json()
        except Exception:
            return {
                "error": "invalid_response",
                "message": f"Unexpected non-JSON response: {resp.text[:500]}",
            }

    def close(self) -> None:
        self._client.close()
