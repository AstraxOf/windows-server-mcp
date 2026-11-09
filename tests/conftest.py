"""Let the test-suite import the package on non-Windows machines.

The tool modules import ``winreg`` and use ``ctypes.windll`` at import time.
On Windows (the real target, and what CI uses) nothing is stubbed. On
Linux/macOS we inject harmless stand-ins so contributors can still run the
registration tests locally. No tool is ever *executed* by these tests.
"""
import ctypes
import sys
from unittest import mock

if sys.platform != "win32":
    sys.modules.setdefault("winreg", mock.MagicMock(name="winreg"))
    if not hasattr(ctypes, "windll"):
        ctypes.windll = mock.MagicMock(name="windll")  # type: ignore[attr-defined]
