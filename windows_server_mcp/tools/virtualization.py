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


def _run_windows_command(command: list[str], timeout: int = 30) -> str:
    result = run(command, capture_output=True, timeout=timeout)
    output = result.stdout or result.stderr
    if not output:
        return ""

    if b"\x00" in output[:100]:
        return output.decode("utf-16le", errors="replace").strip()
    return output.decode(errors="replace").strip()


@windows_server_mcp_tool()
def get_wsl_status() -> str:
    """Return WSL version/status details where WSL is installed."""
    output = _run_windows_command(["wsl", "--status"])
    return output or "WSL status is unavailable. WSL may not be installed."


@windows_server_mcp_tool()
def list_wsl_distros() -> str:
    """List installed WSL distributions and their running/stopped state."""
    output = _run_windows_command(["wsl", "--list", "--verbose"])
    return output or "No WSL distributions found or WSL is unavailable."


@windows_server_mcp_tool()
def list_hyperv_vms() -> str:
    """List Hyper-V virtual machines if the Hyper-V PowerShell module is available."""
    script = (
        "Get-VM -ErrorAction SilentlyContinue | "
        "Select-Object Name,State,CPUUsage,MemoryAssigned,Uptime,Status,Version | "
        "Format-Table -AutoSize | Out-String -Width 220"
    )
    return _run_powershell(script) or "No Hyper-V VMs found, or Hyper-V module is unavailable."


@windows_server_mcp_tool()
def get_windows_optional_features_status() -> str:
    """Show status for common virtualization-related Windows optional features."""
    script = r"""
$names = @(
  'Microsoft-Windows-Subsystem-Linux',
  'VirtualMachinePlatform',
  'Microsoft-Hyper-V-All',
  'HypervisorPlatform',
  'Containers',
  'Windows-Defender-ApplicationGuard'
)
foreach ($name in $names) {
  Get-WindowsOptionalFeature -Online -FeatureName $name -ErrorAction SilentlyContinue |
    Select-Object FeatureName,State,RestartRequired
}
"""
    return _run_powershell(script) or "No optional feature status returned."
