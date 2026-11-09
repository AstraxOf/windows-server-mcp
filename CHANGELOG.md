# Changelog

## 1.0.0 — first release as `windows-server-mcp`

### Added

- **Encoding-safe file tools** (100 tools in total): `read_text_file`, `write_text_file`
  and `normalize_text_file_encoding` always use UTF-8 **without BOM**, so source code and
  emojis are never corrupted by PowerShell 5.1's UTF-16 / ANSI / BOM defaults.

### Fixed

- **Garbled characters in tool output** (accents, emojis, Chinese-looking text): every
  PowerShell call now forces UTF-8 on the console and `$OutputEncoding`, and the output is
  decoded as UTF-8.
- `_harden_stdio` no longer re-points foreign `StreamHandler`s (e.g. pytest's capture
  handlers), which broke test teardown.

### Fixed

- **Tool calls could hang forever and freeze the server.** About half of the
  PowerShell/subprocess calls had no timeout, and children inherited the MCP
  stdio `stdin`. Every external command now goes through
  `windows_server_mcp.shell.run`, which enforces a deadline (60 s by default),
  closes `stdin`, hides console windows and kills the whole process tree on
  timeout, returning a clear "timed out" message instead of hanging.
- `execute_powershell` gains `timeout_seconds` (default 60, max 3600). With
  `require_admin=true` it no longer waits forever on an unseen UAC prompt, runs
  the script from a temp file (fixes quoting breakage) and now returns the
  command's output.
- Tools now run in a worker thread, so on `mcp` 1.x a slow call can no longer
  block the event loop and make the whole server unresponsive.
- **Logging can no longer freeze the server.** Under `pythonw.exe` (launched by a
  bridge), `stderr` is often an unread pipe; once it filled, the next log write
  blocked forever. The server now writes its logs and `stderr` to
  `%LOCALAPPDATA%\windows-server-mcp\server.log` / `stderr.log`. Each tool call
  logs `tool start` / `tool finished`, so a `start` with no `finished` shows
  which tool hung.
- Tool calls have a hard deadline (180 s; longer for installs and for
  `execute_powershell` with a big `timeout_seconds`). If a thread blocks inside
  Python itself the call is abandoned with an error and the server stays alive.
- `find_process_locking_file` scans in a separate, killable process, because
  `psutil.open_files()` can block forever on some Windows handles.
- `get_gpu_usage` and similar tools report a timeout instead of a misleading
  "no data" result.
- **Compatibility with `mcp` 2.x.** The MCP Python SDK v2 (released 2026-07-28)
  renamed `FastMCP` to `MCPServer` and removed the `mcp.server.fastmcp` module
  with no deprecation shim, so a fresh `pip install` crashed on start-up with
  `ModuleNotFoundError`. `server.py` now imports `MCPServer` from
  `mcp.server.mcpserver` and falls back to `FastMCP` on `mcp` 1.x.
- Removed the unused `fastmcp` dependency (the standalone package was never
  imported; the server always used the SDK's built-in class).

### Changed

- Dependency range is now `mcp>=1.12,<3` so the next major release cannot break
  installs silently again.
- Server name shown to clients is now `Windows Management` and the package
  version is reported in the MCP `serverInfo`.
- CI runs on Python 3.10 and 3.13 against both `mcp` 1.x and `mcp` 2.x.

### Added

- `get_server_status` tool (97 tools in total): server and MCP SDK versions, loaded tool count and whether the server is elevated.
- `tests/` with import, tool-count and `list_tools()` checks (they can also be
  run on Linux/macOS thanks to a `conftest.py` that stubs `winreg`/`windll`).
- English and Spanish READMEs (`README.md`, `README.es.md`).

## 0.3.0

- Expanded the server to 96 Windows management tools.
- Added storage cleanup reports and safer Recycle Bin deletion workflows.
- Added GPU, driver, disk health, Windows Update, restore point, WSL, Hyper-V, printer, audio, Bluetooth, firewall, and uninstall maintenance tools.
- Added VS Code extension wrapper.
- Added MCP Registry metadata and publishing documentation.

---

Original project by [Ahmed Laminou Amadou](https://github.com/AhmedLaminou).
