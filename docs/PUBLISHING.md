# Publishing Guide

This project is ready for GitHub and close to ready for the MCP Registry. The remaining thing you must decide is the final GitHub namespace.

The current docs assume:

```text
io.github.astraxof/windows-server-mcp
https://github.com/AstraxOf/windows-server-mcp
```

If your GitHub username changes, update these places before publishing:

- `README.md`: the `<!-- mcp-name: ... -->` marker.
- `server.json`: `name`, `websiteUrl`, and `repository.url`.
- `pyproject.toml`: project URLs.

## 1. Publish to GitHub

```powershell
git init
git add .
git commit -m "Initial Windows Management MCP server"
git branch -M main
git remote add origin https://github.com/AstraxOf/windows-server-mcp.git
git push -u origin main
```

Recommended GitHub settings:

- Add topics: `mcp`, `mcp-server`, `windows`, `automation`, `task-manager`, `system-administration`.
- Enable Issues.
- Add a repository description matching `pyproject.toml`.
- Add the MIT license and security policy files from this repo.

## 2. Verify the Package Locally

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -e .
windows-server-mcp
```

Compile checks:

```powershell
.\venv\Scripts\python.exe -m compileall windows_server_mcp
cd vscode-extension
npm install
npm run compile
```

## 3. Build and Publish to PyPI

The MCP Registry hosts metadata, not the package artifact. Publish the Python package to PyPI first.

This project publishes to PyPI as **`windows-server-mcp`** (version `1.0.0`).

### Option A: automatic (GitHub Actions + Trusted Publishing, recommended)

1. On <https://pypi.org/manage/account/publishing/> add a **pending publisher**:
   - PyPI project name: `windows-server-mcp`
   - Owner: `AstraxOf` · Repository: `windows-server-mcp`
   - Workflow name: `publish.yml` · Environment name: `pypi`
2. In the GitHub repo go to **Settings > Environments** and create an environment named `pypi`.
3. Create a GitHub **Release** with tag `v1.0.0` (or run the workflow manually from the Actions tab).
4. The `Publish to PyPI` workflow builds, checks and uploads the package. No token is needed.

For every new version: bump `version` in `pyproject.toml` and `server.json` (both places), commit, and publish a new Release. PyPI never accepts the same version twice.

### Option B: manual

```powershell
pip install build twine
python -m build
twine check dist/*
twine upload dist/*
```

PyPI ownership verification for the MCP Registry depends on the README containing this marker:

```html
<!-- mcp-name: io.github.astraxof/windows-server-mcp -->
```

The marker must match `server.json` exactly.

## 4. Install mcp-publisher

On Windows PowerShell:

```powershell
$arch = if ([System.Runtime.InteropServices.RuntimeInformation]::ProcessArchitecture -eq "Arm64") { "arm64" } else { "amd64" }
Invoke-WebRequest -Uri "https://github.com/modelcontextprotocol/registry/releases/latest/download/mcp-publisher_windows_$arch.tar.gz" -OutFile "mcp-publisher.tar.gz"
tar xf mcp-publisher.tar.gz mcp-publisher.exe
Remove-Item mcp-publisher.tar.gz
```

Move `mcp-publisher.exe` to a directory on `PATH`, then verify:

```powershell
mcp-publisher --help
```

## 5. Publish to the MCP Registry

Authenticate with GitHub:

```powershell
mcp-publisher login github
```

Publish the registry metadata:

```powershell
mcp-publisher publish
```

Verify through the Registry API:

```powershell
Invoke-WebRequest "https://registry.modelcontextprotocol.io/v0.1/servers?search=io.github.astraxof/windows-server-mcp"
```

## Troubleshooting

- If registry validation says package verification failed, confirm the PyPI-rendered README contains the exact `mcp-name:` marker.
- If publishing says you do not have permission, confirm the `io.github.<username>/...` namespace matches the GitHub account used by `mcp-publisher login github`.
- If the package URL is wrong, confirm `server.json` uses `registryType: "pypi"` and `identifier: "windows-server-mcp"`.
