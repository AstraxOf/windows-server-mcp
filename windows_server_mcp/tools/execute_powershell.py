import os
import shutil
import sys
import tempfile

from windows_server_mcp.registry import windows_server_mcp_tool
from windows_server_mcp.shell import TIMEOUT_RETURNCODE, run

DEFAULT_TIMEOUT_SECONDS = 60
MAX_TIMEOUT_SECONDS = 3600
MAX_OUTPUT_CHARS = 200_000


def _is_admin() -> bool:
    if sys.platform != "win32":
        return False
    try:
        import ctypes

        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def _clip(text: str) -> str:
    if len(text) <= MAX_OUTPUT_CHARS:
        return text
    return text[:MAX_OUTPUT_CHARS] + f"\n... [output truncated, {len(text) - MAX_OUTPUT_CHARS} more characters]"


def _format(result, timeout: int) -> str:
    out = (result.stdout or "").strip()
    err = (result.stderr or "").strip()
    if result.returncode == TIMEOUT_RETURNCODE:
        partial = f"\nPartial output:\n{_clip(out)}" if out else ""
        return (
            f"Timed out: the PowerShell script did not finish within {timeout}s and was terminated.{partial}\n"
            "Hint: run long tasks in smaller steps, or call again with a larger timeout_seconds."
        )
    if result.returncode == 0:
        return _clip(out) if out else "Command completed successfully with no output."
    return f"Error executing PowerShell (Exit {result.returncode}):\n{_clip(err or out)}"


def _run_elevated(script: str, timeout: int) -> str:
    """Run *script* elevated and return its output.

    The script is written to a temp file (no fragile quoting), its output is
    redirected to a second temp file, and the whole thing is bounded by
    *timeout* so an unseen/ignored UAC prompt can never hang the server.
    """
    workdir = tempfile.mkdtemp(prefix="windows-server-mcp-")
    script_path = os.path.join(workdir, "task.ps1")
    out_path = os.path.join(workdir, "out.txt")
    try:
        wrapper = (
            "$ErrorActionPreference = 'Continue'\n"
            "try {\n"
            f"  & {{\n{script}\n  }} *>&1 | Out-File -FilePath '{out_path}' -Encoding utf8\n"
            "  if ($LASTEXITCODE) { exit $LASTEXITCODE }\n"
            "} catch {\n"
            f"  $_ | Out-String | Out-File -FilePath '{out_path}' -Append -Encoding utf8\n"
            "  exit 1\n"
            "}\n"
        )
        # UTF-8 with BOM so Windows PowerShell 5.1 reads non-ASCII correctly.
        with open(script_path, "w", encoding="utf-8-sig") as handle:
            handle.write(wrapper)

        if _is_admin():
            result = run(
                ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", script_path],
                timeout=timeout,
            )
        else:
            launcher = (
                "try { "
                "$p = Start-Process powershell -Verb RunAs -Wait -PassThru -WindowStyle Hidden "
                f"-ArgumentList '-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File','{script_path}'; "
                "exit $p.ExitCode "
                "} catch { Write-Error $_.Exception.Message; exit 1 }"
            )
            result = run(["powershell", "-NoProfile", "-NonInteractive", "-Command", launcher], timeout=timeout)

        if result.returncode == TIMEOUT_RETURNCODE:
            return (
                f"Timed out after {timeout}s waiting for the elevated command. "
                "The UAC prompt was probably not accepted (it may be hidden behind other windows) "
                "or the script is still running in the elevated process."
            )
        captured = ""
        if os.path.exists(out_path):
            with open(out_path, "r", encoding="utf-8-sig", errors="replace") as handle:
                captured = handle.read().strip()
        if result.returncode != 0 and not captured:
            return f"Elevated command failed (Exit {result.returncode}): {(result.stderr or '').strip() or 'UAC was probably declined.'}"
        if result.returncode != 0:
            return f"Elevated command failed (Exit {result.returncode}):\n{_clip(captured)}"
        return _clip(captured) if captured else "Elevated command completed successfully with no output."
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


@windows_server_mcp_tool()
def execute_powershell(script: str, require_admin: bool = False, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> str:
    """
    Execute a PowerShell script or command and return its output.
    Use this for advanced system management tasks not covered by other tools.

    The command always has a deadline: if it does not finish within
    timeout_seconds it is terminated (with its child processes) and a timeout
    message is returned instead of hanging the server. The script cannot read
    from stdin, so avoid Read-Host, pause or interactive installers.

    Output is always decoded as UTF-8 (accents and emojis are preserved). To
    create or edit source code files do NOT use Set-Content, Out-File or '>'
    (Windows PowerShell 5.1 saves them as UTF-16, ANSI or UTF-8 with BOM and can
    corrupt the code); use the write_text_file tool, which writes UTF-8 without BOM.

    Args:
        script: The PowerShell script to execute.
        require_admin: If true, runs elevated (shows a UAC prompt unless the server is already elevated). Output is captured.
        timeout_seconds: Maximum run time in seconds (default 60, max 3600). Raise it for slow tasks such as installs or updates.
    """
    try:
        timeout = max(1, min(int(timeout_seconds), MAX_TIMEOUT_SECONDS))
    except (TypeError, ValueError):
        timeout = DEFAULT_TIMEOUT_SECONDS
    try:
        if require_admin:
            return _run_elevated(script, timeout)
        result = run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], timeout=timeout)
        return _format(result, timeout)
    except Exception as e:
        return f"Exception executing PowerShell: {str(e)}"
