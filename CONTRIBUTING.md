# Contributing

Thanks for helping improve Windows Management MCP Server.

## Development Workflow

1. Create a virtual environment.
2. Install the package in editable mode.
3. Make focused changes.
4. Run the Python compile check.
5. Compile the VS Code extension if extension files changed.
6. Update docs when tools or behavior change.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -e .
.\venv\Scripts\python.exe -m compileall windows_server_mcp
pip install pytest
.\venv\Scripts\python.exe -m pytest -q tests
```

For the VS Code extension:

```powershell
cd vscode-extension
npm install
npm run compile
```

## Tool Safety Guidelines

- Prefer read-only report tools first.
- Add `dry_run` defaults for destructive or broad mutation tools.
- Clearly document privilege requirements.
- Avoid permanent deletion when Recycle Bin behavior is possible.
- Keep PowerShell commands scoped and parameterized.

## Pull Requests

Please include:

- What changed.
- Which tools are affected.
- Verification commands run.
- Any Administrator privilege requirements.
