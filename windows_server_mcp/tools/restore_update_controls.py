from windows_server_mcp.shell import run

from windows_server_mcp.registry import windows_server_mcp_tool


def _run_powershell(script: str, timeout: int = 120) -> str:
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
def list_restore_points(max_points: int = 20) -> str:
    """List recent Windows system restore points."""
    script = (
        f"Get-ComputerRestorePoint -ErrorAction SilentlyContinue | "
        f"Sort-Object CreationTime -Descending | Select-Object -First {max_points} "
        "SequenceNumber,Description,RestorePointType,CreationTime | "
        "Format-Table -AutoSize | Out-String -Width 220"
    )
    return _run_powershell(script) or "No restore points found or System Protection is disabled."


@windows_server_mcp_tool()
def get_system_protection_status() -> str:
    """Return System Protection and restore configuration status."""
    script = r"""
"Restore points:"
Get-ComputerRestorePoint -ErrorAction SilentlyContinue |
  Sort-Object CreationTime -Descending |
  Select-Object -First 5 SequenceNumber,Description,CreationTime |
  Format-Table -AutoSize | Out-String -Width 220
"Shadow copy storage:"
vssadmin list shadowstorage 2>$null
"""
    return _run_powershell(script) or "No system protection status returned."


@windows_server_mcp_tool()
def create_restore_point(description: str = "Windows MCP restore point") -> str:
    """
    Create a Windows system restore point.
    Requires System Protection to be enabled and may require Administrator privileges.
    """
    escaped_description = description.replace("'", "''")
    script = f"Checkpoint-Computer -Description '{escaped_description}' -RestorePointType 'MODIFY_SETTINGS'"
    output = _run_powershell(script, timeout=180)
    return output or f"Restore point requested: '{description}'."


@windows_server_mcp_tool()
def install_windows_updates(dry_run: bool = True, max_updates: int = 25) -> str:
    """
    Preview or install available Windows software updates through Windows Update COM APIs.
    Args:
        dry_run: Defaults to true. When false, downloads and installs the listed updates.
        max_updates: Maximum updates to process.
    """
    if dry_run:
        script = f"""
$session = New-Object -ComObject Microsoft.Update.Session
$searcher = $session.CreateUpdateSearcher()
$result = $searcher.Search("IsInstalled=0 and Type='Software'")
$rows = for ($i = 0; $i -lt $result.Updates.Count -and $i -lt {max_updates}; $i++) {{
  $u = $result.Updates.Item($i)
  [PSCustomObject]@{{Index=$i; Title=$u.Title; RebootRequired=$u.RebootRequired; EulaAccepted=$u.EulaAccepted}}
}}
$rows | Format-Table -AutoSize | Out-String -Width 260
"""
        return _run_powershell(script, timeout=120) or "No software updates available."

    script = f"""
$session = New-Object -ComObject Microsoft.Update.Session
$searcher = $session.CreateUpdateSearcher()
$result = $searcher.Search("IsInstalled=0 and Type='Software'")
$updates = New-Object -ComObject Microsoft.Update.UpdateColl
for ($i = 0; $i -lt $result.Updates.Count -and $i -lt {max_updates}; $i++) {{
  $u = $result.Updates.Item($i)
  if (-not $u.EulaAccepted) {{ $u.AcceptEula() }}
  [void]$updates.Add($u)
}}
if ($updates.Count -eq 0) {{ "No updates to install."; exit }}
$downloader = $session.CreateUpdateDownloader()
$downloader.Updates = $updates
$downloadResult = $downloader.Download()
$installer = $session.CreateUpdateInstaller()
$installer.Updates = $updates
$installResult = $installer.Install()
[PSCustomObject]@{{
  DownloadResult = $downloadResult.ResultCode
  InstallResult = $installResult.ResultCode
  RebootRequired = $installResult.RebootRequired
  UpdatesProcessed = $updates.Count
}} | Format-List | Out-String -Width 220
"""
    return _run_powershell(script, timeout=3600) or "Windows Update install command completed with no output."


@windows_server_mcp_tool()
def install_driver_updates(dry_run: bool = True, max_updates: int = 10) -> str:
    """
    Preview or install available driver updates through Windows Update COM APIs.
    Args:
        dry_run: Defaults to true. When false, downloads and installs listed driver updates.
    """
    update_type = "Driver"
    if dry_run:
        script = f"""
$session = New-Object -ComObject Microsoft.Update.Session
$searcher = $session.CreateUpdateSearcher()
$result = $searcher.Search("IsInstalled=0 and Type='{update_type}'")
$rows = for ($i = 0; $i -lt $result.Updates.Count -and $i -lt {max_updates}; $i++) {{
  $u = $result.Updates.Item($i)
  [PSCustomObject]@{{Index=$i; Title=$u.Title; DriverClass=$u.DriverClass; DriverManufacturer=$u.DriverManufacturer; DriverModel=$u.DriverModel}}
}}
$rows | Format-Table -AutoSize | Out-String -Width 260
"""
        return _run_powershell(script, timeout=120) or "No driver updates available."

    script = f"""
$session = New-Object -ComObject Microsoft.Update.Session
$searcher = $session.CreateUpdateSearcher()
$result = $searcher.Search("IsInstalled=0 and Type='{update_type}'")
$updates = New-Object -ComObject Microsoft.Update.UpdateColl
for ($i = 0; $i -lt $result.Updates.Count -and $i -lt {max_updates}; $i++) {{
  $u = $result.Updates.Item($i)
  if (-not $u.EulaAccepted) {{ $u.AcceptEula() }}
  [void]$updates.Add($u)
}}
if ($updates.Count -eq 0) {{ "No driver updates to install."; exit }}
$downloader = $session.CreateUpdateDownloader()
$downloader.Updates = $updates
$downloadResult = $downloader.Download()
$installer = $session.CreateUpdateInstaller()
$installer.Updates = $updates
$installResult = $installer.Install()
[PSCustomObject]@{{
  DownloadResult = $downloadResult.ResultCode
  InstallResult = $installResult.ResultCode
  RebootRequired = $installResult.RebootRequired
  UpdatesProcessed = $updates.Count
}} | Format-List | Out-String -Width 220
"""
    return _run_powershell(script, timeout=3600) or "Driver update install command completed with no output."
