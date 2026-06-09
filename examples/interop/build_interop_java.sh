#!/usr/bin/env bash
# Build Java <-> PROTEL interop demos (macOS / Linux with JDK headers).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build/interop"
PC="$ROOT/Pc"
RUNTIME="$ROOT/src/runtime/protel_io.c"
INTEROP="$ROOT/examples/interop"

mkdir -p "$BUILD"

if ! command -v javac >/dev/null 2>&1 || ! command -v java >/dev/null 2>&1; then
    echo "interop: javac/java not found; install a JDK" >&2
    exit 1
fi

if ! java -version >/dev/null 2>&1; then
    echo "interop: java runtime not available; set JAVA_HOME to a JDK" >&2
    exit 1
fi

if [ -z "${JAVA_HOME:-}" ]; then
    if [ "$(uname -s)" = "Darwin" ] && command -v /usr/libexec/java_home >/dev/null 2>&1; then
        JAVA_HOME="$(/usr/libexec/java_home 2>/dev/null || true)"
    fi
fi

if [ -z "${JAVA_HOME:-}" ] || [ ! -d "$JAVA_HOME/include" ]; then
    echo "interop: JAVA_HOME must point to a JDK with JNI headers" >&2
    exit 1
fi

JNI_OS="linux"
if [ "$(uname -s)" = "Darwin" ]; then
    JNI_OS="darwin"
fi

JNI_CFLAGS="-I$JAVA_HOME/include -I$JAVA_HOME/include/$JNI_OS"
if [ -d "$JAVA_HOME/lib/server" ]; then
    JVM_LIBDIR="$JAVA_HOME/lib/server"
else
    JVM_LIBDIR="$JAVA_HOME/jre/lib/server"
fi
JNI_LDFLAGS="-L$JVM_LIBDIR -ljvm -Wl,-rpath,$JVM_LIBDIR"

CXX="$(command -v clang++ || command -v g++)"
CC="$(command -v clang || command -v gcc)"

if [ "$(uname -s)" = "Darwin" ]; then
    SHLIB_EXT="dylib"
    SHLIB_FLAGS="-dynamiclib"
else
    SHLIB_EXT="so"
    SHLIB_FLAGS="-shared -fPIC"
fi

javac -d "$BUILD" "$INTEROP/GreetHelper.java" "$INTEROP/JavaCallsProtel.java"

echo "=== PROTEL calls Java ==="
"$PC" "$INTEROP/protel_calls_java.P" \
    --keep -o "$BUILD/protel_calls_java.cpp"
"$CXX" -std=c++20 -Wall -I"$ROOT/src/runtime" -c "$BUILD/protel_calls_java.cpp" \
    -o "$BUILD/protel_calls_java.o"
# shellcheck disable=SC2086
"$CC" -Wall -c "$INTEROP/java_greet.c" -o "$BUILD/java_greet.o" $JNI_CFLAGS
# shellcheck disable=SC2086
"$CXX" "$BUILD/protel_calls_java.o" "$BUILD/java_greet.o" "$RUNTIME" \
    $JNI_LDFLAGS -o "$BUILD/protel_calls_java"
PROTEL_ROOT="$ROOT" "$BUILD/protel_calls_java"

echo "=== Java calls PROTEL ==="
"$PC" "$INTEROP/protel_for_java.P" \
    --keep -o "$BUILD/protel_for_java.cpp"
"$CXX" -std=c++20 -Wall -fPIC -I"$ROOT/src/runtime" -c "$BUILD/protel_for_java.cpp" \
    -o "$BUILD/protel_for_java.o"
# shellcheck disable=SC2086
"$CC" -Wall -fPIC -c "$INTEROP/java_calls_protel.c" -o "$BUILD/java_calls_protel.o" $JNI_CFLAGS
"$CXX" $SHLIB_FLAGS -std=c++20 "$BUILD/protel_for_java.o" "$BUILD/java_calls_protel.o" \
    -o "$BUILD/libjavacallsprotel.$SHLIB_EXT"
java -Djava.library.path="$BUILD" -cp "$BUILD" JavaCallsProtel