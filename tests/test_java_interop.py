"""Java interop example tests (transpile + optional link)."""

import shutil
import subprocess
from pathlib import Path

import pytest

from src.cpp_transpiler import transpile_to_cpp
from src.parser import parse_protel

ROOT = Path(__file__).resolve().parent.parent
INTEROP = ROOT / "examples" / "interop"


def _java_runtime_available() -> bool:
    if shutil.which("javac") is None or shutil.which("java") is None:
        return False
    try:
        subprocess.run(["java", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def test_protel_calls_java_emits_external_java_greet():
    source = (INTEROP / "protel_calls_java.protel").read_text(encoding="utf-8")
    cpp = transpile_to_cpp(parse_protel(source), source_name="protel_calls_java.protel")
    assert 'extern "C"' in cpp
    assert "void java_greet(const char* name, int16_t value)" in cpp
    assert "java_greet(" in cpp
    assert "protel_generated::protel_calls_java::Start()" in cpp


def test_protel_for_java_exports_c_linkage():
    source = (INTEROP / "protel_for_java.protel").read_text(encoding="utf-8")
    cpp = transpile_to_cpp(parse_protel(source), source_name="protel_for_java.protel")
    assert "/* EXPORT protel_add" in cpp
    assert "int16_t protel_add(int16_t a, int16_t b)" in cpp
    assert "return (a + b)" in cpp
    assert "int main()" not in cpp


def test_java_calls_protel_uses_jni_bridge():
    bridge = (INTEROP / "java_calls_protel.c").read_text(encoding="utf-8")
    java_src = (INTEROP / "JavaCallsProtel.java").read_text(encoding="utf-8")
    assert "Java_JavaCallsProtel_protelAdd" in bridge
    assert "protel_add" in bridge
    assert "System.loadLibrary" in java_src
    assert "native short protelAdd" in java_src


@pytest.mark.skipif(not _java_runtime_available(), reason="JDK not installed")
def test_java_interop_examples_build_and_run():
    script = INTEROP / "build_interop_java.sh"
    subprocess.run(["bash", str(script)], cwd=ROOT, check=True, text=True)