from windows_server_mcp.shell import run

from windows_server_mcp.registry import windows_server_mcp_tool


def _run_powershell(script: str, timeout: int = 90) -> str:
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
def list_problem_devices() -> str:
    """List PnP devices that Windows reports as not OK or currently errored."""
    script = r"""
Get-PnpDevice -ErrorAction SilentlyContinue |
  Where-Object { $_.Status -ne 'OK' } |
  Select-Object Status,Class,FriendlyName,InstanceId |
  Format-Table -AutoSize | Out-String -Width 240
"""
    return _run_powershell(script) or "No problem devices found."


@windows_server_mcp_tool()
def get_driver_update_candidates(max_updates: int = 50) -> str:
    """
    Search Windows Update for available driver updates without installing them.
    """
    script = f"""
$session = New-Object -ComObject Microsoft.Update.Session
$searcher = $session.CreateUpdateSearcher()
$result = $searcher.Search("IsInstalled=0 and Type='Driver'")
$rows = for ($i = 0; $i -lt $result.Updates.Count -and $i -lt {max_updates}; $i++) {{
  $u = $result.Updates.Item($i)
  [PSCustomObject]@{{
    Index = $i
    Title = $u.Title
    DriverClass = $u.DriverClass
    DriverManufacturer = $u.DriverManufacturer
    DriverModel = $u.DriverModel
    RebootRequired = $u.RebootRequired
  }}
}}
$rows | Format-Table -AutoSize | Out-String -Width 260
"""
    return _run_powershell(script, timeout=120) or "No available driver updates found."


@windows_server_mcp_tool()
def get_driver_inventory_report(device_class: str = "", max_drivers: int = 100) -> str:
    """
    Return installed driver inventory with dates and versions, optionally filtered by device class.
    """
    escaped_device_class = device_class.replace("'", "''")
    where = f"| Where-Object DeviceClass -eq '{escaped_device_class}'" if device_class else ""
    script = (
        f"Get-CimInstance Win32_PnPSignedDriver -ErrorAction SilentlyContinue {where} | "
        f"Select-Object -First {max_drivers} DeviceName,DeviceClass,Manufacturer,DriverProviderName,DriverVersion,DriverDate,InfName | "
        "Format-Table -AutoSize | Out-String -Width 260"
    )
    return _run_powershell(script) or "No driver inventory returned."
