#!/usr/bin/env bash
# Build Swift <-> PROTEL interop demos (macOS / Linux with Swift installed).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build/interop"
PC="$ROOT/Pc"
RUNTIME="$ROOT/src/runtime/protel_io.c"

mkdir -p "$BUILD"

if ! command -v swiftc >/dev/null 2>&1; then
    echo "interop: swiftc not found; install Swift toolchain to build runnable demos" >&2
    exit 1
fi

CXX="$(command -v clang++ || command -v g++)"

echo "=== PROTEL calls Swift ==="
"$PC" "$ROOT/examples/interop/protel_calls_swift.P" \
    --keep -o "$BUILD/protel_calls_swift.cpp"
"$CXX" -std=c++20 -Wall -I"$ROOT/src/runtime" -c "$BUILD/protel_calls_swift.cpp" \
    -o "$BUILD/protel_calls_swift.o"
swiftc -parse-as-library -c "$ROOT/examples/interop/swift_greet.swift" \
    -o "$BUILD/swift_greet.o"
"$CXX" "$BUILD/protel_calls_swift.o" "$BUILD/swift_greet.o" "$RUNTIME" \
    -o "$BUILD/protel_calls_swift"
"$BUILD/protel_calls_swift"

echo "=== Swift calls PROTEL ==="
"$PC" "$ROOT/examples/interop/protel_for_swift.P" \
    --keep -o "$BUILD/protel_for_swift.cpp"
"$CXX" -std=c++20 -Wall -I"$ROOT/src/runtime" -c "$BUILD/protel_for_swift.cpp" \
    -o "$BUILD/protel_for_swift.o"
swiftc "$ROOT/examples/interop/swift_calls_protel.swift" "$BUILD/protel_for_swift.o" \
    -o "$BUILD/swift_calls_protel"
"$BUILD/swift_calls_protel"