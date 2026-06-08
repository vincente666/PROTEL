# 7.0 PROTEL 2026 Development Tools

**PROTEL Introductory Manual 2026** — Vincente D'Ingianni

---

## 7.0 PROTEL 2026 Development Tools

The PROTEL 2026 toolchain ships with a small set of command-line and editor tools intended for macOS and UNIX/Linux hosts with minimal dependencies.

| Tool | Section | Summary |
|------|---------|---------|
| **`protel`** | §7.1 | Parser, transpiler, and compiler driver |
| **`Pb`** | §7.0.1 | Source beautifier (keyword uppercasing) |
| **`protel-mode`** | §7.2 | GNU Emacs major mode for `.protel`, `.pt`, `.ptl`, legacy `.P`, and PLS `.AA01`–`.ZZ99` files |

---

## 7.0.1 Pb — PROTEL Beautifier

`Pb` uppercases PROTEL reserved keywords for readable, manual-style source. It is a filter-style tool:

```bash
Pb examples/Hello.protel build/Hello.pretty.protel
Pb --bold < myprog.protel > myprog.pretty.protel
```

Install with `make install` (marks `Pb` executable). See `Pb --help` for options.

In Emacs, run Pb on the current buffer with **`C-c C-f`** (`M-x protel-beautify`) — see Introductory Manual §7.2.

---

## 7.0.2 PLS edition modules (`.AA01` … `.ZZ99`)

Historical DMS/PLS modules use edition suffixes such as `vdi.aa01`. The `protel` driver **automatically enables classical preprocessing** for these names (keyword normalization, `$LI` / `$EJECT` linker directives stripped before parse).

```bash
protel vdi.aa01 -c -o build/vdi.aa01.o
make vdi
```

---

## 7.0.3 Type errors and `examples/errors/`

The transpiler performs **strong typing** checks (Reference Manual §11.3). Invalid assignments — such as storing an **integer** into **char** or a **PACK** byte — are rejected before code generation. See `docs/reference-error-messages.md` and `examples/errors/`.

```bash
./protel examples/errors/err_assign_integer_to_char.protel
./protel examples/errors/ok_assign_char_literal.protel -o build/ok_char
```

---

## 7.0.4 UNIX command line and exit status

Standalone programs may read **`argc`** and **`argv`** in the **IS ENTRY** procedure and **RETURN** an integer exit status to the shell. See Introductory Manual §5.5.2 (`docs/intro-5-5-2-entry-args-exit.md`) and `examples/intro_5_5_2_args_exit.protel`.

```bash
./protel examples/intro_5_5_2_args_exit.protel -o build/ArgsExit --run -- one two
echo $?
```

---

## 7.0.5 Runnable `.protel` files (shebang)

A PROTEL source file may be executed directly from the shell when:

1. **Line 1** is a UNIX shebang (`#!...`) naming **`protel-run`** (or `protel --run` via `env -S`).
2. The file is **executable** (`chmod +x`).
3. The PROTEL project directory is on your **`PATH`** so `protel-run` (or `protel`) is found.

The shebang is **not** PROTEL syntax. The preprocessor removes it before parse; **`Pb`** preserves it unchanged when beautifying.

`examples/Hello.protel` demonstrates the usual form:

```protel
#!/usr/bin/env protel-run
% Hello World — run with: ./Hello.protel
SECTION Hello;
...
```

**`protel-run`** is a small helper in the project root. The kernel runs `protel-run /path/to/script.protel [args]`; the helper invokes `protel script.protel --run -- [args]`.

### Setup

From the PROTEL project directory:

```bash
make install
export PATH="$PWD:$PATH"
./examples/Hello.protel
```

From any directory (replace with your checkout path):

```bash
export PATH="$HOME/PROTEL:$PATH"
~/PROTEL/examples/Hello.protel
```

`make install` marks `protel`, `protel-run`, `Pb`, and `examples/Hello.protel` executable.

**PATH pitfall:** `export PATH="~/PROTEL:$PATH"` does **not** work — the shell does not expand `~` inside double quotes, so `env` cannot find `protel-run`. Use **`$PWD`**, **`$HOME/PROTEL`**, or an absolute path instead.

### ENTRY programs with arguments

Add the same shebang to programs such as `examples/intro_5_5_2_args_exit.protel`, then:

```bash
chmod +x examples/intro_5_5_2_args_exit.protel
./examples/intro_5_5_2_args_exit.protel one two
```

The kernel invokes `protel --run -- script.protel one two`. The driver promotes the script path from after **`--`** to the input positional, then forwards **`one`** and **`two`** to the ENTRY procedure.

### Notes

| Topic | Detail |
|-------|--------|
| `%` comments | Cannot replace the shebang; the kernel only recognizes `#!` at the start of the file |
| **`Pb`** | Copies line 1 unchanged when it begins with `#!` |
| **`protel-mode`** | Displays the shebang line with `protel-comment-face` (§7.2) |
| **Parser** | `strip_shebang()` in `src/preprocess.py` runs before keyword normalization |
| **Output binary** | Default `a.out` in the current working directory (same as `protel … --run`) |
| `env: protel: No such file or directory` | **`PATH` wrong** — avoid quoted `~/PROTEL`; use `export PATH="$PWD:$PATH"` from the repo or `export PATH="$HOME/PROTEL:$PATH"` |

---

## See also

- §11.3 — **Type errors** (`docs/reference-error-messages.md`)
- §5.5.2 — **UNIX argc/argv and shell exit status**
- §7.0.5 — **Runnable `.protel` files (shebang)**
- §7.2 — **EMACS PROTEL mode** (`.emacs` setup; automatic `.protel`, `.P`, and PLS suffix detection)
- §7.3 — Foreign language interoperability