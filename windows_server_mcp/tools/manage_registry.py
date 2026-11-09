import winreg
from windows_server_mcp.registry import windows_server_mcp_tool

@windows_server_mcp_tool()
def manage_registry(action: str, hive: str, key_path: str, value_name: str = "", value_data: str = "", value_type: str = "REG_SZ") -> str:
    """
    Manage Windows Registry keys and values.
    
    Args:
        action: 'read', 'write', or 'delete'.
        hive: 'HKCU', 'HKLM', 'HKCR', 'HKU', or 'HKCC'.
        key_path: Path to the registry key (e.g., 'Software\\MyApp').
        value_name: Name of the value to read/write/delete (leave empty for Default value).
        value_data: Data to write (ignored for read/delete).
        value_type: Type of data for write ('REG_SZ', 'REG_DWORD', 'REG_BINARY', 'REG_EXPAND_SZ').
    """
    hives = {
        'HKCU': winreg.HKEY_CURRENT_USER,
        'HKLM': winreg.HKEY_LOCAL_MACHINE,
        'HKCR': winreg.HKEY_CLASSES_ROOT,
        'HKU': winreg.HKEY_USERS,
        'HKCC': winreg.HKEY_CURRENT_CONFIG
    }
    
    if hive not in hives:
        return f"Error: Invalid hive '{hive}'."
        
    hkey = hives[hive]
    
    try:
        if action == "read":
            with winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ) as key:
                val, regtype = winreg.QueryValueEx(key, value_name)
                type_name = [k for k, v in vars(winreg).items() if k.startswith('REG_') and v == regtype]
                type_str = type_name[0] if type_name else str(regtype)
                return f"Value: {val}\nType: {type_str}"
                
        elif action == "write":
            type_map = {
                'REG_SZ': winreg.REG_SZ,
                'REG_DWORD': winreg.REG_DWORD,
                'REG_BINARY': winreg.REG_BINARY,
                'REG_EXPAND_SZ': winreg.REG_EXPAND_SZ
            }
            if value_type not in type_map:
                return f"Error: Unsupported value_type '{value_type}'."
                
            reg_type = type_map[value_type]
            
            if value_type == 'REG_DWORD':
                data = int(value_data)
            elif value_type == 'REG_BINARY':
                data = value_data.encode('utf-8')
            else:
                data = value_data
                
            with winreg.CreateKey(hkey, key_path) as key:
                winreg.SetValueEx(key, value_name, 0, reg_type, data)
            return f"Successfully wrote to {hive}\\{key_path}\\{value_name}"
            
        elif action == "delete":
            with winreg.OpenKey(hkey, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, value_name)
            return f"Successfully deleted {hive}\\{key_path}\\{value_name}"
            
        else:
            return f"Error: Invalid action '{action}'."
            
    except FileNotFoundError:
        return f"Error: Path or value not found '{hive}\\{key_path}\\{value_name}'."
    except PermissionError:
        return "Error: Access denied. You may need Administrator privileges."
    except Exception as e:
        return f"Error managing registry: {str(e)}"
