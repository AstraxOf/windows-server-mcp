import ctypes
import ctypes.wintypes
from typing import Optional

import psutil

from windows_server_mcp.registry import windows_server_mcp_tool


user32 = ctypes.windll.user32
SW_RESTORE = 9
WM_CLOSE = 0x0010


def _visible_windows() -> list[dict[str, int | str]]:
    windows: list[dict[str, int | str]] = []

    def callback(hwnd: int, _lparam: int) -> bool:
        if not user32.IsWindowVisible(hwnd):
            return True

        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return True

        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)

        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

        rect = ctypes.wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))

        try:
            process_name = psutil.Process(pid.value).name()
        except Exception:
            process_name = "Unknown"

        windows.append({
            "handle": hwnd,
            "title": buffer.value,
            "pid": pid.value,
            "process": process_name,
            "bounds": f"{rect.left},{rect.top},{rect.right},{rect.bottom}",
        })
        return True

    enum_proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)(callback)
    user32.EnumWindows(enum_proc, 0)
    return windows


def _find_window(pid: Optional[int], title: str) -> Optional[dict[str, int | str]]:
    title_lower = title.lower()
    for window in _visible_windows():
        pid_matches = pid is not None and int(window["pid"]) == pid
        title_matches = bool(title) and title_lower in str(window["title"]).lower()
        if pid_matches or title_matches:
            return window
    return None


@windows_server_mcp_tool()
def list_open_windows() -> str:
    """Return visible app windows with title, process name, PID, window handle, and bounds."""
    windows = _visible_windows()
    if not windows:
        return "No visible windows found."

    lines = [f"{'HWND':<12} {'PID':<8} {'PROCESS':<25} {'BOUNDS':<25} TITLE"]
    lines.append("-" * 100)
    for window in windows:
        lines.append(
            f"{window['handle']:<12} {window['pid']:<8} "
            f"{str(window['process'])[:24]:<25} {window['bounds']:<25} {window['title']}"
        )
    return "\n".join(lines)


@windows_server_mcp_tool()
def focus_window(pid: int = 0, title: str = "") -> str:
    """
    Bring a visible window forward by PID or title substring.
    Provide either pid or title.
    """
    window = _find_window(pid or None, title)
    if not window:
        return "No matching visible window found."

    hwnd = int(window["handle"])
    user32.ShowWindow(hwnd, SW_RESTORE)
    user32.SetForegroundWindow(hwnd)
    return f"Focused window '{window['title']}' (PID: {window['pid']}, HWND: {hwnd})."


@windows_server_mcp_tool()
def close_window(pid: int = 0, title: str = "") -> str:
    """
    Ask a visible window to close gracefully by PID or title substring.
    This posts WM_CLOSE; it does not force-kill the owning process.
    """
    window = _find_window(pid or None, title)
    if not window:
        return "No matching visible window found."

    hwnd = int(window["handle"])
    user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
    return f"Close requested for '{window['title']}' (PID: {window['pid']}, HWND: {hwnd})."
