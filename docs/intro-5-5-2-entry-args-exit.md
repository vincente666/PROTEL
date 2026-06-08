# 5.5.2 UNIX Command Line and Shell Exit Status

**PROTEL Introductory Manual 2026** — Vincente D'Ingianni

---

## 5.5.2 UNIX `argc` / `argv` and `RETURN` as Exit Status

On macOS and UNIX/Linux hosts, a standalone program's **IS ENTRY** procedure may receive the host command-line argument count and vector. A **RETURN** from an ENTRY body declared **RETURNS integer** becomes the process exit status observed by the shell (`echo $?`).

### Entry declaration

The **IS ENTRY** forward declaration may use the standard UNIX parameter list:

```protel
DCL Start PROC(argc integer, argv PTR TO PTR TO char) IS ENTRY;
```

The procedure body must use the same parameter list. To propagate a status to the shell, declare **RETURNS integer** on the body:

```protel
DCL Start PROC(argc integer, argv PTR TO PTR TO char) RETURNS integer IS
   BLOCK
      ...
      RETURN status;
   ENDBLOCK;
```

Programs without command-line arguments continue to use the classical form from §5.5.2:

```protel
DCL Start PROC() IS ENTRY;
DCL Start PROC() IS
   BLOCK
      ...
   ENDBLOCK;
```

### Generated host `main`

The C++ transpiler emits a POSIX `main` that forwards `argc` and `argv` and returns the ENTRY result:

```cpp
int main(int argc, char** argv) {
    return protel_generated::ArgsExit::Start(argc, argv);
}
```

When the ENTRY body does not **RETURNS integer**, the wrapper calls the procedure and returns `0`.

### Example: `examples/intro_5_5_2_args_exit.protel`

This module prints each command-line argument (including the program name) and **RETURN**s `argc` as the exit status.

Build and run:

```bash
./protel examples/intro_5_5_2_args_exit.protel -o build/ArgsExit --run -- one two
echo $?
```

Arguments after `--` are forwarded to the compiled program when using **`--run`**.

Expected output:

```
build/ArgsExit
one
two
```

Expected exit status: `3` (program name plus two arguments).

### I/O

Command-line demonstration uses **EXTERNAL** C linkage to the minimal POSIX runtime (`writeln` in `src/runtime/protel_io.c`). I/O is not **INTRINSIC** and the transpiler does not emit `#include <iostream>`.

### See also

- §7.0 — **PROTEL 2026 Development Tools** (`protel` driver, `--run`)
- §7.0.5 — **Runnable `.protel` files (shebang)** — direct execution with `#!/usr/bin/env protel-run`
- Reference Manual §13 — **EXPORT** / **EXTERNAL** (ENTRY vs library procedures)