import asyncio
import logging
import sys
import threading
import time


def test_slow_tool_is_abandoned_and_server_stays_responsive(monkeypatch):
    from windows_server_mcp import registry

    monkeypatch.setattr(registry, "DEFAULT_TOOL_DEADLINE", 1)
    release = threading.Event()

    def stuck_tool() -> str:
        """Pretend to block in a syscall."""
        release.wait(30)
        return "late"

    wrapped = registry._run_in_thread(stuck_tool)

    async def scenario():
        started = time.monotonic()
        result = await wrapped()
        elapsed = time.monotonic() - started
        # the event loop must still be alive while the thread is stuck
        await asyncio.sleep(0.01)
        return result, elapsed

    try:
        result, elapsed = asyncio.run(scenario())
    finally:
        release.set()
    assert "abandoned" in result
    assert elapsed < 10


def test_wrapper_preserves_signature_and_doc():
    import inspect

    from windows_server_mcp import registry

    def sample(a: int, b: str = "x") -> str:
        """Doc."""
        return b * a

    wrapped = registry._run_in_thread(sample)
    assert inspect.signature(wrapped) == inspect.signature(sample)
    assert wrapped.__doc__ == "Doc."
    assert asyncio.run(wrapped(2, b="y")) == "yy"


def test_harden_stdio_redirects_stderr_to_file(monkeypatch, tmp_path):
    from windows_server_mcp import server

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    original = sys.stderr
    try:
        server._harden_stdio()
        print("boom", file=sys.stderr)
        logging.getLogger("windows_server_mcp").info("hello")
        assert sys.stderr is not original
    finally:
        sys.stderr = original
    base = tmp_path / "windows-server-mcp"
    assert "boom" in (base / "stderr.log").read_text(encoding="utf-8")
    assert "hello" in (base / "server.log").read_text(encoding="utf-8")
