[![Install in Cursor](https://img.shields.io/badge/Install_in-Cursor-000000?style=flat-square&logoColor=white)](https://cursor.com/en/install-mcp?name=jobless&config=eyJ1cmwiOiAiaHR0cHM6Ly9tY3Auam9ibGVzcy5kZXYvbWNwIn0%3D)
[![Install in VS Code](https://img.shields.io/badge/Install_in-VS_Code-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=jobless&config=%7B%22type%22%3A%20%22http%22%2C%20%22url%22%3A%20%22https%3A//mcp.jobless.dev/mcp%22%7D)

# Jobless MCP

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/bendza/jobless-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/bendza/jobless-mcp/actions/workflows/ci.yml)

> Personalized job search inside Claude. Get ranked job matches based on your actual skills, not keywords. Works in Claude Code, Desktop, Cursor, Windsurf, VS Code, Gemini CLI, and more.

**[Get your API key](https://jobless.dev/mcp)** | **[Documentation](https://jobless.dev/mcp)** | **[Issues](https://github.com/bendza/jobless-mcp/issues)**

## Why Jobless MCP?

### Without Jobless

- Searching job boards manually with keyword filters
- Getting irrelevant results because "Python" matches a snake handler job
- No idea how well you actually match a role until you read the whole posting
- Context-switching between your AI assistant and browser tabs

### With Jobless

Ask Claude naturally and get jobs ranked against your actual resume:

```
What are my best job matches today?
```

Claude calls `get_best_matches` and returns:

```
Top 5 matches personalized to your resume:

1. [94%] Staff AI Engineer - Anthropic
   Remote | Python, PyTorch, Distributed Systems
   role 92% | skills 95% | seniority 96%

2. [91%] Senior ML Engineer - Vercel
   Remote | Go, Postgres, Kubernetes, LLM infra
   role 88% | skills 93% | seniority 91%

3. [89%] Founding Engineer - Cursor
   San Francisco | TypeScript, React, LLMs
   role 92% | skills 88% | seniority 87%
```

10,000+ jobs indexed across Greenhouse, Ashby, Lever, and more. Updated daily.

## Quick Start

### 1. Get your API key

Visit **[jobless.dev/mcp](https://jobless.dev/mcp)** -- drop your resume and get an API key instantly (no signup required for 10 matches/day).

### 2. Connect your client

Remote server URL:

```
https://mcp.jobless.dev/mcp
```

<details>
<summary><b>Claude Code</b></summary>

```bash
claude mcp add jobless --url https://mcp.jobless.dev/mcp --header "Authorization: Bearer YOUR_API_KEY"
```

</details>

<details>
<summary><b>Claude Desktop</b></summary>

Jobless is available as a Claude Connector. Go to **Settings > Connectors** and search for **Jobless**.

Or add manually to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "jobless": {
      "url": "https://mcp.jobless.dev/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

Restart Claude Desktop after saving.

</details>

<details>
<summary><b>Cursor</b></summary>

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "jobless": {
      "url": "https://mcp.jobless.dev/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

</details>

<details>
<summary><b>VS Code</b></summary>

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "jobless": {
      "type": "http",
      "url": "https://mcp.jobless.dev/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

</details>

<details>
<summary><b>Windsurf</b></summary>

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "jobless": {
      "serverUrl": "https://mcp.jobless.dev/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

</details>

<details>
<summary><b>Zed</b></summary>

Add to Zed settings:

```json
{
  "context_servers": {
    "jobless": {
      "url": "https://mcp.jobless.dev/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

</details>

<details>
<summary><b>Gemini CLI</b></summary>

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "jobless": {
      "httpUrl": "https://mcp.jobless.dev/mcp"
    }
  }
}
```

</details>

<details>
<summary><b>OpenCode</b></summary>

Add to `opencode.json`:

```json
{
  "mcp": {
    "jobless": {
      "type": "remote",
      "url": "https://mcp.jobless.dev/mcp",
      "enabled": true
    }
  }
}
```

</details>

<details>
<summary><b>Warp</b></summary>

Settings > MCP Servers > Add MCP Server:

```json
{
  "jobless": {
    "url": "https://mcp.jobless.dev/mcp",
    "headers": {
      "Authorization": "Bearer YOUR_API_KEY"
    }
  }
}
```

</details>

<details>
<summary><b>Kiro</b></summary>

Add to `~/.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "jobless": {
      "url": "https://mcp.jobless.dev/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

</details>

<details>
<summary><b>Local install (pip, privacy mode)</b></summary>

Run the server locally as a subprocess. Your API key never touches `mcp.jobless.dev`:

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

</details>

<details>
<summary><b>Other clients (generic remote MCP)</b></summary>

If your client supports remote MCP servers:

```json
{
  "mcpServers": {
    "jobless": {
      "url": "https://mcp.jobless.dev/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

If your client only supports stdio, use [mcp-remote](https://github.com/anthropics/mcp-remote) as a bridge:

```json
{
  "mcpServers": {
    "jobless": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.jobless.dev/mcp", "--header", "Authorization: Bearer YOUR_API_KEY"]
    }
  }
}
```

</details>

## Tools

Three tools, zero configuration. Claude decides which to call based on what you ask.

### `get_best_matches`

Get your top personalized job matches ranked against your resume.

**Best for:** Daily job check-ins, exploring what's out there, finding roles that match your skills

**Prompt example:**
> "What are my best job matches today?"

**Usage:**
```json
{
  "name": "get_best_matches",
  "arguments": {
    "limit": 10,
    "page": 1
  }
}
```

**Returns:**
```json
{
  "matches": [
    {
      "id": "6374df4a-...",
      "title": "Staff AI Engineer",
      "company": "Anthropic",
      "location": "Remote",
      "link": "https://boards.greenhouse.io/anthropic/jobs/...",
      "match_score": 94.2
    }
  ],
  "total_matches": 487,
  "page": 1,
  "page_size": 10,
  "tier": "free",
  "matches_used_today": 1,
  "matches_remaining_today": 49
}
```

### `get_job`

Get full details for a specific job.

**Best for:** Deep-diving a match, preparing for applications, comparing roles

**Prompt example:**
> "Tell me more about the Anthropic role"

**Usage:**
```json
{
  "name": "get_job",
  "arguments": {
    "job_id": "6374df4a-..."
  }
}
```

**Returns:** Full job description, required tech stack, seniority fit, location details, salary range (when available), and the direct application URL.

### `get_profile_status`

Check your tier, daily usage, and resume state.

**Best for:** Start of conversation, checking remaining quota, debugging auth issues

**Prompt example:**
> "How many matches do I have left today?"

**Usage:**
```json
{
  "name": "get_profile_status",
  "arguments": {}
}
```

**Returns:**
```json
{
  "has_resume": true,
  "tier": "free",
  "is_verified": true,
  "matches_used_today": 3,
  "matches_remaining_today": 47,
  "daily_limit": 50,
  "resets_at": "2026-04-10T00:00:00Z"
}
```

## Pricing

| | Quickstart | Free | Pro |
|---|---|---|---|
| **Daily matches** | 10 | 50 | Unlimited |
| **Signup required** | No | Yes | Yes |
| **Ranking** | Dual KNN | Dual KNN | ColBERT reranking |
| **Price** | Free | Free | $19/mo |

[Upgrade at jobless.dev/dashboard/premium](https://jobless.dev/dashboard/premium)

## Architecture

This package is a **thin wrapper** (~150 LOC) around the Jobless REST API. Two modes:

- **Stdio (local):** launched as a subprocess by your client. API key stays on your machine.
- **Streamable HTTP (hosted):** `mcp.jobless.dev`. No install needed. Bearer token in every request.

Both call the same closed-source Jobless backend (`api.jobless.dev`) which holds the OpenSearch index, Jina embeddings, and ranking models.

```
              github.com/bendza/jobless-mcp
            (MIT, ~150 LOC, this repo)
                      |
         +------------+------------+
         |                         |
   Local stdio mode         Hosted HTTP mode
   (pip install)            (mcp.jobless.dev)
         |                         |
         +------------+------------+
                      v
            api.jobless.dev (Django)
                      v
        OpenSearch + Postgres + Redis
```

## Self-Hosting

```bash
pip install jobless-mcp
JOBLESS_MCP_TRANSPORT=http \
JOBLESS_API_BASE=https://your-api.example.com \
PORT=8100 \
jobless-mcp
```

## Development

```bash
git clone https://github.com/bendza/jobless-mcp.git
cd jobless-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
```

13 tests covering the client layer. All tests mock the API with [respx](https://github.com/lundberg/respx) and run offline in <100ms.

## Links

- **[jobless.dev/mcp](https://jobless.dev/mcp)** -- API key + install commands
- **[jobless.dev](https://jobless.dev)** -- the main product
- **[Issues](https://github.com/bendza/jobless-mcp/issues)** -- bug reports + feature requests

## License

MIT -- see [LICENSE](LICENSE).

[![Star History Chart](https://api.star-history.com/svg?repos=bendza/jobless-mcp&type=Date)](https://www.star-history.com/#bendza/jobless-mcp&Date)
