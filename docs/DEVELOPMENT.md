# Development Guide

## Local Setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -e .
```

## Run the Server

```powershell
windows-server-mcp
```

or:

```powershell
python -m windows_server_mcp.server
```

## Verify Python

```powershell
.\venv\Scripts\python.exe -m compileall windows_server_mcp
```

## Run the Tests

```powershell
pip install pytest
python -m pytest -q tests
```

The tests also run on Linux/macOS (`tests/conftest.py` stubs `winreg` and
`ctypes.windll`); no tool is executed, they only check imports and registration.

## Supported MCP SDK Versions

The server supports `mcp>=1.12,<3`:

| `mcp` | Server class | Import used |
|---|---|---|
| 2.x | `MCPServer` | `mcp.server.mcpserver` |
| 1.x | `FastMCP` | `mcp.server.fastmcp` |

`windows_server_mcp/server.py` picks the right one automatically. Do not import
either class anywhere else: keep the SDK-specific code in that one file.

## Verify Registered Tools

```powershell
.\venv\Scripts\python.exe -c "from windows_server_mcp.registry import register_all_tools, registered_tools; Dummy=type('Dummy',(),{'tool':lambda self: (lambda f:f)}); register_all_tools(Dummy()); print(len(registered_tools))"
```

Expected count: `100`.

## Verify VS Code Extension

```powershell
cd vscode-extension
npm install
npm run compile
```

## Adding a Tool

1. Create or update a module under `windows_server_mcp/tools/`.
2. Decorate the function with `@windows_server_mcp_tool()`.
3. Import the module in `windows_server_mcp/registry.py`.
4. Run the compile and tool-count checks.
5. Update `docs/TOOLS.md` and the README capability summary.

Prefer read-only tools or dry-run defaults for system-changing workflows.
