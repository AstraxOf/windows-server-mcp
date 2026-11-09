<!-- mcp-name: io.github.astraxof/windows-server-mcp -->
<div align="center">

# 🪟 Windows Server MCP

**Let your AI assistant inspect, diagnose and manage your Windows PC: 100 tools, local, over stdio.**

[![English](https://img.shields.io/badge/English-Click-2563eb?style=flat-square)](README.md)
[![Español](https://img.shields.io/badge/Español-Clic-eab308?style=flat-square)](README.es.md)

[![CI](https://github.com/AstraxOf/windows-server-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/AstraxOf/windows-server-mcp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/windows-server-mcp?style=flat-square&logo=pypi&logoColor=white&color=3775A9)](https://pypi.org/project/windows-server-mcp/)
![License MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-10%20%7C%2011%20%7C%20Server-0078D4?style=flat-square&logo=windows&logoColor=white)
![Tools](https://img.shields.io/badge/tools-100-success?style=flat-square)

[![Telegram](https://img.shields.io/badge/Telegram-Channel-26A5E4?style=flat-square&logo=telegram&logoColor=white)](https://t.me/AstraxMCP)
[![YouTube](https://img.shields.io/badge/YouTube-@AstraxOf-FF0000?style=flat-square&logo=youtube&logoColor=white)](https://youtube.com/@AstraxOf)
[![Website](https://img.shields.io/badge/astrabots.pro-0f766e?style=flat-square&logo=googlechrome&logoColor=white)](https://astrabots.pro)

</div>

---

**Windows Server MCP** is a [Model Context Protocol](https://modelcontextprotocol.io) server with **100 tools** for local Windows diagnostics, cleanup, hardware, security and administration. It works with Claude Desktop, Cursor, VS Code and any MCP client, and nothing leaves your PC.

> [!IMPORTANT]
> The server runs with the privileges of the account that starts it. Some tools can delete files, edit the Registry, manage services or run PowerShell. **Start with the read-only and dry-run tools.**

## 🚀 Install

```powershell
pip install windows-server-mcp
```

Requires Windows 10/11/Server and Python 3.10+. From source: `git clone https://github.com/AstraxOf/windows-server-mcp.git`, then `pip install -e .`.

## 🔌 Connect your client

Add this to your MCP client config (Claude Desktop: `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "windows-server": {
      "command": "windows-server-mcp",
      "args": []
    }
  }
}
```

If the command isn't on your `PATH`, use `"command": "C:\\path\\to\\python.exe"` with `"args": ["-m", "windows_server_mcp.server"]`.

## 🛠️ What it can do

| Area | Examples |
|---|---|
| 📊 **Task manager** | CPU, GPU, memory, disk, processes, suspend / resume / kill |
| 🧹 **Storage** | Largest files, duplicates, old files, Recycle Bin cleanup |
| 🖥️ **Hardware** | GPU, `nvidia-smi`, displays, drivers, thermals, battery |
| 🛡️ **Security** | Defender, firewall, BitLocker, Secure Boot, Windows Update |
| ⚙️ **Admin** | Services, startup items, scheduled tasks, event logs, restore points |
| 🌐 **Network** | Interfaces, ports, latency, firewall rules |
| 👩‍💻 **Dev & shell** | Python/Node, env vars, clipboard, screenshots, PowerShell |

Full list in [docs/TOOLS.md](docs/TOOLS.md).

## 🔐 Safety

| Level | Examples |
|---|---|
| 🟢 **Read-only** | `disk_cleanup_report`, `get_security_status`, `list_scheduled_tasks` |
| 🟡 **Previewable** | `safe_delete_by_pattern` (`dry_run=true`), Recycle Bin deletes |
| 🔴 **Sharp** | `execute_powershell`, Registry writes, service changes, kill process |

See [docs/SECURITY_MODEL.md](docs/SECURITY_MODEL.md) before using it with an assistant you don't fully trust.

## 🩺 Troubleshooting

| Symptom | Fix |
|---|---|
| `windows-server-mcp` is not recognized | Activate your venv, or use `python -m windows_server_mcp.server`. |
| A tool says access denied | It needs an elevated terminal. Only elevate if you trust the client. |
| The client shows no tools | Restart it completely and check its MCP logs (`%LOCALAPPDATA%\windows-server-mcp\server.log`). |

## 🧑‍💻 Development

```powershell
pip install -e . pytest
python -m pytest -q tests
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) and [docs/PUBLISHING.md](docs/PUBLISHING.md). Report security issues privately via [SECURITY.md](SECURITY.md).

<div align="center">

[![Telegram Channel](https://img.shields.io/badge/Telegram-Official%20channel-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/AstraxMCP)
[![YouTube](https://img.shields.io/badge/YouTube-@AstraxOf-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtube.com/@AstraxOf)
[![Email](https://img.shields.io/badge/Email-avpn497%40gmail.com-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:avpn497@gmail.com)

</div>

## 🙏 Credits & License

Built on the original work of **[Ahmed Laminou Amadou](https://github.com/AhmedLaminou)**, the original author and maintainer. Maintained by Rufus · [@AstraxOf](https://github.com/AstraxOf) · [astrabots.pro](https://astrabots.pro).

**[MIT License](LICENSE)** · Copyright © 2026 Ahmed Laminou Amadou
