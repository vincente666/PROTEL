"""Swift interop example tests (transpile + optional link)."""

import shutil
import subprocess
from pathlib import Path

import pytest

from src.cpp_transpiler import transpile_to_cpp
from src.parser import parse_protel

ROOT = Path(__file__).resolve().parent.parent
INTEROP = ROOT / "examples" / "interop"


def test_protel_calls_swift_emits_external_swift_greet():
    source = (INTEROP / "protel_calls_swift.protel").read_text(encoding="utf-8")
    cpp = transpile_to_cpp(parse_protel(source), source_name="protel_calls_swift.protel")
    assert 'extern "C"' in cpp
    assert "void swift_greet(const char* name, int16_t value)" in cpp
    assert "swift_greet(" in cpp
    assert "protel_generated::protel_calls_swift::Start()" in cpp


def test_protel_for_swift_exports_c_linkage():
    source = (INTEROP / "protel_for_swift.protel").read_text(encoding="utf-8")
    cpp = transpile_to_cpp(parse_protel(source), source_name="protel_for_swift.protel")
    assert "/* EXPORT protel_add" in cpp
    assert "int16_t protel_add(int16_t a, int16_t b)" in cpp
    assert "return (a + b)" in cpp
    assert "int main()" not in cpp


@pytest.mark.skipif(shutil.which("swiftc") is None, reason="swiftc not installed")
def test_interop_examples_build_and_run():
    script = INTEROP / "build_interop.sh"
    subprocess.run(["bash", str(script)], cwd=ROOT, check=True, text=True)