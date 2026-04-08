"""
Tests for the Jobless MCP client + tool wrappers.

These tests mock api.jobless.dev with respx so they run offline and
don't depend on the real backend. They cover the happy path, the
no_resume error surfaced by BestMatchedJobsView, rate limit 429s,
invalid API key 401s, and network errors.
"""

import os

import httpx
import pytest
import respx


# Set a dummy API key before importing the client — the client raises
# ValueError at construction time if the key is missing, so we need this
# to be set before any JoblessClient() calls.
os.environ["JOBLESS_API_KEY"] = "jbl_test_key_abc123"


from jobless_mcp.client import JoblessClient  # noqa: E402


@pytest.fixture
def client():
    c = JoblessClient()
    yield c
    c.close()


@respx.mock
def test_get_best_matches_happy_path(client):
    respx.get("https://api.jobless.dev/jobs/best-matches/").mock(
        return_value=httpx.Response(
            200,
            json={
                "matches": [
                    {
                        "id": "abc-123",
                        "title": "Senior ML Engineer",
                        "company": "Anthropic",
                        "location": "Remote",
                        "score": 94,
                    }
                ],
                "total_matches": 1,
                "page": 1,
                "page_size": 10,
                "tier": "free",
                "matches_used_today": 1,
                "matches_remaining_today": 99,
            },
        )
    )
    result = client.get("/jobs/best-matches/", params={"page": 1, "page_size": 10})
    assert result["matches"][0]["title"] == "Senior ML Engineer"
    assert result["matches_remaining_today"] == 99
    assert result["tier"] == "free"


@respx.mock
def test_get_best_matches_no_resume(client):
    respx.get("https://api.jobless.dev/jobs/best-matches/").mock(
        return_value=httpx.Response(
            200,
            json={
                "matches": [],
                "total_matches": 0,
                "error": "no_resume",
                "message": "You haven't uploaded a resume yet.",
                "onboarding_url": "https://jobless.dev/onboarding",
            },
        )
    )
    result = client.get("/jobs/best-matches/")
    assert result["error"] == "no_resume"
    assert "onboarding_url" in result


@respx.mock
def test_rate_limit_returns_structured_error(client):
    respx.get("https://api.jobless.dev/jobs/best-matches/").mock(
        return_value=httpx.Response(
            429, json={"detail": "Daily rate limit exceeded"}
        )
    )
    result = client.get("/jobs/best-matches/")
    assert result["error"] == "rate_limit_exceeded"
    assert "upgrade_url" in result
    assert result["upgrade_url"] == "https://jobless.dev/dashboard/premium"


@respx.mock
def test_invalid_key_returns_unauthorized(client):
    respx.get("https://api.jobless.dev/jobs/best-matches/").mock(
        return_value=httpx.Response(401, json={"detail": "Invalid token"})
    )
    result = client.get("/jobs/best-matches/")
    assert result["error"] == "unauthorized"
    assert "jobless.dev/mcp" in result["message"]


@respx.mock
def test_forbidden_returns_upgrade_hint(client):
    respx.get("https://api.jobless.dev/jobs/best-matches/").mock(
        return_value=httpx.Response(403)
    )
    result = client.get("/jobs/best-matches/")
    assert result["error"] == "forbidden"
    assert "upgrade_url" in result


@respx.mock
def test_not_found_on_get_job(client):
    respx.get("https://api.jobless.dev/jobs/missing-id/").mock(
        return_value=httpx.Response(404)
    )
    result = client.get("/jobs/missing-id/")
    assert result["error"] == "not_found"


@respx.mock
def test_server_error_returns_retry_hint(client):
    respx.get("https://api.jobless.dev/jobs/best-matches/").mock(
        return_value=httpx.Response(503)
    )
    result = client.get("/jobs/best-matches/")
    assert result["error"] == "server_error"
    assert "503" in result["message"]


@respx.mock
def test_invalid_json_response(client):
    respx.get("https://api.jobless.dev/jobs/best-matches/").mock(
        return_value=httpx.Response(200, text="not json at all")
    )
    result = client.get("/jobs/best-matches/")
    assert result["error"] == "invalid_response"


@respx.mock
def test_network_error_is_caught(client):
    respx.get("https://api.jobless.dev/jobs/best-matches/").mock(
        side_effect=httpx.ConnectError("Connection refused")
    )
    result = client.get("/jobs/best-matches/")
    assert result["error"] == "network_error"


def test_client_requires_api_key():
    """JoblessClient should raise if no API key is provided at all."""
    with pytest.MonkeyPatch.context() as mp:
        mp.delenv("JOBLESS_API_KEY", raising=False)
        with pytest.raises(ValueError, match="JOBLESS_API_KEY"):
            JoblessClient()


def test_client_accepts_explicit_api_key():
    c = JoblessClient(api_key="jbl_explicit_key")
    assert c.api_key == "jbl_explicit_key"
    c.close()


def test_client_accepts_custom_base_url():
    c = JoblessClient(api_key="jbl_test", base_url="http://localhost:8000")
    assert c.base_url == "http://localhost:8000"
    c.close()


def test_client_strips_trailing_slash_from_base_url():
    c = JoblessClient(api_key="jbl_test", base_url="http://localhost:8000/")
    assert c.base_url == "http://localhost:8000"
    c.close()
