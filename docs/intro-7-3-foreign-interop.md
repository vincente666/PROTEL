# 7.3 Foreign Language Interoperability

**PROTEL Introductory Manual 2026** — Vincente D'Ingianni

---

## 7.3 Foreign Language Interoperability

PROTEL 2026 programs can call routines written in **C**, **C++**, **Swift**, **Rust**, **Python** (via a thin C embedding shim), **Java** (via JNI), and other languages that support the **C calling convention**. Likewise, foreign programs can call procedures you publish from PROTEL. This is the recommended approach for I/O, platform APIs, and performance-critical libraries: PROTEL does **not** use **INTRINSIC** for ordinary host I/O in the 2026 toolchain.

All foreign interop goes through two declarations:

| Direction | PROTEL keyword | Foreign side |
|-----------|----------------|--------------|
| Foreign → PROTEL | **EXPORT** | Import C symbol (e.g. `extern "C"`, Swift `@_silgen_name`, Rust `extern "C"`, Python `ctypes.CDLL`, Java JNI bridge) |
| PROTEL → Foreign | **EXTERNAL** | Export C symbol (e.g. C compilation unit, `#[no_mangle]`, `@_cdecl`, Python C API shim, JNI JVM embed) |

Working examples live under `examples/interop/` in the PROTEL distribution.

---

## 7.3.1 Strings and the C boundary

PROTEL character strings are **tuples of bytes** with a compile-time length. They are **not** automatically NUL-terminated when passed to C.

When a C, Swift, Rust, Python (via C), or Java (via JNI/C) function expects a `char*` / C string, append an explicit **zero** byte in a char tuple:

```
writeln({'Hello', 0});
swift_greet({'PROTEL', 0}, 42);
```

The compiler emits a `(const char[]){ ... }` array; the trailing `0` is your responsibility.

---

## 7.3.2 Calling foreign code from PROTEL (EXTERNAL)

### Step 1 — Declare the foreign routine

```
DCL writeln PROC(msg PTR TO char) EXTERNAL;
```

### Step 2 — Implement it in the foreign language

**C** (`examples/interop` pattern / `protel_io.c`):

```c
void writeln(const char* msg) {
    /* write(2) based implementation */
}
```

**Rust** (`rust_greet.rs`):

```rust
#[no_mangle]
pub extern "C" fn rust_greet(name: *const i8, value: i16) { /* ... */ }
```

**Swift** (`swift_greet.swift`):

```swift
@_cdecl("swift_greet")
public func swift_greet(_ name: UnsafePointer<CChar>, _ value: Int32) { /* ... */ }
```

**Python** (via C embedding shim `python_greet.c`):

```c
void python_greet(const char* name, int16_t value) {
    /* Py_Initialize, import greet_helper, call greet(name, value) */
}
```

PROTEL does not call the Python interpreter directly. A small **C** translation unit exposes `python_greet` with C linkage; it embeds Python and forwards to `greet_helper.py`. Link against `libpython` (Python development headers required).

**Java** (via JNI embedding shim `java_greet.c`):

```c
void java_greet(const char* name, int16_t value) {
    /* JNI_CreateJavaVM, FindClass("GreetHelper"), CallStaticVoidMethod greet */
}
```

PROTEL does not call the JVM directly. A **C** shim exposes `java_greet` with C linkage, embeds the JVM, and forwards to `GreetHelper.java`. Link against `libjvm` (`$JAVA_HOME/include`, JDK required).

### Step 3 — Call from PROTEL

```
DCL Start PROC() IS ENTRY;

DCL Start PROC() IS
   BLOCK
      rust_greet({'PROTEL', 0}, 42);
      writeln({'done', 0});
   ENDBLOCK;
```

### Step 4 — Build and link

```bash
protel myprog.protel --keep -o build/myprog.cpp
clang++ -std=c++20 -c build/myprog.cpp -o build/myprog.o
rustc --crate-type staticlib rust_greet.rs -o build/librust_greet.a
clang++ build/myprog.o build/librust_greet.a src/runtime/protel_io.c -o myprog
```

See `examples/interop/build_interop.sh`, `build_interop_rust.sh`, `build_interop_python.sh`, and `build_interop_java.sh`.

---

