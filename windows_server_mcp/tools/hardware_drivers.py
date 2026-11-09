from windows_server_mcp.shell import TIMEOUT_RETURNCODE, run
import json
import shutil
from windows_server_mcp.registry import windows_server_mcp_tool

@windows_server_mcp_tool()
def get_gpu_details() -> str:
    """
    Retrieve detailed information about installed GPUs, including Driver Version, VRAM, and Resolution.
    """
    try:
        ps_cmd = "Get-CimInstance Win32_VideoController -ErrorAction SilentlyContinue | Select-Object Name, DriverVersion, VideoProcessor, AdapterRAM, CurrentHorizontalResolution, CurrentVerticalResolution | ConvertTo-Json"
        result = run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd], capture_output=True, text=True)
        if result.returncode == TIMEOUT_RETURNCODE:
            return result.stderr.strip()
        if not result.stdout.strip():
            return "No GPU information found."
            
        data = json.loads(result.stdout)
        if isinstance(data, dict):
            data = [data]
            
        lines = []
        for gpu in data:
            vram_gb = gpu.get("AdapterRAM", 0) / (1024**3) if gpu.get("AdapterRAM") else 0
            res = f"{gpu.get('CurrentHorizontalResolution', 'Unknown')}x{gpu.get('CurrentVerticalResolution', 'Unknown')}"
            
            lines.append(f"GPU Name: {gpu.get('Name', 'Unknown')}")
            lines.append(f"  Processor: {gpu.get('VideoProcessor', 'Unknown')}")
            lines.append(f"  Driver Version: {gpu.get('DriverVersion', 'Unknown')}")
            lines.append(f"  VRAM: {vram_gb:.2f} GB")
            lines.append(f"  Current Resolution: {res}")
            lines.append("-" * 40)
            
        return "\n".join(lines)
    except Exception as e:
        return f"Error retrieving GPU details: {str(e)}"

@windows_server_mcp_tool()
def list_installed_drivers(device_class: str = "") -> str:
    """
    List installed device drivers on the system.
    
    Args:
        device_class: Filter by class (e.g., 'Display', 'Net', 'Media', 'System'). 
                      Leave empty for all (WARNING: 'all' returns a massive list).
    """
    try:
        if device_class:
            ps_cmd = f"Get-CimInstance Win32_PnPSignedDriver | Where-Object DeviceClass -eq '{device_class}' | Select-Object DeviceName, Manufacturer, DriverVersion, DeviceClass | ConvertTo-Json"
        else:
            ps_cmd = "Get-CimInstance Win32_PnPSignedDriver | Select-Object DeviceName, Manufacturer, DriverVersion, DeviceClass | Select-Object -First 50 | ConvertTo-Json"
            
        result = run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd], capture_output=True, text=True)
        if result.returncode == TIMEOUT_RETURNCODE:
            return result.stderr.strip()
        if not result.stdout.strip():
            return f"No drivers found for class '{device_class}'."
            
        data = json.loads(result.stdout)
        if isinstance(data, dict):
            data = [data]
            
        lines = [f"{'DEVICE NAME':<50} | {'MANUFACTURER':<20} | {'VERSION':<15}"]
        lines.append("-" * 90)
        
        for d in data:
            name = (d.get("DeviceName") or "Unknown")[:47]
            mfg = (d.get("Manufacturer") or "Unknown")[:17]
            ver = (d.get("DriverVersion") or "Unknown")[:14]
            lines.append(f"{name:<50} | {mfg:<20} | {ver:<15}")
            
        if not device_class and len(data) == 50:
            lines.append("\n... (Truncated to 50 results. Provide a device_class like 'Display' or 'Net' for specific drivers).")
            
        return "\n".join(lines)
    except Exception as e:
        return f"Error retrieving drivers: {str(e)}"


@windows_server_mcp_tool()
def get_gpu_processes() -> str:
    """
    Show processes currently appearing in Windows GPU engine utilization counters.
    """
    ps_cmd = r"""
$samples = Get-Counter '\GPU Engine(*)\Utilization Percentage' -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty CounterSamples |
  Where-Object { $_.CookedValue -gt 0 }
$rows = foreach ($sample in $samples) {
  $pidValue = $null
  if ($sample.InstanceName -match 'pid_(\d+)') { $pidValue = [int]$Matches[1] }
  $process = if ($pidValue) { Get-Process -Id $pidValue -ErrorAction SilentlyContinue } else { $null }
  [PSCustomObject]@{
    PID = $pidValue
    ProcessName = if ($process) { $process.ProcessName } else { 'Unknown' }
    Engine = $sample.InstanceName
    UtilizationPercent = [Math]::Round($sample.CookedValue, 2)
  }
}
$rows | Sort-Object UtilizationPercent -Descending | Format-Table -AutoSize | Out-String -Width 240
"""
    try:
        result = run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd], capture_output=True, text=True)
        if result.returncode == TIMEOUT_RETURNCODE:
            return result.stderr.strip()
        if result.returncode != 0:
            return result.stderr.strip() or "Error reading GPU process counters."
        return result.stdout.strip() or "No active GPU engine process usage found."
    except Exception as e:
        return f"Error retrieving GPU processes: {str(e)}"


