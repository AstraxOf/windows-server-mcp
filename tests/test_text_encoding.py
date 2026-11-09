import codecs

from windows_server_mcp import shell
from windows_server_mcp.tools import text_files

EMOJI = "Hola ñandú 🚀 日本語 ✅\nsegunda línea\n"


def test_write_is_utf8_without_bom(tmp_path):
    target = tmp_path / "sub" / "a.toml"
    text_files.write_text_file(str(target), EMOJI)
    raw = target.read_bytes()
    assert not raw.startswith(codecs.BOM_UTF8)
    assert raw.decode("utf-8") == EMOJI


def test_write_newline_and_append(tmp_path):
    target = tmp_path / "b.txt"
    text_files.write_text_file(str(target), "a\nb\n", newline="crlf")
    text_files.write_text_file(str(target), "c\n", append=True, newline="crlf")
    assert target.read_bytes() == b"a\r\nb\r\nc\r\n"


def test_read_detects_bom_and_utf16(tmp_path):
    bom = tmp_path / "bom.txt"
    bom.write_bytes(codecs.BOM_UTF8 + EMOJI.encode("utf-8"))
    assert EMOJI in text_files.read_text_file(str(bom))
    u16 = tmp_path / "u16.txt"
    u16.write_bytes(codecs.BOM_UTF16_LE + EMOJI.encode("utf-16-le"))
    out = text_files.read_text_file(str(u16))
    assert EMOJI in out and "utf-16" in out


def test_normalize_removes_bom_and_converts_utf16(tmp_path):
    bom = tmp_path / "pyproject.toml"
    bom.write_bytes(codecs.BOM_UTF8 + b'[project]\nname = "x"\n')
    text_files.normalize_text_file_encoding(str(bom))
    assert bom.read_bytes() == b'[project]\nname = "x"\n'
    assert (tmp_path / "pyproject.toml.bak").exists()
    u16 = tmp_path / "u16.txt"
    u16.write_bytes(codecs.BOM_UTF16_LE + EMOJI.encode("utf-16-le"))
    text_files.normalize_text_file_encoding(str(u16), backup=False)
    assert u16.read_bytes() == EMOJI.encode("utf-8")


def test_normalize_repairs_mojibake(tmp_path):
    bad = tmp_path / "bad.txt"
    bad.write_bytes("canciÃ³n".encode("utf-8"))  # UTF-8 text that was decoded as cp1252
    text_files.normalize_text_file_encoding(str(bad), repair_mojibake=True, backup=False)
    assert bad.read_text(encoding="utf-8") == "canción"


def test_powershell_commands_force_utf8():
    argv = shell.powershell_command("Get-Date")
    assert argv[-1].startswith(shell.UTF8_PREAMBLE) and argv[-1].endswith("Get-Date")
    wrapped = shell.with_utf8_preamble(["powershell", "-NoProfile", "-Command", "Get-Date"])
    assert wrapped[-1] == shell.UTF8_PREAMBLE + "Get-Date"
    # idempotent
    assert shell.with_utf8_preamble(wrapped) == wrapped
    assert shell._is_powershell_command(["powershell", "-NoProfile", "-Command", "x"])
    assert not shell._is_powershell_command(["nvidia-smi", "-q"])
