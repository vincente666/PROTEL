"""PROTEL file extension conventions (Emacs mode + compiler driver)."""

import re
import subprocess
from pathlib import Path

import pytest

from src.cpp_transpiler import transpile_to_cpp
from src.extensions import format_suffix_list, is_pls_suffix, is_protel_source, is_protel_suffix
from src.parser import parse_protel

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"
MODE_EL = ROOT / "emacs" / "protel-mode.el"
PROTEL = ROOT / "Pc"


@pytest.mark.parametrize(
    "name,expected",
    [
        ("Hello.P", True),
        ("Hello.protel", True),
        ("Hello.p", True),
        ("Hello.pt", True),
        ("Hello.ptl", True),
        ("vdi.aa01", True),
        ("module.AB18", True),
        ("module.ZZ99", True),
        ("module.aa00", True),
        ("readme.txt", False),
        ("bad.A1", False),
        ("bad.ABC1", False),
        ("bad.1A01", False),
        ("bad.AA1", False),
    ],
)
def test_is_protel_source_recognizes_fixed_and_pls_suffixes(name, expected):
    assert is_protel_source(name) is expected


def test_is_pls_suffix_matches_letter_digit_pattern():
    assert is_pls_suffix(".aa01")
    assert is_pls_suffix(".AB99")
    assert not is_pls_suffix(".P")
    assert not is_pls_suffix(".protel")


def test_format_suffix_list_mentions_pls_range():
    text = format_suffix_list()
    assert ".P" in text
    assert "default" in text
    assert ".AA01" in text
    assert ".ZZ99" in text


def test_protel_mode_registers_legacy_p_extension():
    source = MODE_EL.read_text(encoding="utf-8")
    assert re.search(r'auto-mode-alist.*\\\.P\\', source)


def test_protel_mode_font_locks_shebang_as_comment():
    source = MODE_EL.read_text(encoding="utf-8")
    assert '(list "^#![^\\n]*" 0 \'font-lock-comment-face)' in source


def test_protel_mode_registers_pls_edition_suffixes():
    source = MODE_EL.read_text(encoding="utf-8")
    assert "PLS edition suffixes" in source
    assert "[A-Za-z][A-Za-z][0-9][0-9]" in source


def test_hello_p_transpiles():
    legacy = (EXAMPLES / "Hello.P").read_text(encoding="utf-8")
    cpp = transpile_to_cpp(parse_protel(legacy), source_name="Hello.P")
    assert "protel_generated::Hello::Start()" in cpp
    assert "writeln(" in cpp


def test_hello_pls_transpiles():
    pls = (EXAMPLES / "Hello.aa01").read_text(encoding="utf-8")
    cpp = transpile_to_cpp(parse_protel(pls), source_name="Hello.aa01")
    assert "protel_generated::Hello::Start()" in cpp
    assert "writeln(" in cpp


def test_protel_driver_accepts_pls_suffix_without_warning():
    result = subprocess.run(
        [str(ROOT / ".venv/bin/python"), str(PROTEL), str(EXAMPLES / "Hello.aa01"), "--emit-c"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "does not use a PROTEL extension" not in result.stderr