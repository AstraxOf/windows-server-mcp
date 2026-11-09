# Security Policy

## Supported Versions

Security fixes are handled on the latest released version.

## Reporting a Vulnerability

Please do not open a public issue for a sensitive vulnerability.

If this repository is hosted publicly, use GitHub private vulnerability reporting if enabled, or contact the maintainer through the repository owner profile.

## Security Notes

This server can expose powerful local Windows capabilities to an MCP client. Treat the MCP client as part of the trusted computing base.

Do not run the server as Administrator unless required for the task.

Review [docs/SECURITY_MODEL.md](docs/SECURITY_MODEL.md) for tool risk classes and recommended client policy.
