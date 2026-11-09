from windows_server_mcp.shell import run

import psutil

from windows_server_mcp.registry import windows_server_mcp_tool


def _run_powershell(script: str, timeout: int = 60) -> str:
    result = run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        return result.stderr.strip() or result.stdout.strip()
    return result.stdout.strip()


@windows_server_mcp_tool()
def get_smart_disk_health() -> str:
    """
    Report physical disk health using Storage and WMI SMART status where available.
    """
    script = r"""
"Physical disks:"
Get-PhysicalDisk -ErrorAction SilentlyContinue |
  Select-Object FriendlyName,SerialNumber,MediaType,BusType,HealthStatus,OperationalStatus,Size |
  Format-Table -AutoSize | Out-String -Width 240
"SMART failure prediction:"
Get-CimInstance -Namespace root\wmi -ClassName MSStorageDriver_FailurePredictStatus -ErrorAction SilentlyContinue |
  Select-Object InstanceName,PredictFailure,Reason |
  Format-Table -AutoSize | Out-String -Width 240
"Disk drives:"
Get-CimInstance Win32_DiskDrive -ErrorAction SilentlyContinue |
  Select-Object Model,SerialNumber,InterfaceType,MediaType,Status,Size |
  Format-Table -AutoSize | Out-String -Width 240
"""
    return _run_powershell(script) or "No disk health data returned."


@windows_server_mcp_tool()
def get_volume_health() -> str:
    """Return volume/filesystem health, size, and free space."""
    script = r"""
Get-Volume -ErrorAction SilentlyContinue |
  Select-Object DriveLetter,FriendlyName,FileSystem,HealthStatus,OperationalStatus,SizeRemaining,Size |
  Format-Table -AutoSize | Out-String -Width 220
"""
    return _run_powershell(script) or "No volume health data returned."


@windows_server_mcp_tool()
def get_disk_io_counters() -> str:
    """Show per-disk read/write counters since boot."""
    counters = psutil.disk_io_counters(perdisk=True)
    if not counters:
        return "No disk I/O counters found."

    lines = [f"{'DISK':<20} {'READ':>14} {'WRITE':>14} {'READ COUNT':>14} {'WRITE COUNT':>14}"]
    lines.append("-" * 82)
    for disk, stats in counters.items():
        lines.append(
            f"{disk:<20} {stats.read_bytes / (1024 ** 2):>11.2f} MB "
            f"{stats.write_bytes / (1024 ** 2):>10.2f} MB "
            f"{stats.read_count:>14} {stats.write_count:>14}"
        )
    return "\n".join(lines)
