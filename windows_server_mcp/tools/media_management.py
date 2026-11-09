import os
import glob
from windows_server_mcp.registry import windows_server_mcp_tool

def _format_size(size_bytes: int) -> str:
    if size_bytes == 0: return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    temp = size_bytes
    idx = 0
    while temp >= 1024 and idx < len(size_name) - 1:
        temp /= 1024
        idx += 1
    return f"{temp:.2f} {size_name[idx]}"

@windows_server_mcp_tool()
def find_media_files(directory_path: str, media_type: str = "all", min_size_mb: float = 10.0) -> str:
    """
    Scan a directory for media files (videos, images, sounds) larger than a specific size.
    
    Args:
        directory_path: Path to scan.
        media_type: 'video', 'image', 'audio', or 'all'.
        min_size_mb: Minimum file size in Megabytes to include in the results.
    """
    if not os.path.exists(directory_path):
        return f"Error: Directory '{directory_path}' does not exist."
        
    extensions = {
        "video": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
        "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
        "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"]
    }
    
    if media_type == "all":
        target_exts = set(ext for exts in extensions.values() for ext in exts)
    elif media_type in extensions:
        target_exts = set(extensions[media_type])
    else:
        return f"Error: Invalid media_type '{media_type}'."
        
    min_size_bytes = min_size_mb * 1024 * 1024
    found_files = []
    
    try:
        for dirpath, _, filenames in os.walk(directory_path):
            for f in filenames:
                ext = os.path.splitext(f)[1].lower()
                if ext in target_exts:
                    fp = os.path.join(dirpath, f)
                    try:
                        if not os.path.islink(fp):
                            size = os.path.getsize(fp)
                            if size >= min_size_bytes:
                                found_files.append({"path": fp, "size": size, "ext": ext})
                    except Exception:
                        pass
    except Exception as e:
        return f"Error during scan: {str(e)}"
        
    found_files.sort(key=lambda x: x["size"], reverse=True)
    
    if not found_files:
        return f"No {media_type} files larger than {min_size_mb} MB found in '{directory_path}'."
        
    lines = [f"{'SIZE':<15} | {'TYPE':<6} | {'FILE PATH'}"]
    lines.append("-" * 90)
    for file in found_files[:100]: # Cap at 100 to avoid massive outputs
        lines.append(f"{_format_size(file['size']):<15} | {file['ext']:<6} | {file['path']}")
        
    return "\n".join(lines)

@windows_server_mcp_tool()
def delete_file(file_path: str) -> str:
    """
    Permanently delete a specific file (e.g. a large media file you want to discard).
    WARNING: This skips the Recycle Bin.
    """
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' does not exist."
    if not os.path.isfile(file_path):
        return f"Error: '{file_path}' is a directory, not a file."
        
    try:
        size = os.path.getsize(file_path)
        os.remove(file_path)
        return f"Successfully deleted '{file_path}' (Freed {_format_size(size)})."
    except PermissionError:
        return f"Error: Permission denied to delete '{file_path}'. File might be in use."
    except Exception as e:
        return f"Error deleting file: {str(e)}"

@windows_server_mcp_tool()
def delete_files_by_extension(directory_path: str, extension: str) -> str:
    """
    Mass-delete all files of a specific extension in a given directory (non-recursive).
    Useful for cleaning up generated files, logs, or specific media.
    
    Args:
        directory_path: The directory to clean.
        extension: The file extension to delete (e.g., '.tmp', '.log', '.mp4').
    """
    if not os.path.exists(directory_path):
        return f"Error: Directory '{directory_path}' does not exist."
    if not extension.startswith('.'):
        extension = '.' + extension
        
    deleted_count = 0
    freed_bytes = 0
    errors = 0
    
    try:
        # Use glob to match files directly in the folder (non-recursive to be safe)
        pattern = os.path.join(directory_path, f"*{extension}")
        files_to_delete = glob.glob(pattern)
        
        for fp in files_to_delete:
            if os.path.isfile(fp):
                try:
                    size = os.path.getsize(fp)
                    os.remove(fp)
                    freed_bytes += size
                    deleted_count += 1
                except Exception:
                    errors += 1
                    
        if deleted_count == 0 and errors == 0:
            return f"No files ending with '{extension}' found in '{directory_path}'."
            
        return f"Deleted {deleted_count} files, freeing {_format_size(freed_bytes)}. (Skipped {errors} files)."
    except Exception as e:
        return f"Error during mass deletion: {str(e)}"
