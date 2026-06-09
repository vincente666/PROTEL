"""Python interop example tests (transpile + optional link)."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from src.cpp_transpiler import transpile_to_cpp
from src.parser import parse_protel

ROOT = Path(__file__).resolve().parent.parent
INTEROP = ROOT / "examples" / "interop"


def test_protel_calls_python_emits_external_python_greet():
    source = (INTEROP / "protel_calls_python.P").read_text(encoding="utf-8")
    cpp = transpile_to_cpp(parse_protel(source), source_name="protel_calls_python.P")
    assert 'extern "C"' in cpp
    assert "void python_greet(const char* name, int16_t value)" in cpp
    assert "python_greet(" in cpp
    assert "protel_generated::protel_calls_python::Start()" in cpp


def test_protel_for_python_exports_c_linkage():
    source = (INTEROP / "protel_for_python.P").read_text(encoding="utf-8")
    cpp = transpile_to_cpp(parse_protel(source), source_name="protel_for_python.P")
    assert "/* EXPORT protel_add" in cpp
    assert "int16_t protel_add(int16_t a, int16_t b)" in cpp
    assert "return (a + b)" in cpp
    assert "int main()" not in cpp


def test_python_calls_protel_script_mentions_ctypes():
    script = (INTEROP / "python_calls_protel.py").read_text(encoding="utf-8")
    assert "ctypes.CDLL" in script
    assert "protel_add" in script


@pytest.mark.skipif(shutil.which("python3") is None, reason="python3 not installed")
def test_python_interop_examples_build_and_run():
    script = INTEROP / "build_interop_python.sh"
    subprocess.run(["bash", str(script)], cwd=ROOT, check=True, text=True)