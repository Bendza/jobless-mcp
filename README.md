# jobless-mcp

[![PyPI](https://img.shields.io/pypi/v/jobless-mcp.svg)](https://pypi.org/project/jobless-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Personalized job search inside Claude. Ask Claude what your best job matches are — get ranked results from Jobless's index of 10,000+ jobs across Greenhouse, Ashby, Lever, and more.

## What it does

Jobless MCP gives Claude (Code, Desktop, Cursor, Zed, and any other MCP-aware client) three tools:

- **`get_best_matches`** — your top personalized job matches based on your Jobless resume
- **`get_job`** — full details for any specific job
- **`get_profile_status`** — your tier, daily usage, and resume state

Ask Claude naturally:

> What are my best job matches today?
> Tell me more about the Anthropic one.
> How many matches do I have left today?

Claude calls the right tool, paginates through results, and explains errors in plain language.

## Quick start

### 1. Create a Jobless account + upload your resume

Sign up at [jobless.dev](https://jobless.dev). Upload your resume on the onboarding page — this builds the profile that drives match ranking.

### 2. Get your API key

Visit [jobless.dev/mcp](https://jobless.dev/mcp) — after signing in, your API key is auto-generated and the install commands are pre-filled with it. Copy the one for your client.

### 3. Connect Claude

#### Claude Code

```bash
claude mcp add jobless --url https://mcp.jobless.dev --header "Authorization: Bearer YOUR_API_KEY"
```

#### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "jobless": {
      "url": "https://mcp.jobless.dev",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

Restart Claude Desktop.

#### Cursor

Settings → MCP → Add server, paste the same JSON as Claude Desktop.

#### Local install (optional, privacy mode)

If you'd rather run the server locally as a subprocess:

```bash
pip install jobless-mcp
```

Then in your client config:

```json
{
  "mcpServers": {
    "jobless": {
      "command": "jobless-mcp",
      "env": {
        "JOBLESS_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

The local mode talks directly to `api.jobless.dev` — your key never touches `mcp.jobless.dev`. Same tools, same backend.

## Pricing

### Free tier

- 100 personalized matches per day
- Unlimited `get_job` and `get_profile_status` calls
- Dual KNN ranking (fast)
- All 3 tools

### Pro — $19/mo

- **Unlimited** matches per day
- ColBERT semantic reranking (better quality)
- AI-tailored resumes per job (coming v2)
- AI-generated cover letters (coming v2)

[Upgrade at jobless.dev/dashboard/premium →](https://jobless.dev/dashboard/premium)

## Architecture

This package is a **thin wrapper** around the Jobless REST API. It runs in two modes:

- **Stdio (local)**: launched as a subprocess by your Claude client. Best for privacy — your API key never leaves your machine except in HTTPS calls to `api.jobless.dev`.
- **Streamable HTTP (hosted)**: connects to `mcp.jobless.dev`. No install required. Your Claude client sends the API key in the `Authorization` header, we forward it to the Jobless API.

Both modes call the same closed-source Jobless backend (`api.jobless.dev`) which holds the OpenSearch index, Jina v3 embeddings, ranking models, and all the AI logic. This repo is ~150 lines of Python that translates MCP tool calls into HTTPS requests.

```
                    github.com/bendza/jobless-mcp
                  (MIT, ~150 LOC, this repo)
                            │
           ┌────────────────┴────────────────┐
           │                                 │
   Local stdio mode                  Hosted HTTP mode
   (pip install jobless-mcp)         (mcp.jobless.dev)
           │                                 │
           └────────────────┬────────────────┘
                            ▼
                  api.jobless.dev (Django)
                            ▼
              OpenSearch + Postgres + Redis
```

## Self-hosting

If you want to run your own hosted instance pointing at your own Jobless deployment:

```bash
pip install jobless-mcp
JOBLESS_MCP_TRANSPORT=http \
JOBLESS_API_BASE=https://your-api.example.com \
PORT=8100 \
jobless-mcp
```

Then put any reverse proxy (Caddy, nginx, Traefik) in front of port 8100.

## Development

```bash
git clone https://github.com/bendza/jobless-mcp.git
cd jobless-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

13 tests covering the client layer (happy path, all error codes, network failures, env var handling). All tests mock `api.jobless.dev` with [respx](https://github.com/lundberg/respx) so they run offline in <100ms.

## Tool schemas

### `get_best_matches(limit: int = 10, page: int = 1)`

Returns up to `limit` ranked jobs for the user's profile. Defaults: 10 per call, clamped to [1, 20]. Use `page` for pagination.

**Free tier:** counted against daily 100-call limit.
**Pro tier:** unlimited.

**Success response:**
```json
{
  "matches": [
    {
      "id": "uuid",
      "title": "Senior ML Engineer",
      "company": "Anthropic",
      "location": "Remote",
      "link": "https://...",
      "match_score": 94.2
    }
  ],
  "total_matches": 487,
  "page": 1,
  "page_size": 10,
  "tier": "free",
  "matches_used_today": 1,
  "matches_remaining_today": 99
}
```

**No-resume response:**
```json
{
  "matches": [],
  "error": "no_resume",
  "message": "You haven't uploaded a resume yet.",
  "onboarding_url": "https://jobless.dev/onboarding"
}
```

**Rate limit response:**
```json
{
  "error": "rate_limit_exceeded",
  "message": "Daily rate limit exceeded",
  "upgrade_url": "https://jobless.dev/dashboard/premium"
}
```

### `get_job(job_id: str)`

Returns full details for a specific job UUID. Unlimited on all tiers.

### `get_profile_status()`

Returns `has_resume`, `tier`, `matches_used_today`, `matches_remaining_today`, `resets_at`. Unlimited on all tiers. Useful at the start of a conversation.

## Links

- **[jobless.dev](https://jobless.dev)** — the main product
- **[jobless.dev/mcp](https://jobless.dev/mcp)** — install commands + API key generation
- **[Issues](https://github.com/bendza/jobless-mcp/issues)**
- **[Jobless Server](https://github.com/Bendza/Jobless-server)** — the closed-source backend (for reference, not runnable standalone)

## License

MIT — see [LICENSE](LICENSE).

Copyright © 2026 Belmin Kurtanovic.
