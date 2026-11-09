import psutil
from windows_server_mcp.shell import TIMEOUT_RETURNCODE, run
import json
from windows_server_mcp.registry import windows_server_mcp_tool

@windows_server_mcp_tool()
def get_cpu_usage() -> str:
    """Get the current overall and per-core CPU usage percentage."""
    overall = psutil.cpu_percent(interval=1.0)
    per_core = psutil.cpu_percent(interval=1.0, percpu=True)
    cores_str = ", ".join([f"Core {i}: {p}%" for i, p in enumerate(per_core)])
    return f"Total CPU Usage: {overall}%\nPer Core: {cores_str}"

@windows_server_mcp_tool()
def get_gpu_usage() -> str:
    """
    Get the current GPU usage using Windows Performance Counters via PowerShell.
    (This attempts to fetch general 3D engine utilization).
    """
    try:
        # PowerShell command to get GPU utilization
        ps_cmd = "Get-Counter '\\GPU Engine(*engtype_3D)\\Utilization Percentage' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty CounterSamples | Where-Object {$_.CookedValue -gt 0} | Select-Object InstanceName, CookedValue | ConvertTo-Json"
        result = run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd], capture_output=True, text=True, timeout=30)
        if result.returncode == TIMEOUT_RETURNCODE:
            return "Error reading GPU performance counters: " + result.stderr.strip()
        if not result.stdout.strip():
            return "GPU Usage: 0% or unable to read Performance Counters."
            
        data = json.loads(result.stdout)
        if isinstance(data, dict):
            data = [data]
            
        output = ["Active GPU Engines:"]
        for item in data:
            # Clean up the long instance name
            name = item.get("InstanceName", "Unknown").split("_")[0]
            val = item.get("CookedValue", 0)
            output.append(f"  {name}: {val:.2f}%")
        return "\n".join(output)
    except Exception as e:
        return f"Error fetching GPU usage: {str(e)}"

@windows_server_mcp_tool()
def get_memory_usage() -> str:
    """Get the current RAM usage."""
    mem = psutil.virtual_memory()
    total_gb = mem.total / (1024 ** 3)
    used_gb = mem.used / (1024 ** 3)
    free_gb = mem.available / (1024 ** 3)
    return f"Memory: {used_gb:.2f} GB used / {total_gb:.2f} GB total ({mem.percent}% used)\nAvailable: {free_gb:.2f} GB"

@windows_server_mcp_tool()
def get_disk_usage() -> str:
    """Get disk usage statistics for all physical drives."""
    disks = []
    for part in psutil.disk_partitions(all=False):
        if 'cdrom' in part.opts or part.fstype == '':
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
            total = usage.total / (1024**3)
            used = usage.used / (1024**3)
            free = usage.free / (1024**3)
            disks.append(f"Drive {part.device} [{part.fstype}] - {used:.1f}GB used / {total:.1f}GB total ({usage.percent}% full) - {free:.1f}GB free")
        except PermissionError:
            continue
    return "\n".join(disks)

@windows_server_mcp_tool()
def get_top_processes(sort_by: str = "cpu", count: int = 15) -> str:
    """
    List the top processes currently running.
    Args:
        sort_by: 'cpu' or 'memory'
        count: number of processes to return
    """
    procs = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            if proc.info['name']:
                procs.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
    if sort_by.lower() == "memory":
        procs.sort(key=lambda p: p['memory_percent'] or 0, reverse=True)
    else:
        procs.sort(key=lambda p: p['cpu_percent'] or 0, reverse=True)
        
    lines = [f"{'PID':<8} {'NAME':<35} {'CPU%':<8} {'MEM%':<8}"]
    lines.append("-" * 65)
    for p in procs[:count]:
        cpu = f"{p['cpu_percent']:.1f}" if p['cpu_percent'] is not None else "0.0"
        mem = f"{p['memory_percent']:.1f}" if p['memory_percent'] is not None else "0.0"
        name = str(p['name'])[:34] 
        lines.append(f"{p['pid']:<8} {name:<35} {cpu:<8} {mem:<8}")
        
    return "\n".join(lines)
