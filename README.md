# PROTEL 2026

**Procedure Oriented Type Enforcing Language** — a modern reincarnation of the language developed at Nortel/BNR for telecom switching systems, now with a GCC/clang++ toolchain for MacOS and UNIX/Linux.

Author: **Vincente D'Ingianni** — [PROTEL Introductory Manual 2026](PROTEL%20Introductory%20Manual%202026.pdf) and [PROTEL Reference Manual 2026](PROTEL%20Reference%20Manual%202026.pdf)

---

## About PROTEL

> Modern programming languages in the 21st century have lost their way with overuse of classes and inheritance, inefficient code, and ridiculous overhead requirements… Strong typing aspects allow errors to be caught at compile time, not run time.
>
> *It's all in the name, Procedure Oriented Type Enforcing Language. This is not retro computing, it is smart computing.*
>
> This project was created to resurrect a fantastic language that was left for dead through bankruptcy and corporate mismanagement… dedicated to the BNR Compiler Team and all of the Nortel developers that produced over 50 million lines of PROTEL code…
>

## History

**PROTEL** (the **PR**ocedure **O**riented **T**ype **E**nforcing **L**anguage) was designed at **BNR** (Bell-Northern Research) in **1975** for programming the **DMS-100** digital switching system and its **SOS** (Switching Operating System) at **Nortel** (Northern Telecom). It is a strongly typed, block-structured Algol/Pascal descendant aimed at reliable, maintainable **real-time telecom software** — contemporaneous with early C, but with compile-time type enforcement, ranged subtypes, descriptors, areas, and modular compilation built in from the start.

The language was described publicly in a landmark **1979 IEEE paper**:

