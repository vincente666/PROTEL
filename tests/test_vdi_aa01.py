"""Legacy PLS module vdi.aa01 parse and compile tests."""

import subprocess
from pathlib import Path

from src.cpp_transpiler import transpile_to_cpp
from src.parser import parse_protel
from src.preprocess import normalize_keywords

ROOT = Path(__file__).resolve().parent.parent
VDI = ROOT / "vdi.aa01"
PROTEL = ROOT / "Pc"


def test_preprocess_strips_dollar_li_directive():
    norm = normalize_keywords(VDI.read_text(encoding="utf-8"), classical=True)
    assert "$LI" not in norm
    assert "modentry" not in norm
    assert "DCL" in norm
    assert "vdi_debugging_flag" in norm
    assert "BOOL IS TRUE" in norm


def test_vdi_aa01_parses():
    tree = parse_protel(VDI.read_text(encoding="utf-8"), classical=True)
    assert len(tree) == 1
    section = tree[0]
    assert section.name == "VDI"
    assert len(section.declarations) == 1
    assert section.declarations[0].names == ["vdi_debugging_flag"]


def test_vdi_aa01_transpiles_debug_flag():
    tree = parse_protel(VDI.read_text(encoding="utf-8"), classical=True)
    cpp = transpile_to_cpp(tree, source_name="vdi.aa01", classical=True)
    assert "bool vdi_debugging_flag = true;" in cpp
    assert "namespace VDI" in cpp


def test_vdi_aa01_compiles_to_object():
    out = ROOT / "build" / "test_vdi.aa01.o"
    if out.exists():
        out.unlink()
    subprocess.run(
        [str(ROOT / ".venv/bin/python"), str(PROTEL), str(VDI), "-c", "-o", str(out)],
        cwd=ROOT,
        check=True,
        text=True,
    )
    assert out.is_file()
    assert out.stat().st_size > 0