## 7.3.3 Publishing PROTEL routines for foreign callers (EXPORT)

### Step 1 — Forward EXPORT declaration

```
INTERFACE protel_math;

TYPE integer {-32768 TO 32767};

DCL protel_add PROC(a integer, b integer) RETURNS integer EXPORT;
```

### Step 2 — Procedure body (same section)

```
DCL protel_add PROC(a integer, b integer) RETURNS integer IS
   BLOCK
      RETURN a + b;
   ENDBLOCK;
```

The transpiler places the implementation in an `extern "C"` block so the symbol name is `protel_add`.

### Step 3 — Import from foreign code

**C**:

```c
#include <stdint.h>
int16_t protel_add(int16_t a, int16_t b);
```

**Rust** (`rust_calls_protel.rs`):

```rust
extern "C" {
    fn protel_add(a: i16, b: i16) -> i16;
}
```

**Swift** (`swift_calls_protel.swift`):

```swift
@_silgen_name("protel_add")
func protel_add(_ a: Int16, _ b: Int16) -> Int16
```

**Python** (`python_calls_protel.py`):

```python
import ctypes

lib = ctypes.CDLL("build/interop/libprotel_for_python.dylib")  # .so on Linux
lib.protel_add.argtypes = (ctypes.c_int16, ctypes.c_int16)
lib.protel_add.restype = ctypes.c_int16
sum = lib.protel_add(40, 2)
```

Build the PROTEL EXPORT module as a **shared library** (`.dylib` / `.so`), then load it with **`ctypes.CDLL`**. No Python extension module is required on the PROTEL side.

**Java** (`JavaCallsProtel.java` + `java_calls_protel.c`):

```java
public final class JavaCallsProtel {
    static { System.loadLibrary("javacallsprotel"); }
    private static native short protelAdd(short a, short b);
}
```

Compile the EXPORT module and a thin **JNI** bridge into `libjavacallsprotel.dylib` (`.so` on Linux). `System.loadLibrary` loads the combined library; the JNI stub forwards to the EXPORTed `protel_add` symbol.

### Step 4 — Link

```bash
protel protel_for_rust.protel --keep -o build/protel_for_rust.cpp
clang++ -std=c++20 -c build/protel_for_rust.cpp -o build/protel_for_rust.o
rustc rust_calls_protel.rs build/protel_for_rust.o -o rust_calls_protel
```

**Python** (shared library + ctypes):

```bash
protel protel_for_python.protel --keep -o build/protel_for_python.cpp
clang++ -std=c++20 -fPIC -c build/protel_for_python.cpp -o build/protel_for_python.o
clang++ -shared -o build/libprotel_for_python.so build/protel_for_python.o
python3 examples/interop/python_calls_protel.py
```

**Java** (shared library + JNI):

```bash
protel protel_for_java.protel --keep -o build/protel_for_java.cpp
clang++ -std=c++20 -fPIC -c build/protel_for_java.cpp -o build/protel_for_java.o
clang -fPIC -c java_calls_protel.c -o build/java_calls_protel.o -I$JAVA_HOME/include
clang++ -shared -o build/libjavacallsprotel.so build/protel_for_java.o build/java_calls_protel.o
java -Djava.library.path=build/interop -cp build/interop JavaCallsProtel
```

---

## 7.3.4 Complete minimal examples

### PROTEL calls Rust

File: `examples/interop/protel_calls_rust.protel`

```
SECTION protel_calls_rust;

TYPE char {0 TO 255};
TYPE integer {-32768 TO 32767};

DCL rust_greet PROC(name PTR TO char, value integer) EXTERNAL;
DCL writeln PROC(msg PTR TO char) EXTERNAL;

DCL Start PROC() IS ENTRY;

DCL Start PROC() IS
   BLOCK
      rust_greet({'PROTEL', 0}, 42);
      writeln({'PROTEL called Rust', 0});
   ENDBLOCK;
```

### PROTEL calls Python

File: `examples/interop/protel_calls_python.protel`

```
SECTION protel_calls_python;

TYPE char {0 TO 255};
TYPE integer {-32768 TO 32767};

DCL python_greet PROC(name PTR TO char, value integer) EXTERNAL;
DCL writeln PROC(msg PTR TO char) EXTERNAL;

DCL Start PROC() IS ENTRY;

DCL Start PROC() IS
   BLOCK
      python_greet({'PROTEL', 0}, 42);
      writeln({'PROTEL called Python', 0});
   ENDBLOCK;
```

