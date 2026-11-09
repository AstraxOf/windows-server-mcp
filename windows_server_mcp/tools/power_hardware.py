from windows_server_mcp.shell import run

from windows_server_mcp.registry import windows_server_mcp_tool


def _run_powershell(script: str, timeout: int = 45) -> str:
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
def get_battery_health() -> str:
    """
    Return battery capacity and charge health from WMI where the hardware exposes it.
    """
    script = r"""
$battery = Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue
$static = Get-CimInstance -Namespace root\wmi -ClassName BatteryStaticData -ErrorAction SilentlyContinue
$full = Get-CimInstance -Namespace root\wmi -ClassName BatteryFullChargedCapacity -ErrorAction SilentlyContinue
$status = Get-CimInstance -Namespace root\wmi -ClassName BatteryStatus -ErrorAction SilentlyContinue
[PSCustomObject]@{
  Battery = $battery | Select-Object Name,Status,BatteryStatus,EstimatedChargeRemaining,EstimatedRunTime
  DesignedCapacity = $static.DesignedCapacity
  FullChargedCapacity = $full.FullChargedCapacity
  CycleCount = $static.CycleCount
  PowerOnline = $status.PowerOnline
  Discharging = $status.Discharging
} | Format-List | Out-String -Width 220
"""
    return _run_powershell(script) or "No battery data found. This may be a desktop or unsupported device."


@windows_server_mcp_tool()
def get_thermal_status() -> str:
    """
    Return thermal zone temperatures and power throttling clues where available.
    """
    script = r"""
$thermal = Get-CimInstance -Namespace root\wmi -ClassName MSAcpi_ThermalZoneTemperature -ErrorAction SilentlyContinue |
  Select-Object InstanceName,@{Name='Celsius';Expression={($_.CurrentTemperature / 10) - 273.15}}
$cpu = Get-CimInstance Win32_Processor -ErrorAction SilentlyContinue |
  Select-Object Name,CurrentClockSpeed,MaxClockSpeed,LoadPercentage
"Thermal Zones:"
$thermal | Format-Table -AutoSize | Out-String -Width 200
"CPU:"
$cpu | Format-Table -AutoSize | Out-String -Width 200
"""
    return _run_powershell(script) or "No thermal status data found."


@windows_server_mcp_tool()
def get_power_plan() -> str:
    """Return the active Windows power plan and available power schemes."""
    result = run(["powercfg", "/L"], capture_output=True, text=True)
    if result.returncode != 0:
        return result.stderr.strip() or "Error reading power plans."
    return result.stdout.strip()


@windows_server_mcp_tool()
def set_power_plan(plan: str) -> str:
    """
    Switch Windows power plan.
    Args:
        plan: 'balanced', 'high_performance', 'power_saver', 'ultimate_performance', or a GUID.
    """
    aliases = {
        "balanced": "381b4222-f694-41f0-9685-ff5bb260df2e",
        "high_performance": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
        "power_saver": "a1841308-3541-4fab-bc81-f71556f20b4a",
        "ultimate_performance": "e9a42b02-d5df-448d-aa00-03f14749eb61",
    }
    guid = aliases.get(plan, plan)
    result = run(["powercfg", "/S", guid], capture_output=True, text=True)
    if result.returncode != 0:
        return result.stderr.strip() or f"Error switching to power plan '{plan}'."
    return f"Active power plan set to '{plan}' ({guid})."
