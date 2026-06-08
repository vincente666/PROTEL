"""ENTRY procedure tests (Introductory Manual 5.5.2)."""

import pytest

from src.cpp_transpiler import transpile_to_cpp
from src.parser import parse_protel
from src.transpiler import TranspileError


def test_parse_entry_declaration():
    tree = parse_protel("SECTION demo;\nDCL Start PROC() IS ENTRY;\n")
    decl = tree[0].declarations[0]
    assert decl.entry
    assert decl.name == "Start"
    assert decl.body is None


def test_entry_emits_c_main_wrapper():
    source = """
SECTION Hello;
DCL Start PROC() IS ENTRY;
DCL Start PROC() IS BLOCK ENDBLOCK;
"""
    cpp = transpile_to_cpp(parse_protel(source), source_name="Hello.protel")
    assert "/* ENTRY Start */" in cpp
    assert "void Start()" in cpp
    assert "int main()" in cpp
    assert "protel_generated::Hello::Start();" in cpp
    assert "return 0;" in cpp


def test_procedure_named_main_without_entry_has_no_c_main():
    source = """
SECTION demo;
DCL main PROC() IS BLOCK ENDBLOCK;
"""
    cpp = transpile_to_cpp(parse_protel(source), source_name="demo.protel")
    assert "void main()" in cpp
    assert "int main()" not in cpp


def test_missing_entry_body_raises():
    with pytest.raises(TranspileError, match="has no procedure body"):
        transpile_to_cpp(parse_protel("SECTION s;\nDCL Start PROC() IS ENTRY;\n"))


def test_multiple_entry_raises():
    with pytest.raises(TranspileError, match="multiple ENTRY"):
        transpile_to_cpp(
            parse_protel(
                "SECTION s;\n"
                "DCL Start PROC() IS ENTRY;\n"
                "DCL Other PROC() IS ENTRY;\n"
            )
        )