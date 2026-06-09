"""Preprocessor shebang stripping (Introductory Manual §7.0.5)."""

from pathlib import Path

from src.parser import parse_protel
from src.preprocess import normalize_keywords, strip_shebang

ROOT = Path(__file__).resolve().parent.parent
HELLO = ROOT / "examples" / "Hello.P"


def test_strip_shebang_removes_first_line():
    source = "#!/usr/bin/env -S Pc --run --\nSECTION s;\n"
    assert strip_shebang(source) == "SECTION s;\n"


def test_strip_shebang_passthrough_without_hash_bang():
    source = "% comment\nSECTION s;\n"
    assert strip_shebang(source) == source


def test_normalize_keywords_strips_shebang_before_parse():
    source = "#!/usr/bin/env Pc --run\n% hi\nSECTION s;\n"
    norm = normalize_keywords(source)
    assert "#!" not in norm
    assert "SECTION" in norm


def test_hello_protel_parses_with_shebang():
    tree = parse_protel(HELLO.read_text(encoding="utf-8"))
    assert tree[0].name == "Hello"
    entries = [
        decl
        for decl in tree[0].declarations
        if hasattr(decl, "entry") and decl.entry
    ]
    assert entries and entries[0].name == "Start"