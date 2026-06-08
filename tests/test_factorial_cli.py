"""Factorial CLI example: USES §1.3 module + printf/atoi C interop."""

import subprocess
from pathlib import Path

from src.cpp_transpiler import transpile_to_cpp
from src.parser import parse_protel

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / "examples" / "intro_1_3_factorial_cli.protel"
FACTORIAL = ROOT / "examples" / "intro_1_3_factorial.protel"
PROTEL = ROOT / "protel"
PYTHON = ROOT / ".venv" / "bin" / "python"


def test_factorial_cli_transpile_uses_and_externals():
    source = EXAMPLE.read_text(encoding="utf-8")
    cpp = transpile_to_cpp(
        parse_protel(source),
        source_name=EXAMPLE.name,
        source_path=EXAMPLE,
    )
    assert "/* USES: factorial_demo */" in cpp
    assert "using factorial_demo::factorial;" in cpp
    assert "int16_t factorial(int16_t n)" in cpp
    assert "#include <cstdio>" in cpp
    assert "#include <cstdlib>" in cpp
    assert "int main(int argc, char** argv)" in cpp


def test_factorial_source_unchanged():
    text = FACTORIAL.read_text(encoding="utf-8")
    assert "SECTION factorial_demo;" in text
    assert "IS ENTRY" not in text
    assert "USES" not in text


def test_factorial_cli_compiles_and_prints_result():
    binary = ROOT / "build" / "factorial_cli_test"
    result = subprocess.run(
        [
            str(PYTHON),
            str(PROTEL),
            str(EXAMPLE),
            "-o",
            str(binary),
            "--run",
            "--",
            "5",
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    assert "5! = 120" in result.stdout


def test_factorial_cli_usage_exit_status():
    binary = ROOT / "build" / "factorial_cli_usage"
    result = subprocess.run(
        [
            str(PYTHON),
            str(PROTEL),
            str(EXAMPLE),
            "-o",
            str(binary),
            "--run",
            "--",
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 1, result.stderr
    assert "Usage: factorial N" in result.stdout