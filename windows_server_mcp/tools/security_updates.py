from windows_server_mcp.shell import run

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
def get_windows_update_status() -> str:
    """
    Check pending Windows updates, reboot requirement, and recent update history using Windows Update COM APIs.
    """
    script = r"""
$session = New-Object -ComObject Microsoft.Update.Session
$searcher = $session.CreateUpdateSearcher()
$pending = $searcher.Search("IsInstalled=0 and Type='Software'")
$historyCount = [Math]::Min(10, $searcher.GetTotalHistoryCount())
$history = $searcher.QueryHistory(0, $historyCount) | Select-Object Date,Title,ResultCode
$rebootRequired = Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired'
[PSCustomObject]@{
  PendingUpdates = $pending.Updates.Count
  RebootRequired = $rebootRequired
  RecentHistory = $history
} | Format-List | Out-String -Width 240
"""
    return _run_powershell(script, timeout=90) or "No Windows Update status returned."


@windows_server_mcp_tool()
def list_installed_updates(max_updates: int = 100) -> str:
    """List installed Windows updates and hotfixes with install dates."""
    script = (
        f"Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First {max_updates} "
        "HotFixID,Description,InstalledBy,InstalledOn | Format-Table -AutoSize | Out-String -Width 200"
    )
    return _run_powershell(script) or "No installed updates found."


@windows_server_mcp_tool()
def get_security_status() -> str:
    """
    Summarize Defender, firewall, BitLocker, Secure Boot, and UAC status where available.
    """
    script = r"""
$defender = Get-MpComputerStatus -ErrorAction SilentlyContinue |
  Select-Object AMServiceEnabled,AntivirusEnabled,RealTimeProtectionEnabled,AntispywareEnabled,QuickScanAge,FullScanAge,ComputerState
$firewall = Get-NetFirewallProfile -ErrorAction SilentlyContinue |
  Select-Object Name,Enabled,DefaultInboundAction,DefaultOutboundAction
$bitlocker = Get-BitLockerVolume -ErrorAction SilentlyContinue |
  Select-Object MountPoint,VolumeStatus,ProtectionStatus,EncryptionPercentage
$secureBoot = try { Confirm-SecureBootUEFI } catch { "Unavailable" }
$uac = Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System' -Name EnableLUA -ErrorAction SilentlyContinue |
  Select-Object EnableLUA
"Defender:"
$defender | Format-List | Out-String -Width 200
"Firewall:"
$firewall | Format-Table -AutoSize | Out-String -Width 200
"BitLocker:"
$bitlocker | Format-Table -AutoSize | Out-String -Width 200
"SecureBoot: $secureBoot"
"UAC:"
$uac | Format-List | Out-String -Width 200
"""
    return _run_powershell(script) or "No security status returned."


@windows_server_mcp_tool()
def scan_with_defender(scan_type: str = "quick", path: str = "") -> str:
    """
    Start a Microsoft Defender scan.
    Args:
        scan_type: 'quick', 'full', or 'custom'.
        path: Required for custom scans.
    """
    if scan_type not in {"quick", "full", "custom"}:
        return "Error: scan_type must be 'quick', 'full', or 'custom'."

    if scan_type == "quick":
        script = "Start-MpScan -ScanType QuickScan"
    elif scan_type == "full":
        script = "Start-MpScan -ScanType FullScan"
    else:
        if not path:
            return "Error: path is required for custom scans."
        escaped_path = path.replace("'", "''")
        script = f"Start-MpScan -ScanType CustomScan -ScanPath '{escaped_path}'"

    output = _run_powershell(script, timeout=30)
    return output or f"Microsoft Defender {scan_type} scan started."
