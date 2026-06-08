#!/usr/bin/env python3
"""Python program calling an EXPORTed PROTEL procedure via ctypes (C ABI)."""
from __future__ import annotations

import ctypes
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "build" / "interop"

if sys.platform == "darwin":
    LIB_NAME = "libprotel_for_python.dylib"
elif sys.platform == "win32":
    LIB_NAME = "protel_for_python.dll"
else:
    LIB_NAME = "libprotel_for_python.so"

LIB_PATH = BUILD / LIB_NAME


def main() -> None:
    if not LIB_PATH.is_file():
        raise SystemExit(f"missing shared library: {LIB_PATH} (run build_interop_python.sh)")

    lib = ctypes.CDLL(str(LIB_PATH))
    lib.protel_add.argtypes = (ctypes.c_int16, ctypes.c_int16)
    lib.protel_add.restype = ctypes.c_int16

    total = lib.protel_add(40, 2)
    print(f"Python: protel_add(40, 2) = {total}")


if __name__ == "__main__":
    main()