### Rust calls PROTEL

File: `examples/interop/protel_for_rust.protel` (same EXPORT library as Swift example)

```
INTERFACE protel_math;

TYPE integer {-32768 TO 32767};

DCL protel_add PROC(a integer, b integer) RETURNS integer EXPORT;

DCL protel_add PROC(a integer, b integer) RETURNS integer IS
   BLOCK
      RETURN a + b;
   ENDBLOCK;
```

### PROTEL calls Java

File: `examples/interop/protel_calls_java.protel`

```
SECTION protel_calls_java;

TYPE char {0 TO 255};
TYPE integer {-32768 TO 32767};

DCL java_greet PROC(name PTR TO char, value integer) EXTERNAL;
DCL writeln PROC(msg PTR TO char) EXTERNAL;

DCL Start PROC() IS ENTRY;

DCL Start PROC() IS
   BLOCK
      java_greet({'PROTEL', 0}, 42);
      writeln({'PROTEL called Java', 0});
   ENDBLOCK;
```

### Python calls PROTEL

File: `examples/interop/python_calls_protel.py` loads `protel_for_python.protel` as a shared library via **ctypes**.

### Java calls PROTEL

File: `examples/interop/JavaCallsProtel.java` loads `protel_for_java.protel` via **JNI** (`java_calls_protel.c` bridge).

---

## 7.3.5 ENTRY vs EXPORT

- **IS ENTRY** — marks the **program** entry point. The transpiler emits a host `int main()` that calls your ENTRY procedure. Required for standalone executables.

- **EXPORT** — marks a **library** entry point for foreign languages. Does not create `main`. Use in INTERFACE sections intended to be called from Swift, Rust, Python, Java, C, etc.

A single module may have **one ENTRY** and **many EXPORT** procedures.

---

## 7.3.6 Quick reference

| Task | PROTEL | Build driver |
|------|--------|--------------|
| Hello World (PROTEL only) | `protel Hello.protel --run` | `protel` + `clang++` |
| Hello World (direct shebang) | `./examples/Hello.protel` | §7.0.5 — `export PATH="$PWD:$PATH"`, file executable |
| PROTEL + Swift | `make interop-swift` | `examples/interop/build_interop.sh` |
| PROTEL + Rust | `make interop-rust` | `examples/interop/build_interop_rust.sh` |
| PROTEL + Python | `make interop-python` | `examples/interop/build_interop_python.sh` |
| PROTEL + Java | `make interop-java` | `examples/interop/build_interop_java.sh` |
| Edit `.protel` / `.P` / PLS `.AA01` in Emacs | Add `emacs/` to `load-path`, `(require 'protel-mode)` | See §7.2 |
| Beautify source | `Pb file.protel` | `Pb` |

---

## 7.3.7 Troubleshooting

| Symptom | Likely cause |
|---------|----------------|
| Link error: undefined symbol | EXTERNAL name mismatch; foreign function not `extern "C"` / `#[no_mangle]` / `@_cdecl` |
| Garbled string output | Missing `, 0` NUL suffix on char tuple |
| Duplicate `main` at link | Swift/Rust object compiled with its own `main`; use `-parse-as-library` for helper objects |
| `ctypes` cannot load library | Build EXPORT module as `.dylib`/`.so` first; pass full path to `CDLL` |
| Python embed link error | Install Python dev package (`python3-dev`); use `python3-config --embed --ldflags` (or `python3-config --ldflags`) |
| Python greet silent | Embedded `print` may need `flush=True` when stdout is not a TTY |
| `UnsatisfiedLinkError` (Java) | Set `-Djava.library.path` to the directory containing `libjavacallsprotel`; build JNI bridge first |
| JVM embed link error | Set `JAVA_HOME` to a JDK; link `-L$JAVA_HOME/lib/server -ljvm` with rpath |
| No `main` at link | Program section missing **IS ENTRY** |
| `multiple ENTRY` error | More than one `IS ENTRY` in the module |

For the formal semantics of **EXTERNAL** and **EXPORT**, see Reference Manual §13.0.