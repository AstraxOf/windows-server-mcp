import socket
from windows_server_mcp.shell import TIMEOUT_RETURNCODE, run

import psutil

from windows_server_mcp.registry import windows_server_mcp_tool


def _proc_name(pid: int | None) -> str:
    if not pid:
        return "System/Unknown"
    try:
        return psutil.Process(pid).name()
    except Exception:
        return "Unknown"


@windows_server_mcp_tool()
def get_network_usage_by_process() -> str:
    """
    Show active network sockets grouped by owning process.
    Windows does not expose per-process byte counters through psutil, so this reports socket activity.
    """
    grouped: dict[int, list[str]] = {}
    for conn in psutil.net_connections(kind="inet"):
        if conn.pid is None:
            continue
        proto = "TCP" if conn.type == socket.SOCK_STREAM else "UDP"
        laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else ""
        raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else ""
        grouped.setdefault(conn.pid, []).append(f"{proto} {laddr} -> {raddr} [{conn.status}]")

    if not grouped:
        return "No process-owned network sockets found."

    lines: list[str] = []
    for pid, sockets in sorted(grouped.items(), key=lambda item: len(item[1]), reverse=True):
        lines.append(f"{_proc_name(pid)} (PID: {pid}) - {len(sockets)} socket(s)")
        lines.extend(f"  {entry}" for entry in sockets[:10])
        if len(sockets) > 10:
            lines.append(f"  ... and {len(sockets) - 10} more")
    return "\n".join(lines[:500])


@windows_server_mcp_tool()
def get_listening_ports() -> str:
    """Show local listening ports, owning PID, process name, and executable path when available."""
    lines = [f"{'PROTO':<5} {'LOCAL ADDRESS':<25} {'PID':<8} {'PROCESS':<25} EXE"]
    lines.append("-" * 110)
    for conn in psutil.net_connections(kind="inet"):
        if conn.status != psutil.CONN_LISTEN:
            continue
        proto = "TCP" if conn.type == socket.SOCK_STREAM else "UDP"
        laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else ""
        name = _proc_name(conn.pid)
        exe = ""
        if conn.pid:
            try:
                exe = psutil.Process(conn.pid).exe()
            except Exception:
                exe = "Unavailable"
        lines.append(f"{proto:<5} {laddr:<25} {str(conn.pid or '-'):<8} {name[:24]:<25} {exe}")
    return "\n".join(lines) if len(lines) > 2 else "No listening TCP ports found."


@windows_server_mcp_tool()
def test_network_latency(targets: str = "1.1.1.1,8.8.8.8,microsoft.com", count: int = 4) -> str:
    """
    Measure ping latency to one or more comma-separated targets.
    """
    results: list[str] = []
    for target in [item.strip() for item in targets.split(",") if item.strip()]:
        try:
            completed = run(
                ["ping", "-n", str(count), target],
                capture_output=True,
                text=True,
                timeout=max(10, count * 4),
            )
            results.append(f"=== {target} ===\n{completed.stdout.strip() or completed.stderr.strip()}")
        except Exception as exc:
            results.append(f"=== {target} ===\nError: {exc}")
    return "\n\n".join(results) if results else "No targets provided."


@windows_server_mcp_tool()
def list_firewall_rules(direction: str = "all", enabled_only: bool = True, max_rules: int = 100) -> str:
    """
    Inspect Windows Defender Firewall rules.
    Args:
        direction: 'Inbound', 'Outbound', or 'all'.
        enabled_only: Return enabled rules only.
        max_rules: Maximum number of rules to return.
    """
    filters = []
    if direction != "all":
        filters.append(f"$_.Direction -eq '{direction}'")
    if enabled_only:
        filters.append("$_.Enabled -eq 'True'")
    where = f"| Where-Object {{ {' -and '.join(filters)} }}" if filters else ""
    script = (
        f"Get-NetFirewallRule {where} | Select-Object -First {max_rules} "
        "DisplayName,Direction,Action,Enabled,Profile | "
        "Format-Table -AutoSize | Out-String -Width 220"
    )
    result = run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], capture_output=True, text=True)
    if result.returncode == TIMEOUT_RETURNCODE:
        return result.stderr.strip()
    if result.returncode != 0:
        return result.stderr.strip() or "Error listing firewall rules."
    return result.stdout.strip() or "No firewall rules found."


