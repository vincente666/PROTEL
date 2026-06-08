"""PROTEL string tuple codegen (no implicit NUL termination)."""

from pathlib import Path

from src.cpp_transpiler import transpile_to_cpp
from src.parser import parse_protel

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_string_literal_emits_char_tuple_not_c_string():
    tree = parse_protel(
        "SECTION s;\n"
        "DCL writeln PROC(m PTR TO char) EXTERNAL;\n"
        "DCL Start PROC() IS ENTRY;\n"
        "DCL Start PROC() IS BLOCK writeln({'Hi', 0}); ENDBLOCK;\n"
    )
    cpp = transpile_to_cpp(tree)
    assert '"Hi"' not in cpp
    assert "(const char[]){ 'H', 'i', 0 }" in cpp


def test_string_without_nul_emits_no_trailing_zero():
    tree = parse_protel(
        "SECTION s;\n"
        "DCL writeln PROC(m PTR TO char) EXTERNAL;\n"
        "DCL Start PROC() IS ENTRY;\n"
        "DCL Start PROC() IS BLOCK writeln({'Hi'}); ENDBLOCK;\n"
    )
    cpp = transpile_to_cpp(tree)
    assert "(const char[]){ 'H', 'i' }" in cpp
    assert ", 0 }" not in cpp


def test_hello_uses_explicit_nul_suffix():
    source = (EXAMPLES / "Hello.protel").read_text(encoding="utf-8")
    assert "{'Hello, World!', 0}" in source
    cpp = transpile_to_cpp(parse_protel(source), source_name="Hello.protel")
    assert "(const char[]){" in cpp
    assert "'!'" in cpp
    assert ", 0 }" in cpp
    assert '"Hello, World!"' not in cpp