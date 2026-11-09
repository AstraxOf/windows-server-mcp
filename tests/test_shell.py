import subprocess
import sys
import time

import pytest

from windows_server_mcp.shell import TIMEOUT_RETURNCODE, run

PY = sys.executable


def test_run_returns_output():
    result = run([PY, "-c", "print('hola')"], timeout=20)
    assert result.returncode == 0
    assert result.stdout.strip() == "hola"


def test_run_times_out_and_kills_hung_process():
    start = time.monotonic()
    result = run([PY, "-c", "import time; time.sleep(60)"], timeout=1)
    assert time.monotonic() - start < 15
    assert result.returncode == TIMEOUT_RETURNCODE
    assert "timed out" in result.stderr.lower()


def test_run_timeout_keeps_partial_stdout():
    code = "import sys,time; print('partial', flush=True); time.sleep(60)"
    result = run([PY, "-c", code], timeout=2)
    assert result.returncode == TIMEOUT_RETURNCODE
    assert "partial" in result.stdout


def test_run_closes_stdin():
    """A child that waits for input must get EOF immediately, not hang."""
    result = run([PY, "-c", "import sys; print(repr(sys.stdin.read()))"], timeout=10)
    assert result.returncode == 0
    assert result.stdout.strip() == "''"


def test_run_check_raises():
    with pytest.raises(subprocess.CalledProcessError):
        run([PY, "-c", "import sys; sys.exit(3)"], check=True, timeout=10)


def test_run_bytes_mode():
    result = run([PY, "-c", "print('x')"], text=False, timeout=10)
    assert isinstance(result.stdout, bytes)
    slow = run([PY, "-c", "import time; time.sleep(60)"], text=False, timeout=1)
    assert slow.returncode == TIMEOUT_RETURNCODE
    assert isinstance(slow.stderr, bytes)


def test_execute_powershell_reports_timeout(monkeypatch):
    from windows_server_mcp.tools import execute_powershell as mod

    def fake_run(args, timeout=None, **kwargs):
        return subprocess.CompletedProcess(args, TIMEOUT_RETURNCODE, "", "Command timed out")

    monkeypatch.setattr(mod, "run", fake_run)
    out = mod.execute_powershell("Start-Sleep 999", timeout_seconds=5)
    assert "Timed out" in out and "5s" in out


def test_execute_powershell_clamps_timeout(monkeypatch):
    from windows_server_mcp.tools import execute_powershell as mod

    seen = {}

    def fake_run(args, timeout=None, **kwargs):
        seen["timeout"] = timeout
        return subprocess.CompletedProcess(args, 0, "ok", "")

    monkeypatch.setattr(mod, "run", fake_run)
    assert mod.execute_powershell("1", timeout_seconds=10**9) == "ok"
    assert seen["timeout"] == mod.MAX_TIMEOUT_SECONDS
    mod.execute_powershell("1", timeout_seconds=-5)
    assert seen["timeout"] == 1


def test_no_tool_uses_raw_subprocess_run():
    """Guard: every tool must go through windows_server_mcp.shell."""
    import pathlib

    tools = pathlib.Path(__file__).parent.parent / "windows_server_mcp" / "tools"
    offenders = [
        p.name
        for p in tools.glob("*.py")
        if "subprocess.run(" in p.read_text(encoding="utf-8")
        or "subprocess.Popen(" in p.read_text(encoding="utf-8")
    ]
    assert offenders == []