@windows_server_mcp_tool()
def get_port_firewall_rules(port: int, protocol: str = "TCP", direction: str = "Inbound") -> str:
    """
    Find firewall rules that reference a local port.
    Args:
        port: Local port to inspect.
        protocol: 'TCP', 'UDP', or 'Any'.
        direction: 'Inbound', 'Outbound', or 'Any'.
    """
    proto_filter = "" if protocol == "Any" else f"-Protocol {protocol}"
    direction_filter = "" if direction == "Any" else f"-Direction {direction}"
    script = f"""
$rules = Get-NetFirewallRule {direction_filter} -ErrorAction SilentlyContinue
$matches = foreach ($rule in $rules) {{
  $ports = $rule | Get-NetFirewallPortFilter -ErrorAction SilentlyContinue
  foreach ($filter in $ports) {{
    $localPorts = @($filter.LocalPort)
    if ($filter.Protocol -eq '{protocol}' -or '{protocol}' -eq 'Any') {{
      if ($localPorts -contains '{port}' -or $localPorts -contains 'Any') {{
        [PSCustomObject]@{{
          DisplayName = $rule.DisplayName
          Enabled = $rule.Enabled
          Direction = $rule.Direction
          Action = $rule.Action
          Profile = $rule.Profile
          Protocol = $filter.Protocol
          LocalPort = $filter.LocalPort
          RemotePort = $filter.RemotePort
        }}
      }}
    }}
  }}
}}
$matches | Format-Table -AutoSize | Out-String -Width 260
"""
    result = run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], capture_output=True, text=True)
    if result.returncode == TIMEOUT_RETURNCODE:
        return result.stderr.strip()
    if result.returncode != 0:
        return result.stderr.strip() or "Error correlating firewall rules."
    return result.stdout.strip() or f"No firewall rules found for {protocol}/{port}."


@windows_server_mcp_tool()
def get_listening_ports_with_firewall() -> str:
    """
    Show listening TCP ports and summarize matching inbound firewall rules for each port.
    """
    listeners: list[tuple[int, str, int | None, str]] = []
    for conn in psutil.net_connections(kind="inet"):
        if conn.status != psutil.CONN_LISTEN or not conn.laddr:
            continue
        listeners.append((conn.laddr.port, conn.laddr.ip, conn.pid, _proc_name(conn.pid)))

    if not listeners:
        return "No listening TCP ports found."

    ports = sorted({port for port, _, _, _ in listeners})
    port_list = ",".join(str(port) for port in ports)
    script = f"""
$targetPorts = @({port_list})
$rules = Get-NetFirewallRule -Direction Inbound -ErrorAction SilentlyContinue
$rows = foreach ($rule in $rules) {{
  $filters = $rule | Get-NetFirewallPortFilter -ErrorAction SilentlyContinue
  foreach ($filter in $filters) {{
    foreach ($port in $targetPorts) {{
      if (($filter.Protocol -eq 'TCP' -or $filter.Protocol -eq 'Any') -and ($filter.LocalPort -contains [string]$port -or $filter.LocalPort -contains 'Any')) {{
        [PSCustomObject]@{{ Port=$port; Rule=$rule.DisplayName; Action=$rule.Action; Enabled=$rule.Enabled; Profile=$rule.Profile }}
      }}
    }}
  }}
}}
$rows | ConvertTo-Json -Depth 4
"""
    result = run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], capture_output=True, text=True)
    if result.returncode == TIMEOUT_RETURNCODE:
        return result.stderr.strip()
    firewall_note = result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else "No firewall correlation data returned."

    lines = [f"{'PORT':<8} {'ADDRESS':<18} {'PID':<8} {'PROCESS':<25}"]
    lines.append("-" * 70)
    for port, address, pid, process_name in listeners:
        lines.append(f"{port:<8} {address:<18} {str(pid or '-'):<8} {process_name[:24]:<25}")
    lines.extend(["", "Matching inbound firewall rules (JSON):", firewall_note])
    return "\n".join(lines)
