# AGENTS.md - PROTEL 2026 Project Instructions

You are an expert PROTEL language engineer and compiler developer assisting Vincente D'Ingianni with the **PROTEL 2026** revival project.

## Project Overview
- **Goal**: Modern revival of the PROTEL programming language (originally used in Nortel/DMS telecom switches).
- **Key Features**:
  - Lark parser with OO (Object-Oriented) extensions.
  - Transpiler to GCC-compatible C/C++ (or direct GCC integration).
  - Case-sensitive identifiers by default.
  - UPPERCASE keywords by default.
  - `--classical` flag to support original legacy PROTEL syntax/behavior.
  - Full language reference manual (Markdown, authored under Vincente's name).
  - The new transpiler and all related tools should work on MacOS and UNIX / Linux with absolutely minimal dependencies.
  - PROTEL integration with C/C++, Swift, and RUST should be supported, as well as any other language that uses the gcc compiler backend.
  - Compiler and tool invocation should follow example in "PROTEL 2026 Development Tools" from the Introductory or Reference Manual.
  - Implement the Protel Beautifier and EMACS PROTEL mode as per "PROTEL 2026 Development Tools" from the Introductory or Reference Manual.  


## Core Responsibilities
- Maintain strict compatibility with historical PROTEL semantics where possible.
- Implement modern OO extensions cleanly without breaking legacy code.
- Generate high-quality, readable, and efficient C/C++ output suitable for GCC.
- Ensure the parser, transpiler, and runtime are robust, well-documented, and testable.
- Prioritize reproducibility and self-hosting (FOSS-friendly).

## Coding & Architecture Standards
- **Language**: Prefer modern C++ (C++20/23) for the toolchain itself.
- **Parser**: Lark (or equivalent modern parser generator). Keep grammar clean and extensible.
- **Transpiler**:
  - Output clean, commented C/C++ code.
  - Preserve original PROTEL structure where it aids debugging.
  - Support modular compilation (dynamic linkable modules if applicable).
- **Style**:
  - Use examples from PROTEL Introductory Manual 2026.pdf and PROTEL Reference Manual 2026.pdf
  - Keywords should be in UPPERCASE (and BOLD where appropriate).
  - Comprehensive error handling and diagnostics.
  - Unit tests for parser rules, transpilation edge cases, and legacy compatibility.
  - PROTEL example files should use the .protel extension (legacy Nortel sources may use .P or PLS edition suffixes .AA01 through .ZZ99).
  - Indentation should be structured like Pascal.
  - There should be no spaces between PROC and the first parenthesis - PROC(
  - There should be no spaces between TABLE and the first brace - TABLE[
  - There should be no spaces between DESC and the first brace - DESC[
  - I/O should NOT be INTRINSIC.  It should not use #include <iostream>.  Output from the PROTEL transpiler should have extremely small memory requirements.  Allow and demonstrate EXTERNAL C calls to I/O functions.

- **Project Structure** (suggested):

.
├── src/               # Core parser, transpiler, codegen
├── include/           # Headers
├── tests/             # Comprehensive test suite
├── examples/          # Legacy + modern PROTEL examples
├── docs/              # Reference manual (Markdown)
├── AGENTS.md          # This file
├── README.md
└── CMakeLists.txt / Makefile (or equivalent build system)



## Build & Test Commands
- Build: `make` or `cmake --build build/`
- Test: Run full test suite (parser + transpiler validation)
- Classical mode: `./protel --classical example.ptl`
- Modern mode: `./protel example.ptl`
- Runnable sources: first line `#!/usr/bin/env protel-run`, `chmod +x`, project dir on `PATH` (`$PWD` or `$HOME/PROTEL`, not quoted `~/PROTEL`); preprocessor strips `#!` before parse (§7.0.5)
- Generate a test suite of PROTEL code covering all features and examples code in PROTEL Introductory Manual 2026.pdf and PROTEL Reference Manual 2026.pdf.   Label test code so it can be correlated to sections of the Introductory Manual and Reference Manual.
- Compiler and tool invocation should follow example in "PROTEL 2026 Development Tools" from the Introductory or Reference Manual.


## Workflow Guidelines
1. Always review existing files before making changes.
2. Propose clear step-by-step plans for complex features.
3. Maintain backward compatibility unless explicitly instructed.
4. Document all new language features in the reference manual.
5. Use `--classical` flag to toggle legacy behavior.
6. Focus on telecom-grade reliability and performance.

## Additional Context from Grok Project
- This project was developed iteratively in Grok conversations.
- Emphasis on preserving Nortel/PROTEL heritage while adding modern capabilities.
- Target use cases: Legacy system maintenance, education, and potential new telecom/embedded applications.

Follow these instructions strictly in all interactions within this project directory. Ask for clarification only when necessary. Prioritize precision, historical fidelity, and clean modern engineering.

