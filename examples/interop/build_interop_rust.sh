#!/usr/bin/env bash
# Build Rust <-> PROTEL interop demos (macOS / Linux with Rust installed).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build/interop"
PC="$ROOT/Pc"
RUNTIME="$ROOT/src/runtime/protel_io.c"

mkdir -p "$BUILD"

if ! command -v rustc >/dev/null 2>&1; then
    echo "interop: rustc not found; install Rust (rustup) to build runnable demos" >&2
    exit 1
fi

CXX="$(command -v clang++ || command -v g++)"

echo "=== PROTEL calls Rust ==="
"$PC" "$ROOT/examples/interop/protel_calls_rust.P" \
    --keep -o "$BUILD/protel_calls_rust.cpp"
"$CXX" -std=c++20 -Wall -I"$ROOT/src/runtime" -c "$BUILD/protel_calls_rust.cpp" \
    -o "$BUILD/protel_calls_rust.o"
rustc --crate-type staticlib "$ROOT/examples/interop/rust_greet.rs" \
    -o "$BUILD/librust_greet.a"
"$CXX" "$BUILD/protel_calls_rust.o" "$BUILD/librust_greet.a" "$RUNTIME" \
    -o "$BUILD/protel_calls_rust"
"$BUILD/protel_calls_rust"

echo "=== Rust calls PROTEL ==="
"$PC" "$ROOT/examples/interop/protel_for_rust.P" \
    --keep -o "$BUILD/protel_for_rust.cpp"
"$CXX" -std=c++20 -Wall -I"$ROOT/src/runtime" -c "$BUILD/protel_for_rust.cpp" \
    -o "$BUILD/protel_for_rust.o"
rustc "$ROOT/examples/interop/rust_calls_protel.rs" "$BUILD/protel_for_rust.o" \
    -o "$BUILD/rust_calls_protel"
"$BUILD/rust_calls_protel"