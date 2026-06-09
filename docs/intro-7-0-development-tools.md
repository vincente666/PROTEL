# 7.0 PROTEL 2026 Development Tools

**PROTEL Introductory Manual 2026** — Vincente D'Ingianni

---

## 7.0 PROTEL 2026 Development Tools

The PROTEL 2026 toolchain ships with a small set of command-line and editor tools intended for macOS and UNIX/Linux hosts with minimal dependencies.

| Tool | Section | Summary |
|------|---------|---------|
| **`Pc`** | §7.1 | **PROTEL compiler** — parser, transpiler, and GCC/clang++ driver |
| **`Pc!`** | §7.0.5 | **Shebang runner** — pronounced *"P c Bang"*; runs `.P` files from `#!` lines or the shell |
| **`Pb`** | §7.0.1 | Source beautifier (keyword uppercasing) |
| **`protel-mode`** | §7.2 | GNU Emacs major mode for `.P`, `.protel`, `.pt`, `.ptl`, and PLS `.AA01`–`.ZZ99` files |

---

## 7.0.0 Source file extensions

**`.P`** is the default suffix for PROTEL 2026 sources (historical Nortel/BNR convention). The **`Pc`** compiler and parser **do not require** any particular extension — you may name a module `myprog.P`, `myprog.protel`, `myprog.pt`, or even `myprog.txt` if you wish.

Recognized suffixes (`.P`, `.protel`, `.pt`, `.ptl`, and PLS `.AA01`–`.ZZ99`) enable Emacs **`protel-mode`** auto-detection and suppress the optional extension warning from **`Pc`**. Unrecognized suffixes still compile when the file contains valid PROTEL source.

---

## 7.0.0.1 System-wide installation

For a host-wide install (macOS or UNIX/Linux), use **`make install-system`**. The default layout is:

| Path | Contents |
|------|----------|
| **`/usr/local/protel/`** | Toolkit root — `Pc`, `Pc!`, `Pb`, `src/`, `examples/`, `emacs/`, `.venv/` |
| **`/usr/local/bin/`** | Symlinks to `Pc`, `Pb`, and `Pc!` in the toolkit root |
| **`/usr/local/share/man/man1/`** | Manual pages `Pc.1` and `Pb.1` |

```bash
sudo make install-system
Pc /usr/local/protel/examples/Hello.P --run
man Pc
```

`/usr/local/bin` is normally already on **`PATH`**, so shebang lines (`#!/usr/bin/env Pc!`) work without extra setup once **`Pc!`** is on the path.

Override locations for packaging or non-default prefixes:

```bash
sudo make install-system SYSPREFIX=/opt/protel SYSBINDIR=/opt/bin
sudo make install-system DESTDIR=/tmp/stage SYSPREFIX=/usr/local/protel
```

Remove a system install:

```bash
sudo make uninstall-system
```

### Local (checkout) installation

From a source tree, **`make install`** prepares the repository for development: marks tools executable, creates a local **`.venv`**, and installs manual pages under **`./man/man1/`** (set **`MANPATH=$PWD/man:$MANPATH`** to read them).

---

## 7.0.1 Pb — PROTEL Beautifier

`Pb` uppercases PROTEL reserved keywords for readable, manual-style source. It is a filter-style tool:

```bash
Pb examples/Hello.P build/Hello.pretty.P
Pb --bold < myprog.P > myprog.pretty.P
```

Install with `make install` (checkout) or `sudo make install-system` (host-wide). See `Pb --help` and `man Pb`.

In Emacs, run Pb on the current buffer with **`C-c C-f`** (`M-x protel-beautify`) — see Introductory Manual §7.2.

---

## 7.0.2 PLS edition modules (`.AA01` … `.ZZ99`)

Historical DMS/PLS modules use edition suffixes such as `vdi.aa01`. The `Pc` compiler **automatically enables classical preprocessing** for these names (keyword normalization, `$LI` / `$EJECT` linker directives stripped before parse).

```bash
Pc vdi.aa01 -c -o build/vdi.aa01.o
make vdi
```

---

## 7.0.3 Type errors and `examples/errors/`

The transpiler performs **strong typing** checks (Reference Manual §11.3). Invalid assignments — such as storing an **integer** into **char** or a **PACK** byte — are rejected before code generation. See `docs/reference-error-messages.md` and `examples/errors/`.