> **David G. Foxall**, **Marc L. Joliat**, **Rym F. Kamel**, and **J. J. Miceli**,  
> [*Protel: a high level language for telephony*](https://ieeexplore.ieee.org/document/762490),  
> **COMPSAC 1979** (IEEE Computer Society International Computer Software & Applications Conference), pp. 193–197.

That paper presented PROTEL as a **telephony systems language** for the DMS program — an Algol/Pascal descendant with left-to-right assignment (`->`, colloquially *gazinta*) and no C-style operator precedence. The authors emphasized strict typing to catch errors during compilation rather than in the field, rich data structuring (numeric subranges, `TABLE`, `SET`, `STRUCT`, pointers, and **descriptors** for bounds-checked array slices), and language features suited to switching software. Their examples included telephony-oriented types such as ranged digit values, digit registers, status conditions, and protocol state — the paper's sample declarations read like call-processing data, not generic systems code.

A striking design choice documented there: for DMS-100, **PROTEL was to be the only implementation language** — no assembly-language escape hatch. The language, **SOS**, the **CALLP** call-processing environment, and the **PLS** (Protel Library System) toolchain formed one integrated platform: compiler, linker, source configuration management, and dynamically loadable modules in a shared address space — with the support software itself written in PROTEL.

A follow-on paper, [*Experience With a Modular Typed Language: Protel*](https://dl.acm.org/doi/10.5555/800078.802525) (Cashin, Joliat, Kamel, and Lasker, **ICSE 1981**), documented modular interfaces, edition/version control, and the practical benefits of catching inter-module errors at compile time. **PROTEL-2** later added object-oriented extensions used in field features such as Carrier AIN.

Over decades, Nortel teams produced **tens of millions of lines** of PROTEL for production switches worldwide. **PROTEL 2026** continues that lineage with a new open toolchain (`Pc`, `Pb`), GCC/clang++ code generation, and manuals that preserve the spirit of the original **OFLPI** / **OFLPR** documentation.

**PROTEL 2026** updates include:

- **Case-sensitive identifiers** by default
- **`--classical`** mode for legacy Nortel DMS case-insensitivity
- **GCC/clang++ backend** — transpile to C++, compile to native code
- **C/C++, Rust, Swift, Python, and Java interoperability** via EXTERNAL and EXPORT
- **Strong typing** at compile time (Reference Manual §11.3)
- **Object-oriented extensions** (classes, methods)
- **Legacy PLS support** — `.AA01` … `.ZZ99` edition suffixes with classical preprocessing

---

## Toolchain

| Tool | Role |
|------|------|
| **`Pc`** | PROTEL compiler — parse, type-check, transpile, and drive GCC/clang++ |
| **`Pb`** | Beautifier — uppercase reserved keywords |
| **`Pc!`** | Shebang runner (*"P c Bang"*) — run `.P` files from `#!` lines or the shell |
| **`protel-mode`** | GNU Emacs major mode for `.P` and related suffixes |

Source files conventionally use the **`.P`** suffix (historical Nortel/BNR). The compiler does not require any particular extension.

---

## Requirements

- **Python 3** (parser bootstrap and virtual environment)
- **GCC, clang++, or g++** with C++20 support (compilation)
- **make** (build and install)
- Optional: **GNU Emacs**, **Swift**, **Rust**, **Python**, **Java** (interop examples)

---

## Installation

### System-wide (recommended for end users)

Installs to **`/usr/local/protel`**, symlinks commands into **`/usr/local/bin`**, and manual pages into **`/usr/local/share/man/man1/`**:

```bash
git clone http://github.com/vincente666/PROTEL.git
cd PROTEL
sudo make install-system
```

Then:

```bash
Pc /usr/local/protel/examples/Hello.P --run
man Pc
man Pb
```

Override paths when needed:

```bash
sudo make install-system SYSPREFIX=/opt/protel SYSBINDIR=/opt/bin
```

Remove a system install:

```bash
sudo make uninstall-system
```

### Local development (from a checkout)

```bash
git clone http://gitea.binary-systems.com/vincente/PROTEL.git
cd PROTEL
make install
export PATH="$PWD:$PATH"
export MANPATH="$PWD/man:$MANPATH"   # optional: read man Pc / man Pb
```

`make install` creates a project **`.venv`**, marks tools executable, and installs manual pages under `./man/man1/`.

### Run the test suite

```bash
make test
```

---

## Using `Pc`

**`Pc`** parses PROTEL source, performs strong type checking, transpiles to C++ (or C with `--emit-c`), and optionally compiles and links with GCC/clang++.

### Quick start

```bash
# Transpile to stdout
Pc examples/Hello.P

# Compile and run
Pc examples/Hello.P --run

# Named executable
Pc examples/Hello.P -o build/Hello --run

# ENTRY program with command-line arguments
Pc examples/intro_5_5_2_args_exit.P -o build/ArgsExit --run -- one two

# Legacy PLS module → object file
Pc vdi.aa01 -c -o build/vdi.aa01.o

# Classical (legacy Nortel) identifier rules
Pc mymodule.P --classical --run
```

### Runnable scripts (`Pc!`)

Add a shebang to an executable `.P` file:

```protel
#!/usr/bin/env Pc!
SECTION Hello;
...
```

```bash
chmod +x myprog.P
export PATH="/usr/local/bin:$PATH"    # after install-system
./myprog.P
# or
Pc! myprog.P
```

### Common options

| Option | Description |
|--------|-------------|
| `-o`, `--output` *file* | Output file (source, object, or executable) |
| `--classical` | Legacy identifier rules (auto for `.AA01`–`.ZZ99`) |
| `--parse-only` | Parse and print AST summary |
| `--emit-c` | Emit C instead of C++ (transpile only) |
| `--compile` | Transpile and compile |
| `--run` | Compile and run (implies `--compile`) |
| `-c` | Compile to object file only |
| `-g` | Generate debug info (passed to GCC) |
| `--keep` | Retain generated `.cpp` after compile |
| `--version` | Print version |
| `--` *args* | Arguments forwarded to ENTRY `argc`/`argv` with `--run` |

Full details: **`man Pc`** or **`Pc --help`**.

---

## Using `Pb`

**`Pb`** is a lexical beautifier. It uppercases PROTEL reserved keywords (per the Reference Manual appendix) and optionally wraps them in ANSI bold for terminal display. Comments (`% …`), strings, and non-keyword text are preserved. A first-line `#!` shebang is copied unchanged.

### Examples

```bash
# File → file
Pb examples/Hello.P build/Hello.pretty.P

# Stdin → stdout
Pb --bold < myprog.P > myprog.pretty.P

# Pipe
cat myprog.P | Pb | less
```

| Option | Description |
|--------|-------------|
| `-b`, `--bold` | Wrap keywords in ANSI bold |
| `--version` | Print version |
| *input* | Input file (default: stdin) |
| *output* | Output file (default: stdout) |

In Emacs: **`C-c C-f`** (`M-x protel-beautify`) — see `docs/intro-7-2-emacs-protel-mode.md`.

Full details: **`man Pb`** or **`Pb --help`**.

---

## Documentation

| Resource | Description |
|----------|-------------|
| [PROTEL Introductory Manual 2026.pdf](PROTEL%20Introductory%20Manual%202026.pdf) | Tutorial and language introduction |
| [PROTEL Reference Manual 2026.pdf](PROTEL%20Reference%20Manual%202026.pdf) | Full language reference |
| [`docs/`](docs/) | Markdown editions of manual sections |
| [`examples/`](examples/) | Introductory, reference, error, and interop samples |
| [`man/Pc.1`](man/Pc.1), [`man/Pb.1`](man/Pb.1) | Manual pages (installed by `make install` / `make install-system`) |
| [`AGENTS.md`](AGENTS.md) | Contributor and architecture notes |

---

## Project layout

```
.
├── Pc, Pc!, Pb          # Compiler, shebang runner, beautifier
├── src/                 # Parser, transpiler, type checker, runtime
├── examples/            # Sample .P sources
├── emacs/protel-mode.el # GNU Emacs mode
├── docs/                # Manual sections (Markdown)
├── man/                 # Pc.1, Pb.1
├── tests/               # pytest suite
└── Makefile
```

---

## Heritage

PROTEL powered Nortel **DMS** switching software from the 1970s onward. The 1979 IEEE COMPSAC paper and the later ICSE experience report remain the best published introductions to the original language design. **PROTEL 2026** preserves historical semantics where practical, adds modern OO extensions cleanly, and targets telecom-grade reliability, education, and new embedded/telecom applications with minimal toolchain dependencies.

---

*Vincente D'Ingianni — PROTEL 2026 revival project*
