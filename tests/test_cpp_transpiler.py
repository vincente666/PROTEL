"""C++ transpiler and Hello World tests."""

import os
import stat
import subprocess
from pathlib import Path

from src.parser import parse_protel
from src.cpp_transpiler import transpile_to_cpp

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"
PROTEL = ROOT / "Pc"


def _transpile_hello() -> str:
    source = (EXAMPLES / "Hello.P").read_text(encoding="utf-8")
    tree = parse_protel(source)
    return transpile_to_cpp(tree, source_name="Hello.P")


def test_cpp_hello_emits_namespace_and_main():
    cpp = _transpile_hello()
    assert "namespace protel_generated" in cpp
    assert "namespace Hello" in cpp
    assert "IS ENTRY" in (EXAMPLES / "Hello.P").read_text(encoding="utf-8")
    assert "void Start()" in cpp
    assert 'extern "C"' in cpp
    assert "void writeln(const char* msg)" in cpp
    assert "<iostream>" not in cpp
    assert "IS INTRINSIC" not in (EXAMPLES / "Hello.P").read_text(encoding="utf-8")
    assert "EXTERNAL" in (EXAMPLES / "Hello.P").read_text(encoding="utf-8")
    assert "int main()" in cpp
    assert "protel_generated::Hello::Start()" in cpp
    assert "(const char[]){" in cpp
    assert ", 0 }" in cpp
    assert '"Hello, World!"' not in cpp


def test_cpp_hello_class_uses_this():
    source = (EXAMPLES / "ref_oo_class_with_var.P").read_text(encoding="utf-8")
    cpp = transpile_to_cpp(parse_protel(source), source_name="ref_oo_class_with_var.P")
    assert "class class_with_var" in cpp
    assert "static int16_t class_var" in cpp
    assert "class_with_var::class_method" in cpp
    assert "class_with_var::class_var = 5" in cpp
    assert "void class_with_var::instance_method" in cpp
    assert "this->instance_var" in cpp


def test_hello_compiles_and_runs():
    result = subprocess.run(
        [
            str(ROOT / ".venv/bin/python"),
            str(PROTEL),
            str(EXAMPLES / "Hello.P"),
            "-o",
            str(ROOT / "build" / "Hello"),
            "--run",
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    assert "Hello, World!" in result.stdout


def test_hello_shebang_direct_execution():
    hello = EXAMPLES / "Hello.P"
    assert hello.read_text(encoding="utf-8").startswith("#!/usr/bin/env Pc!")
    mode = hello.stat().st_mode
    hello.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    env = dict(os.environ)
    env["PATH"] = f"{ROOT}:{env.get('PATH', '')}"
    result = subprocess.run(
        [str(hello.resolve())],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    assert "Hello, World!" in result.stdout


def test_hello_compiles_and_runs_a_out():
    result = subprocess.run(
        [str(ROOT / ".venv/bin/python"), str(PROTEL), "examples/Hello.P", "--run"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    assert "Hello, World!" in result.stdout
    assert (ROOT / "a.out").exists()


def test_cpp_oo_examples_compile():
    from src.compile import check_cpp_syntax

    for name in ("ref_oo_class_with_var.P", "ref_oo_class_method_invoke.P"):
        source = EXAMPLES / name
        tree = parse_protel(source.read_text(encoding="utf-8"))
        cpp = transpile_to_cpp(tree, source_name=name)
        cpp_path = ROOT / "build" / f"{name.replace('.P', '.cpp')}"
        cpp_path.parent.mkdir(parents=True, exist_ok=True)
        cpp_path.write_text(cpp, encoding="utf-8")
        check_cpp_syntax(cpp_path)


def test_parse_external_proc():
    tree = parse_protel(
        "SECTION s;\nDCL writeln PROC(msg PTR TO char) EXTERNAL;\n"
    )
    decl = tree[0].declarations[0]
    assert decl.external
    assert decl.name == "writeln"