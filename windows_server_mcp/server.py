"""Entry point for the Windows Management MCP server.

This module works with both generations of the official MCP Python SDK:

* ``mcp >= 2.0``  -> ``MCPServer`` (``mcp.server.mcpserver``).
  In v2 the old ``FastMCP`` class was renamed to ``MCPServer`` and the
  ``mcp.server.fastmcp`` module was removed without a deprecation shim.
* ``mcp 1.x``     -> ``FastMCP`` (``mcp.server.fastmcp``).

Migration guide:
https://py.sdk.modelcontextprotocol.io/v2/migration/#fastmcp-renamed-to-mcpserver
"""

import logging
import logging.handlers
import os
import sys
import tempfile
from importlib.metadata import PackageNotFoundError, version as _dist_version

from windows_server_mcp.registry import register_all_tools

try:  # mcp 2.x
    from mcp.server.mcpserver import MCPServer as _Server

    _SDK_GENERATION = 2
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server

    _SDK_GENERATION = 1

SERVER_NAME = "Windows Management"


def _package_version() -> str:
    try:
        return _dist_version("windows-server-mcp")
    except PackageNotFoundError:  # running from a source checkout
        return "0.0.0+local"


def create_server():
    """Build the MCP server and register every Windows tool on it."""
    if _SDK_GENERATION == 2:
        # In v2 only `name` is positional-safe: pass everything else by keyword.
        server = _Server(SERVER_NAME, version=_package_version())
    else:
        server = _Server(SERVER_NAME)
    register_all_tools(server)
    return server


mcp = create_server()


def _log_dir() -> str:
    base = os.environ.get("LOCALAPPDATA") or tempfile.gettempdir()
    return os.path.join(base, "windows-server-mcp")


def _harden_stdio() -> None:
    """Make sure logging can never block the server.

    When the server is started with ``pythonw.exe`` by a bridge/launcher,
    ``stderr`` is often a pipe nobody reads.  Once ~64 KB of log lines fill it,
    the next ``write`` blocks forever and every tool call "hangs" until the
    process is killed.  We send our own logs and ``stderr`` to files instead.
    ``stdout`` is left alone: it carries the MCP protocol.
    """
    try:
        directory = _log_dir()
        os.makedirs(directory, exist_ok=True)
        log_file = os.path.join(directory, "server.log")
        err_file = os.path.join(directory, "stderr.log")

        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=1_000_000, backupCount=2, encoding="utf-8"
        )
        handler.setFormatter(logging.Formatter("%(asctime)s %(threadName)s %(levelname)s %(message)s"))
        package_logger = logging.getLogger("windows_server_mcp")
        package_logger.setLevel(logging.INFO)
        package_logger.addHandler(handler)
        package_logger.propagate = False

        if os.path.exists(err_file) and os.path.getsize(err_file) > 5_000_000:
            os.remove(err_file)
        err_stream = open(err_file, "a", buffering=1, encoding="utf-8", errors="replace")
        previous_stderr = sys.stderr
        sys.stderr = err_stream
        loggers = [logging.getLogger()] + [
            lg for lg in logging.root.manager.loggerDict.values() if isinstance(lg, logging.Logger)
        ]
        for lg in loggers:
            for existing in lg.handlers:
                # Only re-point handlers that write to the old stderr; leave
                # foreign handlers (e.g. pytest's capture handlers) untouched.
                if (
                    isinstance(existing, logging.StreamHandler)
                    and not isinstance(existing, logging.FileHandler)
                    and getattr(existing, "stream", None) in (previous_stderr, sys.__stderr__)
                ):
                    existing.setStream(err_stream)
        package_logger.info("server starting (python %s, sdk generation %s)", sys.executable, _SDK_GENERATION)
    except Exception:
        # Never let logging setup prevent the server from starting.
        pass


def main():
    """Run the server over stdio (the default transport)."""
    _harden_stdio()
    mcp.run()


if __name__ == "__main__":
    main()
