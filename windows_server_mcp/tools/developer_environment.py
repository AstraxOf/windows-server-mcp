import os
import shutil
from windows_server_mcp.shell import run
import winreg

import psutil

from windows_server_mcp.registry import windows_server_mcp_tool


@windows_server_mcp_tool()
def list_env_vars(scope: str = "process") -> str:
    """
    Inspect environment variables.
    Args:
        scope: 'process', 'user', or 'machine'.
    """
    if scope == "process":
        items = sorted(os.environ.items())
        return "\n".join(f"{key}={value}" for key, value in items)

    hive = winreg.HKEY_CURRENT_USER if scope == "user" else winreg.HKEY_LOCAL_MACHINE
    key_path = "Environment" if scope == "user" else r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
    if scope not in {"user", "machine"}:
        return "Error: scope must be 'process', 'user', or 'machine'."

    try:
        with winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ) as key:
            values = []
            for index in range(winreg.QueryInfoKey(key)[1]):
                name, value, _ = winreg.EnumValue(key, index)
                values.append(f"{name}={value}")
            return "\n".join(sorted(values))
    except Exception as exc:
        return f"Error reading environment variables: {exc}"


@windows_server_mcp_tool()
def set_env_var(name: str, value: str, scope: str = "user") -> str:
    """
    Set a user or machine environment variable.
    Args:
        name: Variable name.
        value: Variable value. Use an empty string to clear the variable.
        scope: 'user' or 'machine'.
    """
    if scope not in {"user", "machine"}:
        return "Error: scope must be 'user' or 'machine'."

    hive = winreg.HKEY_CURRENT_USER if scope == "user" else winreg.HKEY_LOCAL_MACHINE
    key_path = "Environment" if scope == "user" else r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
    try:
        with winreg.OpenKey(hive, key_path, 0, winreg.KEY_SET_VALUE) as key:
            if value == "":
                winreg.DeleteValue(key, name)
            else:
                winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
        return f"Set {scope} environment variable '{name}'. Restart apps to pick up the change."
    except FileNotFoundError:
        return f"Environment variable '{name}' was not found."
    except PermissionError:
        return "Error: Access denied. Machine scope usually requires Administrator privileges."
    except Exception as exc:
        return f"Error setting environment variable: {exc}"


def _where_all(command: str) -> list[str]:
    result = run(["where", command], capture_output=True, text=True)
    if result.returncode != 0:
        path = shutil.which(command)
        return [path] if path else []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


@windows_server_mcp_tool()
def list_python_installs() -> str:
    """Find Python installations visible through PATH and the Python launcher."""
    lines: list[str] = []
    for exe in _where_all("python") + _where_all("py"):
        try:
            result = run([exe, "--version"], capture_output=True, text=True, timeout=10)
            version = result.stdout.strip() or result.stderr.strip()
        except Exception as exc:
            version = f"Error: {exc}"
        lines.append(f"{exe} -> {version}")

    try:
        launcher = run(["py", "-0p"], capture_output=True, text=True, timeout=10)
        if launcher.stdout.strip():
            lines.append("\nPython launcher registrations:")
            lines.append(launcher.stdout.strip())
    except Exception:
        pass

    return "\n".join(lines) if lines else "No Python installations found on PATH."


@windows_server_mcp_tool()
def list_node_installs() -> str:
    """Find Node.js/npm installations visible through PATH."""
    lines: list[str] = []
    for command in ["node", "npm", "npx"]:
        for exe in _where_all(command):
            try:
                result = run([exe, "--version"], capture_output=True, text=True, timeout=10)
                version = result.stdout.strip() or result.stderr.strip()
            except Exception as exc:
                version = f"Error: {exc}"
            lines.append(f"{exe} -> {version}")
    return "\n".join(lines) if lines else "No Node.js tools found on PATH."


@windows_server_mcp_tool()
def check_dev_ports(ports: str = "3000,5173,8000,8080,9229") -> str:
    """
    Check common developer ports and show owning processes.
    Args:
        ports: Comma-separated ports to check.
    """
    target_ports = {int(port.strip()) for port in ports.split(",") if port.strip().isdigit()}
    lines = [f"{'PORT':<8} {'STATUS':<15} {'PID':<8} {'PROCESS':<25} EXE"]
    lines.append("-" * 90)

    found_ports = set()
    for conn in psutil.net_connections(kind="inet"):
        if not conn.laddr or conn.laddr.port not in target_ports:
            continue
        found_ports.add(conn.laddr.port)
        name = "Unknown"
        exe = ""
        if conn.pid:
            try:
                proc = psutil.Process(conn.pid)
                name = proc.name()
                exe = proc.exe()
            except Exception:
                pass
        lines.append(f"{conn.laddr.port:<8} {conn.status:<15} {str(conn.pid or '-'):<8} {name[:24]:<25} {exe}")

    for port in sorted(target_ports - found_ports):
        lines.append(f"{port:<8} {'free':<15} {'-':<8} {'-':<25} -")

    return "\n".join(lines)
