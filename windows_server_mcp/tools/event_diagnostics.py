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
def get_event_logs(
    log_name: str = "System",
    level: str = "Error",
    hours: int = 24,
    max_events: int = 25,
    source: str = "",
) -> str:
    """
    Query recent Windows Event Viewer entries.
    Args:
        log_name: Event log name, such as 'System' or 'Application'.
        level: 'Critical', 'Error', 'Warning', 'Information', or 'all'.
        hours: Lookback window in hours.
        max_events: Maximum entries to return.
        source: Optional provider/source filter.
    """
    level_map = {"Critical": 1, "Error": 2, "Warning": 3, "Information": 4}
    level_part = "" if level == "all" else f"; Level={level_map.get(level, 2)}"
    escaped_source = source.replace("'", "''")
    escaped_log_name = log_name.replace("'", "''")
    provider_part = f"; ProviderName='{escaped_source}'" if source else ""
    script = (
        "$start=(Get-Date).AddHours(-" + str(hours) + "); "
        f"Get-WinEvent -FilterHashtable @{{LogName='{escaped_log_name}'; StartTime=$start"
        f"{level_part}{provider_part}}} -MaxEvents {max_events} | "
        "Select-Object TimeCreated,ProviderName,Id,LevelDisplayName,Message | "
        "Format-List | Out-String -Width 240"
    )
    output = _run_powershell(script)
    return output or "No matching events found."


@windows_server_mcp_tool()
def diagnose_recent_crashes(hours: int = 72, max_events: int = 30) -> str:
    """
    Pull recent application crashes, system critical events, and Windows Error Reporting entries.
    """
    script = (
        "$start=(Get-Date).AddHours(-" + str(hours) + "); "
        "$filters=@("
        "@{LogName='Application'; StartTime=$start; Level=2},"
        "@{LogName='System'; StartTime=$start; Level=1}"
        "); "
        "$events=@(); foreach($f in $filters){ $events += Get-WinEvent -FilterHashtable $f -ErrorAction SilentlyContinue }; "
        "$events | Where-Object { $_.ProviderName -match 'Application Error|Windows Error Reporting|BugCheck|Display|Service Control Manager|Kernel-Power' -or $_.LevelDisplayName -eq 'Critical' } | "
        f"Sort-Object TimeCreated -Descending | Select-Object -First {max_events} TimeCreated,LogName,ProviderName,Id,LevelDisplayName,Message | "
        "Format-List | Out-String -Width 260"
    )
    output = _run_powershell(script, timeout=60)
    return output or f"No crash-related events found in the last {hours} hours."
