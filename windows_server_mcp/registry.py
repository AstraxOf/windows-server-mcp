import functools
import inspect
import logging
import time

log = logging.getLogger("windows_server_mcp")

registered_tools = []

#: Hard ceiling (seconds) for a single tool call.  Commands have their own,
#: shorter timeouts (see shell.py); this only frees the server when something
#: blocks inside Python itself (a stuck syscall, a hung handle query...).
DEFAULT_TOOL_DEADLINE = 180
LONG_TOOL_DEADLINE = 3700  # update/driver installs


def _deadline_for(name: str, kwargs: dict) -> int:
    if name == "execute_powershell":
        try:
            return min(int(kwargs.get("timeout_seconds", 60)), 3600) + 30
        except (TypeError, ValueError):
            return 90
    if "install" in name:
        return LONG_TOOL_DEADLINE
    return DEFAULT_TOOL_DEADLINE


def _run_in_thread(func):
    """Run a blocking tool in a worker thread with a hard deadline.

    * With ``mcp`` 1.x plain sync tools run on the event loop, so one slow call
      froze the whole server.  A thread keeps the server responsive.
    * If the thread blocks forever (e.g. a stuck syscall), the call is
      abandoned after the deadline and an error is returned, instead of the
      client waiting until its own timeout.
    * Every call is logged (start/finish/abandon) so a hang can be traced to a
      specific tool: a ``start`` line with no ``finished`` line is the culprit.
    """
    if inspect.iscoroutinefunction(func):
        return func

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        import anyio

        name = func.__name__
        deadline = _deadline_for(name, kwargs)
        started = time.monotonic()
        log.info("tool start: %s (deadline %ss)", name, deadline)

        def target():
            try:
                return func(*args, **kwargs)
            finally:
                log.info("tool finished: %s in %.1fs", name, time.monotonic() - started)

        try:
            with anyio.fail_after(deadline):
                return await anyio.to_thread.run_sync(target, abandon_on_cancel=True)
        except TimeoutError:
            log.error("tool ABANDONED: %s still running after %ss", name, deadline)
            return (
                f"Error: tool '{name}' did not finish within {deadline}s and was abandoned. "
                "The server is still responsive; try a narrower request."
            )
        except Exception:
            log.exception("tool failed: %s", name)
            raise

    return wrapper


def windows_server_mcp_tool():
    """
    Decorator to register a function as a Windows MCP tool.
    """
    def decorator(func):
        registered_tools.append(func)
        return func
    return decorator

def register_all_tools(mcp):
    """
    Imports all tool modules and registers them with the server instance
    (``MCPServer`` on mcp 2.x, ``FastMCP`` on mcp 1.x).
    """
    import windows_server_mcp.tools.execute_powershell
    import windows_server_mcp.tools.manage_registry
    import windows_server_mcp.tools.manage_network
    import windows_server_mcp.tools.task_manager
    import windows_server_mcp.tools.software_audit
    import windows_server_mcp.tools.storage_analysis
    import windows_server_mcp.tools.system_info
    import windows_server_mcp.tools.process_management
    import windows_server_mcp.tools.optimization
    import windows_server_mcp.tools.services
    import windows_server_mcp.tools.hardware_drivers
    import windows_server_mcp.tools.media_management
    import windows_server_mcp.tools.advanced_process
    import windows_server_mcp.tools.window_management
    import windows_server_mcp.tools.startup_tasks
    import windows_server_mcp.tools.event_diagnostics
    import windows_server_mcp.tools.network_diagnostics
    import windows_server_mcp.tools.security_updates
    import windows_server_mcp.tools.power_hardware
    import windows_server_mcp.tools.safe_file_operations
    import windows_server_mcp.tools.developer_environment
    import windows_server_mcp.tools.shell_helpers
    import windows_server_mcp.tools.disk_health
    import windows_server_mcp.tools.driver_maintenance
    import windows_server_mcp.tools.software_maintenance
    import windows_server_mcp.tools.peripherals
    import windows_server_mcp.tools.virtualization
    import windows_server_mcp.tools.restore_update_controls
    import windows_server_mcp.tools.text_files

    for func in registered_tools:
        mcp.tool()(_run_in_thread(func))
