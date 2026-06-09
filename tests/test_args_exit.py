"""ENTRY argc/argv and RETURN exit status (Introductory Manual §5.5.2)."""

import subprocess
from pathlib import Path

import pytest

from src.cpp_transpiler import transpile_to_cpp
from src.parser import parse_protel
from src.transpiler import TranspileError

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / "examples" / "intro_5_5_2_args_exit.P"
PROTEL = ROOT / "Pc"
PYTHON = ROOT / ".venv" / "bin" / "python"


def test_parse_entry_with_unix_argv_parms():
    tree = parse_protel(
        "SECTION demo;\n"
        "TYPE integer {-1 TO 1};\n"
        "TYPE char {0 TO 255};\n"
        "DCL Start PROC(argc integer, argv PTR TO PTR TO char) IS ENTRY;\n"
    )
    decl = tree[0].declarations[-1]
    assert decl.entry
    assert decl.name == "Start"
    assert len(decl.parms) == 2


def test_entry_unix_argv_emits_main_with_forwarding():
    source = EXAMPLE.read_text(encoding="utf-8")
    cpp = transpile_to_cpp(parse_protel(source), source_name=EXAMPLE.name)
    assert "int main(int argc, char** argv)" in cpp
    assert "return protel_generated::ArgsExit::Start(argc, argv);" in cpp
    assert "int16_t Start(int16_t argc, char * * argv)" in cpp


def test_entry_parm_mismatch_raises():
    with pytest.raises(TranspileError, match="parameters must match"):
        transpile_to_cpp(
            parse_protel(
                "SECTION s;\n"
                "TYPE integer {-1 TO 1};\n"
                "TYPE char {0 TO 255};\n"
                "DCL Start PROC(argc integer, argv PTR TO PTR TO char) IS ENTRY;\n"
                "DCL Start PROC() RETURNS integer IS BLOCK RETURN 0; ENDBLOCK;\n"
            )
        )


def test_args_exit_compiles_prints_and_returns_argc():
    binary = ROOT / "build" / "ArgsExit_test"
    result = subprocess.run(
        [
            str(PYTHON),
            str(PROTEL),
            str(EXAMPLE),
            "-o",
            str(binary),
            "--run",
            "--",
            "one",
            "two",
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 3, result.stderr
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert lines[-2:] == ["one", "two"]
    assert lines[0].endswith("ArgsExit_test") or "ArgsExit" in lines[0]