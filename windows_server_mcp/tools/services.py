import psutil
import subprocess
from windows_server_mcp.shell import run
from windows_server_mcp.registry import windows_server_mcp_tool

@windows_server_mcp_tool()
def list_services(status: str = "running") -> str:
    """
    List Windows services.
    Args:
        status: 'running', 'stopped', or 'all'
    """
    services = []
    try:
        for svc in psutil.win_service_iter():
            try:
                info = svc.as_dict()
                if status == "all" or info['status'] == status:
                    services.append(f"Name: {info['name']:<20} | Display: {str(info['display_name'])[:30]:<30} | Status: {info['status']}")
            except psutil.NoSuchProcess:
                pass
    except AttributeError:
        return "Error: psutil.win_service_iter is only available on Windows."
    
    if not services:
        return f"No services found with status '{status}'"
    return "\n".join(services)

@windows_server_mcp_tool()
def manage_service(service_name: str, action: str) -> str:
    """
    Manage a Windows service.
    Args:
        service_name: The internal name of the service (e.g. 'Spooler').
        action: 'start', 'stop', 'pause', or 'continue'.
    Note: Requires Administrator privileges for most services.
    """
    if action not in ['start', 'stop', 'pause', 'continue']:
        return "Error: action must be 'start', 'stop', 'pause', or 'continue'."
    
    try:
        result = run(["sc", action, service_name], capture_output=True, text=True, check=True)
        return f"Successfully executed '{action}' on service '{service_name}'.\nOutput: {result.stdout.strip()}"
    except subprocess.CalledProcessError as e:
        return f"Error managing service: {e.stderr or e.stdout}"
    except Exception as e:
        return f"Error: {str(e)}"
