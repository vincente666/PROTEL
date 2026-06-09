"""Rust interop example tests (transpile + optional link)."""

import shutil
import subprocess
from pathlib import Path

import pytest

from src.cpp_transpiler import transpile_to_cpp
from src.parser import parse_protel

ROOT = Path(__file__).resolve().parent.parent
INTEROP = ROOT / "examples" / "interop"


def test_protel_calls_rust_emits_external_rust_greet():
    source = (INTEROP / "protel_calls_rust.P").read_text(encoding="utf-8")
    cpp = transpile_to_cpp(parse_protel(source), source_name="protel_calls_rust.P")
    assert 'extern "C"' in cpp
    assert "void rust_greet(const char* name, int16_t value)" in cpp
    assert "rust_greet(" in cpp
    assert "protel_generated::protel_calls_rust::Start()" in cpp


def test_protel_for_rust_exports_c_linkage():
    source = (INTEROP / "protel_for_rust.P").read_text(encoding="utf-8")
    cpp = transpile_to_cpp(parse_protel(source), source_name="protel_for_rust.P")
    assert "/* EXPORT protel_add" in cpp
    assert "int16_t protel_add(int16_t a, int16_t b)" in cpp
    assert "return (a + b)" in cpp
    assert "int main()" not in cpp


@pytest.mark.skipif(shutil.which("rustc") is None, reason="rustc not installed")
def test_rust_interop_examples_build_and_run():
    script = INTEROP / "build_interop_rust.sh"
    subprocess.run(["bash", str(script)], cwd=ROOT, check=True, text=True)