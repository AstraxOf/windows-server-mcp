# Reference Review

This project used two public references while shaping the repository structure:

- MarkItDown: https://github.com/microsoft/markitdown
- MCP Registry: https://github.com/modelcontextprotocol/registry

## Patterns Adopted from MarkItDown

MarkItDown is a mature Python project with a clear public-facing README, package structure, security warning, contribution notes, license, support, and security policy.

Useful patterns copied into this project:

- Lead with what the project does and who it is for.
- Put a security warning near the top when the tool performs local I/O or privileged work.
- Include installation, usage, optional client setup, development, and contribution sections.
- Keep standard community files at the root: `LICENSE`, `SECURITY.md`, `SUPPORT.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`.
- Use `.github/` for CI and issue templates.

## Patterns Adopted from the MCP Registry Docs

The MCP Registry documentation currently treats the registry as metadata only; the actual package artifact must be published elsewhere first. For this project that means PyPI first, then MCP Registry metadata.

Useful patterns applied here:

- `server.json` uses the current registry schema URL.
- `server.json` uses a registry-style name: `io.github.astraxof/windows-server-mcp`.
- `server.json` declares a PyPI package entry with stdio transport.
- `README.md` contains the PyPI package verification marker:

```html
<!-- mcp-name: io.github.astraxof/windows-server-mcp -->
```

Before publishing, change `ahmed` if the final GitHub username differs.

## Intentional Differences

- This is not a monorepo, so there is no `packages/` split like MarkItDown.
- This is Windows-specific, so CI uses `windows-latest`.
- The README links to a separate tool catalog instead of listing every tool inline.
- Many tools are administrative, so the security model is more explicit than a typical library README.
