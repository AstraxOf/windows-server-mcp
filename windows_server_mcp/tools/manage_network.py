import socket
import psutil
from windows_server_mcp.shell import run
from windows_server_mcp.registry import windows_server_mcp_tool

@windows_server_mcp_tool()
def manage_network(action: str, target: str = "") -> str:
    """
    Manage and inspect network settings.
    
    Args:
        action: 'interfaces', 'connections', 'ping', 'wifi_networks'.
        target: IP or hostname (required for 'ping').
    """
    if action == "interfaces":
        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()
        result = []
        for name, addrs_list in addrs.items():
            result.append(f"Interface: {name}")
            stat = stats.get(name)
            if stat:
                result.append(f"  Status: {'Up' if stat.isup else 'Down'} | Speed: {stat.speed}MB/s")
            for addr in addrs_list:
                family = "IPv4" if addr.family == socket.AF_INET else "IPv6" if addr.family == socket.AF_INET6 else "MAC"
                result.append(f"  {family}: {addr.address}")
        return "\n".join(result)
        
    elif action == "connections":
        conns = psutil.net_connections(kind='inet')
        lines = [f"{'PROTO':<5} {'LADDR':<20} {'RADDR':<20} {'STATUS':<15} {'PID':<8}"]
        lines.append("-" * 70)
        for c in conns[:20]:
            proto = "TCP" if c.type == socket.SOCK_STREAM else "UDP"
            laddr = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else ""
            raddr = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else ""
            status = c.status
            lines.append(f"{proto:<5} {laddr:<20} {raddr:<20} {status:<15} {c.pid or '-':<8}")
        if len(conns) > 20:
            lines.append(f"... and {len(conns) - 20} more connections.")
        return "\n".join(lines)
        
    elif action == "ping":
        if not target:
            return "Error: target is required for ping."
        res = run(["ping", "-n", "4", target], capture_output=True, text=True)
        return res.stdout
        
    elif action == "wifi_networks":
        try:
            res = run(["netsh", "wlan", "show", "networks"], capture_output=True, text=True, check=True)
            return res.stdout
        except Exception as e:
            return f"Error getting Wi-Fi networks: {str(e)}"
            
    return f"Error: Invalid action '{action}'."
