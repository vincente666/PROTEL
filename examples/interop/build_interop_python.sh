#!/usr/bin/env bash
# Build Python <-> PROTEL interop demos (macOS / Linux with Python 3 dev headers).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build/interop"
PROTEL="$ROOT/protel"
RUNTIME="$ROOT/src/runtime/protel_io.c"
INTEROP="$ROOT/examples/interop"

mkdir -p "$BUILD"

if ! command -v python3 >/dev/null 2>&1; then
    echo "interop: python3 not found" >&2
    exit 1
fi

PYTHON="${PYTHON:-python3}"
if ! "$PYTHON" -c "import sysconfig; sysconfig.get_config_var('LIBDIR')" >/dev/null 2>&1; then
    echo "interop: Python development headers not available (install python3-dev)" >&2
    exit 1
fi

PY_CONFIG=""
if command -v python3-config >/dev/null 2>&1; then
    PY_CONFIG="python3-config"
elif command -v "$PYTHON-config" >/dev/null 2>&1; then
    PY_CONFIG="$PYTHON-config"
fi

if [ -n "$PY_CONFIG" ]; then
    PY_CFLAGS="$("$PY_CONFIG" --includes)"
    if "$PY_CONFIG" --embed --ldflags >/dev/null 2>&1; then
        PY_LDFLAGS="$("$PY_CONFIG" --embed --ldflags)"
    else
        PY_LDFLAGS="$("$PY_CONFIG" --ldflags)"
    fi
else
    PY_CFLAGS=$("$PYTHON" -c "import sysconfig; print('-I' + sysconfig.get_config_var('INCLUDEPY'))")
    PY_LDFLAGS=$("$PYTHON" -c "import sysconfig; print('-L' + sysconfig.get_config_var('LIBDIR') + ' -lpython' + sysconfig.get_config_var('VERSION') + ' ' + (sysconfig.get_config_var('LIBS') or ''))")
fi

CXX="$(command -v clang++ || command -v g++)"
CC="$(command -v clang || command -v gcc)"

if [ "$(uname -s)" = "Darwin" ]; then
    SHLIB_EXT="dylib"
    SHLIB_FLAGS="-dynamiclib -Wl,-undefined,dynamic_lookup"
else
    SHLIB_EXT="so"
    SHLIB_FLAGS="-shared -fPIC"
fi

echo "=== PROTEL calls Python ==="
"$PROTEL" "$INTEROP/protel_calls_python.protel" \
    --keep -o "$BUILD/protel_calls_python.cpp"
"$CXX" -std=c++20 -Wall -I"$ROOT/src/runtime" -c "$BUILD/protel_calls_python.cpp" \
    -o "$BUILD/protel_calls_python.o"
# shellcheck disable=SC2086
"$CC" -Wall -c "$INTEROP/python_greet.c" -o "$BUILD/python_greet.o" $PY_CFLAGS
# shellcheck disable=SC2086
"$CXX" "$BUILD/protel_calls_python.o" "$BUILD/python_greet.o" "$RUNTIME" \
    $PY_LDFLAGS -o "$BUILD/protel_calls_python"
(cd "$ROOT" && "$BUILD/protel_calls_python")

echo "=== Python calls PROTEL ==="
"$PROTEL" "$INTEROP/protel_for_python.protel" \
    --keep -o "$BUILD/protel_for_python.cpp"
"$CXX" -std=c++20 -Wall -fPIC -I"$ROOT/src/runtime" -c "$BUILD/protel_for_python.cpp" \
    -o "$BUILD/protel_for_python.o"
"$CXX" $SHLIB_FLAGS -std=c++20 "$BUILD/protel_for_python.o" \
    -o "$BUILD/libprotel_for_python.$SHLIB_EXT"
"$PYTHON" "$INTEROP/python_calls_protel.py"