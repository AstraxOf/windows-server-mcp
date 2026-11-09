import asyncio

import pytest

EXPECTED_TOOL_COUNT = 100


def test_registry_counts_tools():
    from windows_server_mcp.registry import register_all_tools, registered_tools

    class Dummy:
        def tool(self):
            return lambda f: f

    register_all_tools(Dummy())
    assert len(registered_tools) == EXPECTED_TOOL_COUNT


def test_server_imports_with_installed_sdk():
    """Fails loudly if the installed `mcp` SDK moves the server class again."""
    from windows_server_mcp import server

    assert server.mcp is not None
    assert server._SDK_GENERATION in (1, 2)


def test_server_exposes_all_tools():
    from windows_server_mcp.server import mcp

    tools = asyncio.run(mcp.list_tools())
    names = {t.name for t in tools}
    assert len(names) == EXPECTED_TOOL_COUNT
    assert "execute_powershell" in names
    assert "get_cpu_usage" in names
