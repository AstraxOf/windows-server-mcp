<div align="center">

# 🪟 Windows Server MCP

**Deja que tu asistente de IA inspeccione, diagnostique y administre tu PC con Windows: 100 herramientas, locales, por stdio.**

[![English](https://img.shields.io/badge/English-Click-2563eb?style=flat-square)](README.md)
[![Español](https://img.shields.io/badge/Español-Clic-eab308?style=flat-square)](README.es.md)

[![CI](https://github.com/AstraxOf/windows-server-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/AstraxOf/windows-server-mcp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/windows-server-mcp?style=flat-square&logo=pypi&logoColor=white&color=3775A9)](https://pypi.org/project/windows-server-mcp/)
![License MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-10%20%7C%2011%20%7C%20Server-0078D4?style=flat-square&logo=windows&logoColor=white)
![Tools](https://img.shields.io/badge/herramientas-100-success?style=flat-square)

[![Telegram](https://img.shields.io/badge/Telegram-Canal-26A5E4?style=flat-square&logo=telegram&logoColor=white)](https://t.me/AstraxMCP)
[![YouTube](https://img.shields.io/badge/YouTube-@AstraxOf-FF0000?style=flat-square&logo=youtube&logoColor=white)](https://youtube.com/@AstraxOf)
[![Web](https://img.shields.io/badge/astrabots.pro-0f766e?style=flat-square&logo=googlechrome&logoColor=white)](https://astrabots.pro)

</div>

---

**Windows Server MCP** es un servidor del [Model Context Protocol](https://modelcontextprotocol.io) con **100 herramientas** para diagnóstico, limpieza, hardware, seguridad y administración local de Windows. Funciona con Claude Desktop, Cursor, VS Code y cualquier cliente MCP, y nada sale de tu PC.

> [!IMPORTANT]
> El servidor se ejecuta con los privilegios de la cuenta que lo inicia. Algunas herramientas pueden borrar archivos, editar el Registro, gestionar servicios o ejecutar PowerShell. **Empieza con las herramientas de solo lectura y `dry_run`.**

## 🚀 Instalación

```powershell
pip install windows-server-mcp
```

Requiere Windows 10/11/Server y Python 3.10+. Desde el código: `git clone https://github.com/AstraxOf/windows-server-mcp.git` y luego `pip install -e .`.

## 🔌 Conecta tu cliente

Añade esto a la configuración MCP de tu cliente (Claude Desktop: `claude_desktop_config.json`):

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

Si el comando no está en el `PATH`, usa `"command": "C:\\ruta\\a\\python.exe"` con `"args": ["-m", "windows_server_mcp.server"]`.

## 🛠️ Qué puede hacer

| Área | Ejemplos |
|---|---|
| 📊 **Administrador de tareas** | CPU, GPU, memoria, disco, procesos, suspender / reanudar / terminar |
| 🧹 **Almacenamiento** | Archivos grandes, duplicados, archivos antiguos, Papelera |
| 🖥️ **Hardware** | GPU, `nvidia-smi`, pantallas, drivers, temperatura, batería |
| 🛡️ **Seguridad** | Defender, firewall, BitLocker, Secure Boot, Windows Update |
| ⚙️ **Administración** | Servicios, inicio, tareas programadas, registros de eventos, puntos de restauración |
| 🌐 **Red** | Interfaces, puertos, latencia, reglas de firewall |
| 👩‍💻 **Dev y shell** | Python/Node, variables de entorno, portapapeles, capturas, PowerShell |

Lista completa en [docs/TOOLS.md](docs/TOOLS.md).

## 🔐 Seguridad

| Nivel | Ejemplos |
|---|---|
| 🟢 **Solo lectura** | `disk_cleanup_report`, `get_security_status`, `list_scheduled_tasks` |
| 🟡 **Previsualizable** | `safe_delete_by_pattern` (`dry_run=true`), borrado a la Papelera |
| 🔴 **Delicadas** | `execute_powershell`, escrituras en el Registro, cambios de servicios, matar procesos |

Lee [docs/SECURITY_MODEL.md](docs/SECURITY_MODEL.md) antes de usarlo con un asistente en el que no confíes del todo.

## 🩺 Solución de problemas

| Síntoma | Solución |
|---|---|
| `windows-server-mcp` no se reconoce | Activa tu venv, o usa `python -m windows_server_mcp.server`. |
| Una herramienta dice acceso denegado | Necesita una terminal elevada. Eleva solo si confías en el cliente. |
| El cliente no muestra herramientas | Reinícialo por completo y revisa sus logs MCP (`%LOCALAPPDATA%\windows-server-mcp\server.log`). |

## 🧑‍💻 Desarrollo

```powershell
pip install -e . pytest
python -m pytest -q tests
```

Mira [CONTRIBUTING.md](CONTRIBUTING.md), [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) y [docs/PUBLISHING.md](docs/PUBLISHING.md). Reporta problemas de seguridad en privado vía [SECURITY.md](SECURITY.md).

<div align="center">

[![Canal de Telegram](https://img.shields.io/badge/Telegram-Canal%20oficial-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/AstraxMCP)
[![YouTube](https://img.shields.io/badge/YouTube-@AstraxOf-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtube.com/@AstraxOf)
[![Email](https://img.shields.io/badge/Email-avpn497%40gmail.com-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:avpn497@gmail.com)

</div>

## 🙏 Créditos y licencia

Construido sobre el trabajo original de **[Ahmed Laminou Amadou](https://github.com/AhmedLaminou)**, autor y mantenedor original. Mantenido por Rufus · [@AstraxOf](https://github.com/AstraxOf) · [astrabots.pro](https://astrabots.pro).

**[Licencia MIT](LICENSE)** · Copyright © 2026 Ahmed Laminou Amadou
