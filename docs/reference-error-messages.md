# PROTEL 2026 Error Messages

**PROTEL Reference Manual 2026** — Vincente D'Ingianni

---

## Overview

The **`Pc`** driver reports errors in three phases: **parse**, **type check**, and **compile**. Error examples live under `examples/errors/`.

```bash
./Pc examples/errors/err_assign_integer_to_char.P
```

---

## 1. Parse errors

**Prefix:** `Pc: parse error in '<file>':`

The Lark parser rejects invalid syntax before transpilation.

| Message pattern | Typical cause |
|-----------------|---------------|
| `Unexpected token` | Misspelled keyword, missing `;`, `ENDIF`, or `ENDBLOCK` |
| `Unexpected input` | Tokens where a declaration or statement is required |
| `No terminal matches` | Unterminated string or malformed tuple |

**Example**

```protel
DCL demo PROC() IS
   BLOCK
      IF x > 0 THEN
         x + 1 -> x;
      % missing ENDIF
   ENDBLOCK;
```

---

## 2. Type errors (strong typing)

**Prefix:** `Pc: type error in '<file>':`

PROTEL 2026 enforces Reference Manual §11.3 compatibility at transpile time. Wide **integer** values cannot be stored in **char**, **PACK** byte fields, or **BOOL** without an explicit **CAST**.

| Message | Meaning | Example file |
|---------|---------|--------------|
| `cannot assign integer to char in …` | A variable or expression typed **integer** is assigned to **char {0 TO 255}** | `examples/errors/err_assign_integer_to_char.P` |
| `cannot assign wide integer to packed byte-sized type {…} PACK(n) in …` | **integer** assigned to a **PACK** subrange | `examples/errors/err_assign_integer_to_packed_byte.P` |
| `cannot assign integer to BOOL in …` | Numeric value assigned to **BOOL** | `examples/errors/err_assign_integer_to_bool.P` |
| `value L..H is out of range for {A TO B} in …` | Numeric literal exceeds destination subrange | `examples/errors/err_constant_out_of_range.P` |
| `cannot assign PTR TO T1 to PTR TO T2 in …` | Pointer pointee types differ | `examples/errors/err_assign_incompatible_pointer.P` |
| `RETURN type T1 is not compatible with RETURNS T2 in procedure 'P'` | **RETURN** expression does not match **RETURNS** type | `examples/errors/err_return_type_mismatch.P` |
| `procedure 'P' cannot RETURN a value` | **RETURN** with value in a `PROC()` without **RETURNS** | — |
| `procedure 'P' must RETURN T` | Missing **RETURN** in a **RETURNS** procedure | — |
| `unknown identifier 'x' in …` | Assignment to an undeclared name | — |

**Valid contrast:** `examples/errors/ok_assign_char_literal.P` assigns literal `65` to **char** (within `{0 TO 255}`).

### Strong typing rules (summary)

1. **integer** does not silently narrow to **char** or **PACK** types.
2. Numeric literals must fit the destination subrange.
3. **BOOL** accepts only boolean expressions.
4. **PTR TO** assignments require compatible pointee types.
5. **RETURN** must match the procedure **RETURNS** type.

---

## 3. Transpile errors

**Prefix:** `Pc: transpile error in '<file>':`

Structural or linkage problems in the transpiler (not type compatibility).

| Message | Cause |
|---------|-------|
| `multiple ENTRY procedures (…)` | More than one **IS ENTRY** per module |
| `ENTRY procedure 'P' has no procedure body` | **IS ENTRY** forward without matching body |
| `ENTRY procedure 'P' parameters must match …` | **IS ENTRY** declaration differs from body |
| `EXPORT procedure 'P' has no procedure body` | **EXPORT** without implementation |
| `duplicate EXPORT declaration for 'P'` | Two **EXPORT** declarations for one name |
| `compile mode requires C++ output (omit --emit-c)` | `--emit-c` with `--compile` |

---

## 4. Driver and I/O errors

| Message | Cause |
|---------|-------|
| `Pc: cannot read '<file>': …` | Missing or unreadable source path |
| `Pc: cannot write '<file>': …` | Output path not writable |
| `Pc: '<file>' is not a PROTEL source file` | Unrecognized extension |
| `Pc: warning: only the first source file is compiled` | Multiple inputs on command line |

---

## 5. Compile and link errors

**Prefix:** `Pc: compile error:`

Emitted when GCC/clang++ rejects generated C++. Often caused by invalid generated code or missing runtime symbols.

| Underlying message | Typical fix |
|--------------------|-------------|
| `undefined reference to 'writeln'` | Link without `protel_io.c` (use default `Pc` compile, not raw `g++` on `.cpp` alone) |
| `functions that differ only in their return type` | Duplicate ENTRY/forward signatures (report as transpile bug) |
| `no C++ compiler found` | Install `g++`, `clang++`, or `c++` on `PATH` |

---

## 6. Runtime warnings

| Message | Cause |
|---------|-------|
| `Pc: warning: call to P uses a PROTEL string without an explicit NUL (0) suffix` | **EXTERNAL** call with string missing `, 0` in char tuple |

---

## See also

- Reference Manual §11.0–§11.3 — type compatibility
- `examples/errors/` — intentional error and OK contrast programs
- Introductory Manual §7.0 — **`Pc`** driver usage