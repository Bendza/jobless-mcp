# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 0.1.x   | Yes       |

## Reporting a Vulnerability

If you discover a security vulnerability in jobless-mcp, please report it responsibly:

1. **Do not** open a public GitHub issue
2. Email **hello@jobless.dev** with details
3. Include steps to reproduce if possible

We will acknowledge your report within 48 hours and provide a timeline for a fix.

## Scope

This package is a thin MCP wrapper (~150 LOC) that forwards tool calls to `api.jobless.dev` over HTTPS. The attack surface is limited to:

- API key handling (stored in env vars or HTTP headers, never logged)
- Input validation on tool arguments (limit, page, job_id)
- HTTPS connections to api.jobless.dev (certificate validation via httpx defaults)

The Jobless backend (api.jobless.dev) is closed-source. Report backend vulnerabilities to the same email address.
