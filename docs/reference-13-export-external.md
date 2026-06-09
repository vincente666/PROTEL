# 13.0 EXTERNAL and EXPORT Procedures

**PROTEL Reference Manual 2026** — Vincente D'Ingianni

---

## 13.0 EXTERNAL and EXPORT Procedures

PROCEDURE constants may be declared **EXTERNAL** (import a foreign routine) or **EXPORT** (publish a PROTEL routine for foreign callers). In the PROTEL 2026 transpiler, both map to the **C application binary interface (ABI)** so that code produced by GCC, Clang, Swift, Rust, Python (via **ctypes** or a C embedding shim), Java (via **JNI**), and other C-compatible toolchains can be linked with PROTEL modules.

Ordinary procedure constants (without EXTERNAL or EXPORT) are emitted inside C++ namespaces and are intended for use within the PROTEL module. EXTERNAL and EXPORT procedures use `extern "C"` linkage at the generated C/C++ level so that symbol names are stable and unmangled.

---

## SYNTAX

```
<DCL GROUP> ::= <PROCEDURE DCL GROUP><PROCEDURE INIT>

<PROCEDURE INIT> ::= IS <BLOCK>
                   | IS INTRINSIC
                   | IS ENTRY
                   | EXTERNAL
                   | EXPORT

<PROCEDURE DCL GROUP> ::= <ID LIST><PROCEDURE ATTRIBUTES>
```

**EXTERNAL** and **EXPORT** are mutually exclusive with **IS** \<block\>, **IS INTRINSIC**, and **IS ENTRY** on the same declaration.

An EXPORT or EXTERNAL declaration is a **forward** declaration (like **IS FORWARD**). The procedure body, if any, appears in a subsequent **DCL** statement with the same name and compatible signature in the **same section**.

---

## EXTERNAL (import)

### Description

1. **EXTERNAL** declares that the named procedure is **implemented outside** the current module (typically in C, C++, Rust, Swift, Python via a C API bridge, Java via JNI, or another language that exports C-callable symbols).

2. The transpiler emits an `extern "C"` **prototype** only. No code is generated for the body.

3. Parameter and return types are mapped to C types (for example, **integer** → `int16_t`, **PTR TO char** → `const char*` for string arguments in external calls).

4. **PROTEL strings are not NUL-terminated.** When passing text to an EXTERNAL procedure that expects a C string, the caller must supply an **explicit trailing `0`** byte in a char tuple (see Introductory Manual §7.3).

### Examples

```
DCL writeln PROC(msg PTR TO char) EXTERNAL;

DCL rust_greet PROC(name PTR TO char, value integer) EXTERNAL;

DCL python_greet PROC(name PTR TO char, value integer) EXTERNAL;

DCL java_greet PROC(name PTR TO char, value integer) EXTERNAL;

DCL read_config PROC(path PTR TO char, size integer) RETURNS integer EXTERNAL;
```

### Generated C++ (conceptual)

```cpp
extern "C" {
    void writeln(const char* msg);
    void rust_greet(const char* name, int16_t value);
    int16_t read_config(const char* path, int16_t size);
}
```

---

## EXPORT (publish)

### Description

1. **EXPORT** declares that a procedure constant is part of the **public foreign interface** of the module. The implementation is emitted with `extern "C"` linkage at global scope (outside C++ namespaces).

2. There is no restriction on the number of EXPORT procedures per module (unlike **ENTRY**, which is limited to one per module).

3. EXPORT implies a forward declaration. The body must follow in the same section with an identical signature (parameter list, **RETURNS** type, and procedure class).

4. EXPORT procedures are suitable for **INTERFACE** sections that act as libraries for C, Swift, Rust, Python, Java, or other hosts. They do not, by themselves, define a program entry point. Use **IS ENTRY** for executable programs.

5. EXPORT must not be combined with **IS ENTRY** on the same procedure name.

### Examples