@windows_server_mcp_tool()
def get_display_configuration() -> str:
    """
    Return attached display and video-controller configuration.
    """
    ps_cmd = r"""
"Video Controllers:"
Get-CimInstance Win32_VideoController -ErrorAction SilentlyContinue |
  Select-Object Name,VideoProcessor,DriverVersion,CurrentHorizontalResolution,CurrentVerticalResolution,CurrentRefreshRate,AdapterRAM |
  Format-Table -AutoSize | Out-String -Width 240
"Desktop Monitors:"
Get-CimInstance Win32_DesktopMonitor -ErrorAction SilentlyContinue |
  Select-Object Name,MonitorType,ScreenWidth,ScreenHeight,PixelsPerXLogicalInch,PixelsPerYLogicalInch |
  Format-Table -AutoSize | Out-String -Width 240
"""
    try:
        result = run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd], capture_output=True, text=True)
        if result.returncode == TIMEOUT_RETURNCODE:
            return result.stderr.strip()
        if result.returncode != 0:
            return result.stderr.strip() or "Error reading display configuration."
        return result.stdout.strip() or "No display configuration found."
    except Exception as e:
        return f"Error retrieving display configuration: {str(e)}"


@windows_server_mcp_tool()
def get_gpu_performance_summary() -> str:
    """
    Summarize GPU utilization and adapter memory counters where Windows exposes them.
    """
    ps_cmd = r"""
"GPU Engine Utilization:"
Get-Counter '\GPU Engine(*)\Utilization Percentage' -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty CounterSamples |
  Where-Object { $_.CookedValue -gt 0 } |
  Select-Object InstanceName,@{Name='UtilizationPercent';Expression={[Math]::Round($_.CookedValue,2)}} |
  Sort-Object UtilizationPercent -Descending |
  Select-Object -First 20 |
  Format-Table -AutoSize | Out-String -Width 240
"GPU Adapter Memory:"
Get-Counter '\GPU Adapter Memory(*)\*' -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty CounterSamples |
  Select-Object InstanceName,Path,@{Name='Bytes';Expression={[Math]::Round($_.CookedValue,0)}} |
  Format-Table -AutoSize | Out-String -Width 240
"""
    try:
        result = run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd], capture_output=True, text=True)
        if result.returncode == TIMEOUT_RETURNCODE:
            return result.stderr.strip()
        if result.returncode != 0:
            return result.stderr.strip() or "Error reading GPU performance counters."
        return result.stdout.strip() or "No GPU performance counters returned."
    except Exception as e:
        return f"Error retrieving GPU performance summary: {str(e)}"


@windows_server_mcp_tool()
def get_nvidia_smi_summary() -> str:
    """
    Return NVIDIA GPU details from nvidia-smi when the NVIDIA CLI is installed.
    """
    nvidia_smi = shutil.which("nvidia-smi")
    if not nvidia_smi:
        return "nvidia-smi was not found on PATH. This system may not have an NVIDIA GPU or NVIDIA tools installed."

    query = (
        "name,driver_version,pstate,temperature.gpu,utilization.gpu,utilization.memory,"
        "memory.total,memory.used,power.draw,power.limit"
    )
    result = run(
        [nvidia_smi, f"--query-gpu={query}", "--format=csv,noheader,nounits"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        return result.stderr.strip() or "nvidia-smi returned an error."

    headers = [
        "Name", "Driver", "PState", "TempC", "GPU%", "Mem%", "MemTotalMB",
        "MemUsedMB", "PowerW", "PowerLimitW",
    ]
    lines = [", ".join(headers)]
    lines.extend(line.strip() for line in result.stdout.splitlines() if line.strip())
    return "\n".join(lines) if len(lines) > 1 else "nvidia-smi returned no GPU rows."


@windows_server_mcp_tool()
def get_gpu_vendor_report() -> str:
    """
    Try vendor-specific GPU probes, then fall back to Windows GPU/display counters.
    """
    lines = ["NVIDIA:"]
    lines.append(get_nvidia_smi_summary())
    lines.extend([
        "",
        "Windows GPU details:",
        get_gpu_details(),
        "",
        "Windows GPU performance:",
        get_gpu_performance_summary(),
    ])
    return "\n".join(lines)
