import ctypes
import datetime
import platform
import sys
from importlib.metadata import PackageNotFoundError, version

import psutil
from windows_server_mcp.registry import registered_tools, windows_server_mcp_tool


def _dist_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "not installed"


def _is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


@windows_server_mcp_tool()
def get_system_info() -> str:
    """Retrieve fundamental Windows system information (OS version, PC name, Uptime)."""
    uname = platform.uname()
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.datetime.now() - boot_time
    return (f"OS: {uname.system} {uname.release} (Version: {uname.version})\n"
            f"PC Name: {uname.node}\nArchitecture: {uname.machine}\n"
            f"Processor: {uname.processor}\nBoot Time: {boot_time}\nUptime: {uptime}")

@windows_server_mcp_tool()
def get_hardware_info() -> str:
    """Retrieve deep hardware specifications including CPU, RAM limits, and disk geometries."""
    mem = psutil.virtual_memory()
    cpu_cores = psutil.cpu_count(logical=False)
    cpu_threads = psutil.cpu_count(logical=True)
    cpu_freq = psutil.cpu_freq()
    
    res = [
        f"CPU Cores: {cpu_cores} (Logical: {cpu_threads})",
        f"CPU Freq: {cpu_freq.current:.2f}MHz (Max: {cpu_freq.max:.2f}MHz)" if cpu_freq else "CPU Freq: Unknown",
        f"Memory Total: {mem.total / (1024**3):.2f} GB",
        f"Memory Used: {mem.used / (1024**3):.2f} GB ({mem.percent}%)"
    ]
    
    res.append("\nDisks:")
    for part in psutil.disk_partitions(all=False):
        if 'cdrom' in part.opts or part.fstype == '': continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
            res.append(f"  {part.device} [{part.fstype}] {usage.used/(1024**3):.1f}GB / {usage.total/(1024**3):.1f}GB ({usage.percent}%)")
        except PermissionError: pass
        
    return "\n".join(res)

@windows_server_mcp_tool()
def get_server_status() -> str:
    """Report the server version, MCP SDK version, Python version, number of loaded tools and whether the server is running as Administrator. Call this first to know which tools will need elevation."""
    elevated = _is_admin()
    return (f"Server: windows-server-mcp {_dist_version('windows-server-mcp')}\n"
            f"MCP SDK: mcp {_dist_version('mcp')}\n"
            f"Python: {sys.version.split()[0]}\n"
            f"Tools loaded: {len(registered_tools)}\n"
            f"Administrator: {'yes' if elevated else 'no'}\n"
            f"Elevation-only tools available: {'yes' if elevated else 'no (restart the client as Administrator if a tool reports access denied)'}")
