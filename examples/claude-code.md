# Claude Code setup

Run this command in your terminal (replace `YOUR_API_KEY` with the key from https://jobless.dev/mcp):

```bash
claude mcp add jobless --url https://mcp.jobless.dev --header "Authorization: Bearer YOUR_API_KEY"
```

Then in any Claude Code session, ask:

> What are my best job matches today?

Claude will call `get_best_matches` and return your ranked matches.

## Local install (optional)

If you prefer to run the MCP server locally instead of hitting `mcp.jobless.dev`:

```bash
pip install jobless-mcp
claude mcp add jobless -- env JOBLESS_API_KEY=YOUR_API_KEY jobless-mcp
```

Same tools, same behavior, but the request path is:

```
Claude Code → local jobless-mcp subprocess → https://api.jobless.dev
```

instead of:

```
Claude Code → https://mcp.jobless.dev → https://api.jobless.dev
```

## Verify it's working

```bash
claude mcp list
```

Should show `jobless` in the list. Then start a Claude session and ask about jobs.
