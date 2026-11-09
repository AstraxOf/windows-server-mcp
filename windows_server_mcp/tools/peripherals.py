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
def list_printers() -> str:
    """List installed printers and their status."""
    script = (
        "Get-Printer -ErrorAction SilentlyContinue | "
        "Select-Object Name,DriverName,PortName,PrinterStatus,Default,Shared,Published | "
        "Format-Table -AutoSize | Out-String -Width 220"
    )
    return _run_powershell(script) or "No printers found."


@windows_server_mcp_tool()
def set_default_printer(printer_name: str) -> str:
    """Set the default Windows printer."""
    escaped_name = printer_name.replace("'", "''")
    output = _run_powershell(f"Set-Printer -Name '{escaped_name}' -IsDefault $true")
    return output or f"Default printer set to '{printer_name}'."


@windows_server_mcp_tool()
def list_print_jobs(printer_name: str = "") -> str:
    """List print jobs, optionally for one printer."""
    escaped_printer_name = printer_name.replace("'", "''")
    filter_part = f"-PrinterName '{escaped_printer_name}'" if printer_name else ""
    script = (
        f"Get-PrintJob {filter_part} -ErrorAction SilentlyContinue | "
        "Select-Object PrinterName,ID,DocumentName,JobStatus,SubmittedTime,Size | "
        "Format-Table -AutoSize | Out-String -Width 220"
    )
    return _run_powershell(script) or "No print jobs found."


@windows_server_mcp_tool()
def clear_print_queue(printer_name: str, dry_run: bool = True) -> str:
    """
    Preview or remove all print jobs for a printer.
    """
    escaped_name = printer_name.replace("'", "''")
    preview = list_print_jobs(printer_name)
    if dry_run:
        return f"Dry run. Would clear print queue for '{printer_name}'.\n\n{preview}"

    script = f"Get-PrintJob -PrinterName '{escaped_name}' -ErrorAction SilentlyContinue | Remove-PrintJob"
    output = _run_powershell(script)
    return output or f"Print queue cleared for '{printer_name}'."


@windows_server_mcp_tool()
def list_audio_devices() -> str:
    """List audio endpoint devices and status."""
    script = (
        "Get-PnpDevice -Class AudioEndpoint -ErrorAction SilentlyContinue | "
        "Select-Object Status,FriendlyName,InstanceId | "
        "Format-Table -AutoSize | Out-String -Width 240"
    )
    return _run_powershell(script) or "No audio endpoint devices found."


@windows_server_mcp_tool()
def list_bluetooth_devices() -> str:
    """List Bluetooth devices and status."""
    script = (
        "Get-PnpDevice -Class Bluetooth -ErrorAction SilentlyContinue | "
        "Select-Object Status,FriendlyName,InstanceId | "
        "Format-Table -AutoSize | Out-String -Width 240"
    )
    return _run_powershell(script) or "No Bluetooth devices found."
