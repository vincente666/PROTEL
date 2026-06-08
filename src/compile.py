"""Compile and link PROTEL-generated C++ on macOS / Linux."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_RUNTIME_DIR = Path(__file__).resolve().parent / "runtime"
_RUNTIME_IO_C = _RUNTIME_DIR / "protel_io.c"


def find_cxx_compiler() -> str | None:
    for name in ("g++", "c++", "clang++"):
        path = shutil.which(name)
        if path:
            return path
    return None


def compile_cpp(
    cpp_source: Path,
    output: Path,
    *,
    compile_only: bool = False,
    debug: bool = False,
    link_runtime: bool = True,
    extra_flags: list[str] | None = None,
) -> None:
    compiler = find_cxx_compiler()
    if compiler is None:
        raise RuntimeError("no C++ compiler found (tried g++, c++, clang++)")

    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        compiler,
        "-std=c++20",
        "-Wall",
        "-Wextra",
        f"-I{_RUNTIME_DIR}",
    ]
    if debug:
        cmd.append("-g")
    if extra_flags:
        cmd.extend(extra_flags)

    src = str(cpp_source.resolve())
    if compile_only:
        cmd.extend(["-c", src, "-o", str(output.resolve())])
    else:
        cmd.append(src)
        if link_runtime and _RUNTIME_IO_C.exists():
            cmd.append(str(_RUNTIME_IO_C.resolve()))
        cmd.extend(["-o", str(output.resolve())])

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=_ROOT)
    if result.returncode != 0:
        msg = result.stderr.strip() or result.stdout.strip() or "compile failed"
        raise RuntimeError(msg)


def check_cpp_syntax(
    cpp_source: Path,
    *,
    extra_flags: list[str] | None = None,
) -> None:
    compiler = find_cxx_compiler()
    if compiler is None:
        raise RuntimeError("no C++ compiler found (tried g++, c++, clang++)")

    cmd = [
        compiler,
        "-std=c++20",
        "-Wall",
        "-Wextra",
        f"-I{_RUNTIME_DIR}",
        "-fsyntax-only",
        str(cpp_source.resolve()),
    ]
    if extra_flags:
        cmd.extend(extra_flags)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=_ROOT)
    if result.returncode != 0:
        msg = result.stderr.strip() or result.stdout.strip() or "syntax check failed"
        raise RuntimeError(msg)


def run_executable(
    path: Path,
    program_args: list[str] | None = None,
) -> tuple[int, str, str]:
    exe = path.resolve()
    cmd = [str(exe)]
    if program_args:
        cmd.extend(program_args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=exe.parent,
    )
    return result.returncode, result.stdout, result.stderr