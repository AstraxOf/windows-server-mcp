import os
from windows_server_mcp.shell import run
import winreg
import shutil
from windows_server_mcp.registry import windows_server_mcp_tool

@windows_server_mcp_tool()
def empty_recycle_bin() -> str:
    """Empty the Windows Recycle Bin to free up space."""
    try:
        result = run(
            ["powershell", "-NoProfile", "-Command", "Clear-RecycleBin -Force -ErrorAction Stop"], 
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return "Recycle Bin emptied successfully."
        else:
            return f"Failed to empty Recycle Bin: {result.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

@windows_server_mcp_tool()
def clear_temp_files() -> str:
    """
    Clear standard Windows temporary folders (%TEMP% and C:\\Windows\\Temp).
    Useful for system optimization.
    """
    temp_dirs = [
        os.environ.get("TEMP"),
        os.environ.get("TMP"),
        "C:\\Windows\\Temp"
    ]
    
    freed_bytes = 0
    deleted_files = 0
    errors = 0
    
    for temp_dir in set(filter(None, temp_dirs)):
        if os.path.exists(temp_dir):
            for root, dirs, files in os.walk(temp_dir):
                for name in files:
                    file_path = os.path.join(root, name)
                    try:
                        size = os.path.getsize(file_path)
                        os.remove(file_path)
                        freed_bytes += size
                        deleted_files += 1
                    except Exception:
                        errors += 1
                        
    mb_freed = freed_bytes / (1024 * 1024)
    return f"Optimization Complete: Deleted {deleted_files} temp files, freeing {mb_freed:.2f} MB. (Skipped {errors} files currently in use)."

@windows_server_mcp_tool()
def list_startup_apps() -> str:
    """
    Retrieve a list of programs configured to run at Windows startup from the Registry.
    Use this to identify background apps slowing down boot times.
    """
    startup_apps = []
    
    def read_registry_key(hive, subkey, hive_name):
        try:
            with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ) as key:
                num_values = winreg.QueryInfoKey(key)[1]
                for i in range(num_values):
                    name, value, _ = winreg.EnumValue(key, i)
                    startup_apps.append(f"[{hive_name}] {name}: {value}")
        except FileNotFoundError:
            pass
        except Exception as e:
            startup_apps.append(f"Error reading {hive_name}: {str(e)}")

    read_registry_key(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "HKCU")
    read_registry_key(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", "HKLM")
    
    if not startup_apps:
        return "No startup apps found in standard Run keys."
    return "\n".join(startup_apps)
