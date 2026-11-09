"""Safe subprocess helpers shared by every tool.

Why this module exists
----------------------
The MCP server talks to the client over stdio.  A child process that

* inherits the server's ``stdin`` (the MCP channel) can block waiting for input
  (``pause``, installers, ``Read-Host``...), and
* has no ``timeout`` never returns if PowerShell hangs (``Get-Counter``,
  Windows Update COM calls, a UAC prompt nobody can see...).

When that happens the tool call never completes and the MCP client eventually
gives up with its own timeout.  Every external command should go through
:func:`run` / :func:`run_powershell` so it always has a deadline, never reads
from the MCP channel, never pops a console window and is killed together with
all of its children when the deadline expires.
"""

from __future__ import annotations

import os
import subprocess
import sys
from typing import Any, Sequence

#: Used when a caller does not pass an explicit ``timeout``.
DEFAULT_TIMEOUT = 60

#: Exit code reported when a command was killed because it timed out
#: (same convention as GNU ``timeout``).
TIMEOUT_RETURNCODE = 124

_IS_WINDOWS = sys.platform == "win32"
_CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
_CREATE_NEW_PROCESS_GROUP = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)


#: Prepended to every PowerShell ``-Command`` script.  Windows PowerShell 5.1
#: writes to a pipe using the console's OEM code page (cp437/cp850...), which
#: turns accents and emojis into garbage ("Ã©", "?", Chinese-looking text) once
#: Python decodes it.  Forcing UTF-8 (without BOM) on both sides fixes that.
UTF8_PREAMBLE = (
    "try { [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false) } catch {}; "
    "try { [Console]::InputEncoding = New-Object System.Text.UTF8Encoding($false) } catch {}; "
    "$OutputEncoding = New-Object System.Text.UTF8Encoding($false); "
)


def _is_powershell_command(args: Any) -> bool:
    if isinstance(args, (str, bytes)) or not args:
        return False
    exe = os.path.basename(str(args[0])).lower()
    if exe not in ("powershell", "powershell.exe", "pwsh", "pwsh.exe"):
        return False
    return any(str(a).lower() in ("-command", "-c") for a in args[:-1])


def with_utf8_preamble(args: Sequence[str]) -> list[str]:
    """Return *args* with the UTF-8 preamble added to the PowerShell script."""
    argv = list(args)
    for index, value in enumerate(argv[:-1]):
        if str(value).lower() in ("-command", "-c") and not argv[index + 1].startswith(UTF8_PREAMBLE):
            argv[index + 1] = UTF8_PREAMBLE + argv[index + 1]
            break
    return argv


def powershell_command(script: str, *, non_interactive: bool = True) -> list[str]:
    """Build the argv used to run *script* with Windows PowerShell."""
    argv = ["powershell", "-NoProfile"]
    if non_interactive:
        argv.append("-NonInteractive")
    argv += ["-Command", UTF8_PREAMBLE + script]
    return argv


def kill_process_tree(proc: subprocess.Popen) -> None:
    """Kill *proc* and every process it spawned."""
    try:
        if _IS_WINDOWS:
            subprocess.run(
                ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10,
                creationflags=_CREATE_NO_WINDOW,
            )
        else:  # pragma: no cover - only used when developing on Linux/macOS
            import signal

            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except Exception:
        pass
    try:
        proc.kill()
    except Exception:
        pass


def _timeout_message(args: Any, timeout: float) -> str:
    return (
        f"Command timed out after {timeout:g}s and was terminated. "
        "Try a narrower query, or raise the timeout if the task is expected to be slow."
    )


def run(
    args: Sequence[str] | str,
    *,
    timeout: float | None = DEFAULT_TIMEOUT,
    capture_output: bool = True,
    text: bool = True,
    check: bool = False,
    **kwargs: Any,
) -> subprocess.CompletedProcess:
    """Drop-in replacement for :func:`subprocess.run` that cannot hang.

    Differences from ``subprocess.run``:

    * ``timeout`` defaults to :data:`DEFAULT_TIMEOUT`.  Pass ``None`` only if
      you really want to wait forever.
    * ``stdin`` is always closed (``DEVNULL``) so the child can never read from
      the MCP stdio channel.
    * No console window is created on Windows.
    * On timeout the whole process tree is killed and a ``CompletedProcess``
      with ``returncode == 124`` is *returned* (not raised).  ``stderr``
      contains an explanatory message, so the existing
      ``if result.returncode != 0: return result.stderr`` code paths report the
      timeout to the model instead of blowing up.
    """
    kwargs.pop("stdin", None)
    if _is_powershell_command(args):
        args = with_utf8_preamble(args)
        if text:
            kwargs.setdefault("encoding", "utf-8")
    if capture_output:
        kwargs.setdefault("stdout", subprocess.PIPE)
        kwargs.setdefault("stderr", subprocess.PIPE)
    if text:
        kwargs.setdefault("errors", "replace")
    flags = kwargs.pop("creationflags", 0) | _CREATE_NO_WINDOW
    if not _IS_WINDOWS:  # pragma: no cover
        kwargs.setdefault("start_new_session", True)
        flags = 0
    else:
        flags |= _CREATE_NEW_PROCESS_GROUP

    proc = subprocess.Popen(
        args,
        stdin=subprocess.DEVNULL,
        text=text,
        creationflags=flags,
        **kwargs,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        kill_process_tree(proc)
        try:
            stdout, stderr = proc.communicate(timeout=5)
        except Exception:
            stdout, stderr = ("" if text else b""), ("" if text else b"")
        message = _timeout_message(args, timeout or 0)
        if text:
            stderr = f"{(stderr or '').rstrip()}\n{message}".strip()
        else:
            stderr = (stderr or b"") + b"\n" + message.encode()
        return subprocess.CompletedProcess(args, TIMEOUT_RETURNCODE, stdout, stderr)
    except BaseException:
        kill_process_tree(proc)
        raise

    result = subprocess.CompletedProcess(args, proc.returncode, stdout, stderr)
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, args, output=stdout, stderr=stderr
        )
    return result


def run_powershell(
    script: str,
    *,
    timeout: float | None = DEFAULT_TIMEOUT,
    non_interactive: bool = True,
) -> subprocess.CompletedProcess:
    """Run a PowerShell script with a deadline and a closed stdin."""
    return run(powershell_command(script, non_interactive=non_interactive), timeout=timeout)


def spawn_detached(args: Sequence[str]) -> subprocess.Popen:
    """Start a GUI program (e.g. Explorer) without waiting for it or sharing stdio."""
    return subprocess.Popen(
        args,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=_CREATE_NO_WINDOW if _IS_WINDOWS else 0,
    )