```
INTERFACE protel_math;

TYPE integer {-32768 TO 32767};

DCL protel_add PROC(a integer, b integer) RETURNS integer EXPORT;

DCL protel_add PROC(a integer, b integer) RETURNS integer IS
   BLOCK
      RETURN a + b;
   ENDBLOCK;
```

### Generated C++ (conceptual)

```cpp
namespace protel_generated {
namespace protel_math {
    /* EXPORT protel_add (defined with C linkage below) */
}
}

extern "C" {
    int16_t protel_add(int16_t a, int16_t b)
    {
        return (a + b);
    }
}
```

---

## Comparison with other procedure initialisers

| Clause | Purpose | Body location | Linkage | Count per module |
|--------|---------|---------------|---------|------------------|
| *(none)* | Internal procedure | Same section | C++ namespace | unlimited |
| **IS FORWARD** | Forward reference | Later in module | C++ namespace | unlimited |
| **IS ENTRY** | Program entry | Same or other section | C++ namespace; host `main` calls ENTRY | **one** |
| **IS INTRINSIC** | Machine primitive | Compiler provided | implementation-defined | unlimited |
| **EXTERNAL** | Import foreign | Foreign object file | `extern "C"` import | unlimited |
| **EXPORT** | Export to foreign | Same section | `extern "C"` export | unlimited |

---

## Type mapping for foreign calls

| PROTEL type | C/C++ type (typical) | Notes |
|-------------|----------------------|-------|
| **integer** | `int16_t` | Range {-32768 TO 32767} |
| **char** (range) | `uint8_t` | Single byte |
| **PTR TO char** | `const char*` | Caller supplies NUL if C string required |
| **BOOL** | `bool` / `uint8_t` | Implementation-defined packing |
| **PROC** (procedure value) | function pointer | Rare in EXTERNAL declarations |

---

## Linking

1. Transpile PROTEL to `.cpp` with the PROTEL 2026 compiler (`Pc`).

2. Compile generated C++ with `g++` or `clang++` (`-std=c++20`).

3. Compile foreign sources (`.c`, `.rs`, `.swift`, `.java`, etc.) to objects or static libraries using the foreign toolchain. For **Python → PROTEL**, compile the EXPORT module as a shared library and load it with **`ctypes.CDLL`**. For **PROTEL → Python**, link a C shim that embeds the Python interpreter (`python_greet.c` in `examples/interop/`). For **Java → PROTEL**, link the EXPORT module with a JNI bridge (`java_calls_protel.c`). For **PROTEL → Java**, link a C shim that embeds the JVM (`java_greet.c`).

4. Link all objects with the same C ABI conventions. On macOS and Linux, `clang++` is commonly used as the final link driver. Python embedding requires linking `libpython` (see `python3-config --embed --ldflags`). Java embedding requires linking `libjvm` from `$JAVA_HOME/lib/server`.

5. The minimal PROTEL I/O runtime (`protel_io.c`) is linked only when EXTERNAL procedures such as `writeln` from the example runtime are referenced.

---

## Restrictions and diagnostics

1. EXPORT and EXTERNAL declarations and their bodies must reside in the **same section**.

2. Duplicate EXPORT declarations or duplicate bodies for the same EXPORT name are rejected at transpile time.

3. EXPORT declaration and body signatures must match exactly.

4. Calling an EXTERNAL routine with a PROTEL string literal that lacks an explicit `0` suffix produces a **warning** (C interop requires NUL-terminated buffers for `const char*` parameters).

---

## See also

- §12.0 Intrinsic Procedures (machine-level **INTRINSIC**; not used for ordinary I/O in PROTEL 2026)
- Introductory Manual §7.2 — EMACS PROTEL mode
- Introductory Manual §7.3 — Foreign language interoperability (how-to)
- Introductory Manual §5.5.2 — **IS ENTRY**, UNIX `argc`/`argv`, and shell exit status (`docs/intro-5-5-2-entry-args-exit.md`)