import datetime
import os
from windows_server_mcp.shell import TIMEOUT_RETURNCODE, run, spawn_detached
import tempfile

from windows_server_mcp.registry import windows_server_mcp_tool


@windows_server_mcp_tool()
def open_path_in_explorer(path: str) -> str:
    """
    Open a folder in Explorer or select a file.
    """
    if not os.path.exists(path):
        return f"Error: Path '{path}' does not exist."

    try:
        if os.path.isfile(path):
            spawn_detached(["explorer", f"/select,{os.path.abspath(path)}"])
        else:
            spawn_detached(["explorer", os.path.abspath(path)])
        return f"Opened '{path}' in Explorer."
    except Exception as exc:
        return f"Error opening Explorer: {exc}"


@windows_server_mcp_tool()
def take_screenshot(output_path: str = "", screen: str = "virtual") -> str:
    """
    Capture a screenshot to a PNG file.
    Args:
        output_path: Optional output PNG path. Defaults to the system temp folder.
        screen: 'primary' or 'virtual' for all monitors.
    """
    if not output_path:
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = os.path.join(tempfile.gettempdir(), f"windows-server-mcp-screenshot-{timestamp}.png")

    escaped_path = output_path.replace("'", "''")
    bounds_expr = (
        "[System.Windows.Forms.SystemInformation]::PrimaryMonitorSize"
        if screen == "primary"
        else "[System.Windows.Forms.SystemInformation]::VirtualScreen"
    )
    script = f"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$bounds = {bounds_expr}
if ('{screen}' -eq 'primary') {{
  $rect = New-Object System.Drawing.Rectangle 0, 0, $bounds.Width, $bounds.Height
}} else {{
  $rect = New-Object System.Drawing.Rectangle $bounds.Left, $bounds.Top, $bounds.Width, $bounds.Height
}}
$bitmap = New-Object System.Drawing.Bitmap $rect.Width, $rect.Height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.CopyFromScreen($rect.Left, $rect.Top, 0, 0, $rect.Size)
$bitmap.Save('{escaped_path}', [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()
"""
    result = run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], capture_output=True, text=True)
    if result.returncode == TIMEOUT_RETURNCODE:
        return result.stderr.strip()
    if result.returncode != 0:
        return result.stderr.strip() or "Error taking screenshot."
    return f"Screenshot saved to '{output_path}'."


@windows_server_mcp_tool()
def get_clipboard_text() -> str:
    """Return current text content from the Windows clipboard."""
    result = run(["powershell", "-NoProfile", "-NonInteractive", "-Command", "Get-Clipboard"], capture_output=True, text=True)
    if result.returncode == TIMEOUT_RETURNCODE:
        return result.stderr.strip()
    if result.returncode != 0:
        return result.stderr.strip() or "Error reading clipboard."
    return result.stdout.rstrip("\n")


@windows_server_mcp_tool()
def set_clipboard_text(text: str) -> str:
    """Set Windows clipboard text."""
    escaped = text.replace("'", "''")
    result = run(
        ["powershell", "-NoProfile", "-Command", f"Set-Clipboard -Value '{escaped}'"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return result.stderr.strip() or "Error setting clipboard."
    return "Clipboard text updated."