```bash
./Pc examples/errors/err_assign_integer_to_char.P
./Pc examples/errors/ok_assign_char_literal.P -o build/ok_char
```

---

## 7.0.4 UNIX command line and exit status

Standalone programs may read **`argc`** and **`argv`** in the **IS ENTRY** procedure and **RETURN** an integer exit status to the shell. See Introductory Manual §5.5.2 (`docs/intro-5-5-2-entry-args-exit.md`) and `examples/intro_5_5_2_args_exit.P`.

```bash
./Pc examples/intro_5_5_2_args_exit.P -o build/ArgsExit --run -- one two
echo $?
```

---

## 7.0.5 Runnable `.P` files (shebang)

A PROTEL source file may be executed directly from the shell when:

1. **Line 1** is a UNIX shebang (`#!...`) naming **`Pc!`** (or `Pc --run` via `env -S`).
2. The file is **executable** (`chmod +x`).
3. **`Pc!`** (or `Pc`) is on your **`PATH`** — automatic after **`make install-system`** (`/usr/local/bin`); for a checkout, add the project directory to **`PATH`**.

The shebang is **not** PROTEL syntax. The preprocessor removes it before parse; **`Pb`** preserves it unchanged when beautifying.

`examples/Hello.P` demonstrates the usual form:

```protel
#!/usr/bin/env Pc!
% Hello World — run with: ./Hello.P
SECTION Hello;
...
```

**`Pc!`** (pronounced *"P c Bang"*) is a small helper in the project root. The exclamation mark echoes the **`#!`** *shebang* convention and doubles as a memorable command-line shortcut for running PROTEL programs. The kernel runs `Pc! /path/to/script.P [args]`; the helper invokes `Pc script.P --run -- [args]`.

You can also invoke **`Pc!`** directly from the shell (with the project directory on **`PATH`**):

```bash
Pc! examples/Hello.P
Pc! examples/intro_5_5_2_args_exit.P one two
```

### Setup

**System-wide** (after `sudo make install-system`):

```bash
Pc! /usr/local/protel/examples/Hello.P
/usr/local/protel/examples/Hello.P    # if executable
```

**From a source checkout**:

```bash
make install
export PATH="$PWD:$PATH"
./examples/Hello.P
```

From any directory (replace with your checkout path):

```bash
export PATH="$HOME/PROTEL:$PATH"
~/PROTEL/examples/Hello.P
```

`make install` marks `Pc`, `Pc!`, `Pb`, and `examples/Hello.P` executable in the tree. `make install-system` installs the same tools under **`/usr/local/protel`** with symlinks in **`/usr/local/bin`**.

**PATH pitfall:** `export PATH="~/PROTEL:$PATH"` does **not** work — the shell does not expand `~` inside double quotes, so `env` cannot find **`Pc!`**. Use **`$PWD`**, **`$HOME/PROTEL`**, or an absolute path instead.

### ENTRY programs with arguments

Add the same shebang to programs such as `examples/intro_5_5_2_args_exit.P`, then:

```bash
chmod +x examples/intro_5_5_2_args_exit.P
./examples/intro_5_5_2_args_exit.P one two
```

The kernel invokes `Pc --run -- script.P one two`. The driver promotes the script path from after **`--`** to the input positional, then forwards **`one`** and **`two`** to the ENTRY procedure.

### Notes

| Topic | Detail |
|-------|--------|
| `%` comments | Cannot replace the shebang; the kernel only recognizes `#!` at the start of the file |
| **`Pb`** | Copies line 1 unchanged when it begins with `#!` |
| **`protel-mode`** | Displays the shebang line with `protel-comment-face` (§7.2) |
| **Parser** | `strip_shebang()` in `src/preprocess.py` runs before keyword normalization |
| **Output binary** | Default `a.out` in the current working directory (same as `Pc … --run`) |
| `env: Pc!: No such file or directory` | **`PATH` wrong** — avoid quoted `~/PROTEL`; use `export PATH="$PWD:$PATH"` from the repo or `export PATH="$HOME/PROTEL:$PATH"` |

---

## See also

- §11.3 — **Type errors** (`docs/reference-error-messages.md`)
- §5.5.2 — **UNIX argc/argv and shell exit status**
- §7.0.5 — **Runnable `.P` files (shebang)**
- §7.2 — **EMACS PROTEL mode** (`.emacs` setup; automatic `.P`, `.protel`, and PLS suffix detection)
- §7.3 — Foreign language interoperability