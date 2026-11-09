"""Encoding-safe text file tools.

Windows PowerShell 5.1 writes files as UTF-16 (``>``, ``Out-File``), as the
ANSI code page (``Set-Content``) or as UTF-8 *with BOM* (``-Encoding UTF8``).
Any of those can corrupt source code: Chinese-looking characters, ``Ã©``,
``?`` instead of emojis, or a BOM that makes ``tomllib`` / ``json`` / shebangs
fail.  These tools always read and write UTF-8 **without BOM**, so code and
emojis survive.  Prefer them over ``Set-Content`` / ``>`` for source files.
"""

import codecs
import os

from windows_server_mcp.registry import windows_server_mcp_tool

MAX_READ_CHARS = 200_000

_BOMS = (
    (codecs.BOM_UTF32_LE, "utf-32"),
    (codecs.BOM_UTF32_BE, "utf-32"),
    (codecs.BOM_UTF8, "utf-8-sig"),
    (codecs.BOM_UTF16_LE, "utf-16"),
    (codecs.BOM_UTF16_BE, "utf-16"),
)


def _decode(raw: bytes) -> tuple[str, str]:
    """Decode *raw* and return ``(text, detected_encoding)``."""
    for bom, name in _BOMS:
        if raw.startswith(bom):
            return raw.decode(name), name
    # UTF-16 without BOM (typical of `>` redirection edge cases): many NULs.
    if raw and raw.count(b"\x00") > len(raw) // 4:
        for name in ("utf-16-le", "utf-16-be"):
            try:
                return raw.decode(name), name
            except UnicodeDecodeError:
                continue
    try:
        return raw.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return raw.decode("cp1252", errors="replace"), "cp1252 (legacy ANSI)"


def _repair_mojibake(text: str) -> str:
    """Undo UTF-8 text that was wrongly decoded as cp1252 (e.g. 'Ã©' -> 'é')."""
    try:
        return text.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def _apply_newline(text: str, newline: str) -> str:
    if newline == "keep":
        return text
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.replace("\n", "\r\n") if newline == "crlf" else text


@windows_server_mcp_tool()
def read_text_file(path: str, max_chars: int = MAX_READ_CHARS) -> str:
    """Read a text file safely, auto-detecting UTF-8, UTF-8 with BOM, UTF-16 and legacy ANSI, and return its text. Emojis and accents are preserved. The first line reports the detected encoding. Args: path: file to read (use / in paths). max_chars: maximum characters to return."""
    path = os.path.expanduser(path)
    if not os.path.isfile(path):
        return f"Error: file not found: {path}"
    with open(path, "rb") as handle:
        raw = handle.read()
    text, encoding = _decode(raw)
    note = f"[encoding: {encoding}{' - has BOM, consider normalize_text_file_encoding' if 'sig' in encoding or 'utf-16' in encoding or 'utf-32' in encoding else ''}]"
    if len(text) > max_chars:
        text = text[:max_chars] + f"\n... [truncated, {len(text) - max_chars} more characters]"
    return f"{note}\n{text}"


@windows_server_mcp_tool()
def write_text_file(path: str, content: str, append: bool = False, newline: str = "keep") -> str:
    """Write a text file as UTF-8 WITHOUT BOM, so source code and emojis are never corrupted (unlike Set-Content, Out-File or '>' in Windows PowerShell 5.1). Creates missing folders. Args: path: destination file (use / in paths). content: the full text to write. append: add to the end instead of overwriting. newline: 'keep' (as given), 'lf' or 'crlf'."""
    if newline not in ("keep", "lf", "crlf"):
        return "Error: newline must be 'keep', 'lf' or 'crlf'."
    path = os.path.expanduser(path)
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    data = _apply_newline(content, newline).encode("utf-8")
    with open(path, "ab" if append else "wb") as handle:
        handle.write(data)
    verb = "Appended" if append else "Wrote"
    return f"{verb} {len(data)} bytes (UTF-8, no BOM) to {path}"


@windows_server_mcp_tool()
def normalize_text_file_encoding(path: str, repair_mojibake: bool = False, backup: bool = True) -> str:
    """Convert a damaged or legacy text file to clean UTF-8 without BOM: removes the BOM and converts UTF-16/UTF-32/ANSI text. Set repair_mojibake=true to also fix text like 'Ã©' or 'ðŸš€' that was UTF-8 decoded as ANSI. Writes a .bak copy first when backup is true. Args: path: file to fix (use / in paths). repair_mojibake: try to undo double-encoding. backup: keep a .bak copy."""
    path = os.path.expanduser(path)
    if not os.path.isfile(path):
        return f"Error: file not found: {path}"
    with open(path, "rb") as handle:
        raw = handle.read()
    text, encoding = _decode(raw)
    repaired = False
    if repair_mojibake:
        fixed = _repair_mojibake(text)
        repaired = fixed != text
        text = fixed
    new_raw = text.encode("utf-8")
    if new_raw == raw:
        return f"No changes needed: {path} is already UTF-8 without BOM."
    if backup:
        with open(path + ".bak", "wb") as handle:
            handle.write(raw)
    with open(path, "wb") as handle:
        handle.write(new_raw)
    extra = " Mojibake repaired." if repaired else ""
    return f"Converted {path} from {encoding} to UTF-8 without BOM.{extra}" + (" Backup: .bak" if backup else "")
