"""Lexical preprocessing for PROTEL source before parsing."""

from __future__ import annotations

import re

from .keywords import PROTEL_KEYWORDS

_DOLLAR_DIRECTIVES = frozenset(k for k in PROTEL_KEYWORDS if k.startswith("$"))

KEYWORD_RE = re.compile(
    r"\b(" + "|".join(sorted(PROTEL_KEYWORDS, key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
)

TOKEN_SPEC = [
    ("STRING", r"'(?:''|[^'])*'"),
    ("IDENT", r"[A-Za-z_$][A-Za-z0-9_$]*"),
    ("NUMBER", r"\d+(?:\.\d+)?(?:[eE][+-]?\d+)?"),
    ("OP_SYM", r"->|::=|[<>=!&|/*%+-]+|[\(\)\[\]\{\},;:\.\^]"),
    ("WHITESPACE", r"[ \t\r\n]+"),
    ("OTHER", r"."),
]

TOKEN_RE = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC),
    re.DOTALL,
)


def _find_comment_start(line: str) -> int:
    in_string = False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "'":
            in_string = not in_string
            if in_string and i + 1 < len(line) and line[i + 1] == "'":
                i += 1
        elif ch == "%" and not in_string:
            return i
        i += 1
    return -1


def _is_dollar_directive_line(code_part: str) -> bool:
    """True for linker control lines such as ``$li modentry restart``."""
    for match in TOKEN_RE.finditer(code_part):
        kind = match.lastgroup
        if kind == "WHITESPACE":
            continue
        if kind == "IDENT":
            return match.group().upper() in _DOLLAR_DIRECTIVES
        return False
    return False


def strip_shebang(source: str) -> str:
    """
    Remove a UNIX shebang (``#!...``) from the first line when present.

    The shebang is host metadata for direct execution; it is not PROTEL syntax.
    """
    if source.startswith("#!"):
        _, _, rest = source.partition("\n")
        return rest
    return source


def normalize_keywords(source: str, *, classical: bool = False) -> str:
    """
    Uppercase reserved keywords outside comments and strings.

    In modern mode, keywords are normalized to UPPERCASE before parsing.
    In classical mode, the same normalization applies but identifiers remain
    case-sensitive when not matching reserved words.
    """
    del classical  # reserved for future classical-only identifier rules
    source = strip_shebang(source)
    output_parts: list[str] = []

    for line in source.splitlines(keepends=True):
        comment_pos = _find_comment_start(line)
        if comment_pos != -1:
            code_part = line[:comment_pos]
            # Drop comments before parse; the transpiler re-emits source file name.
        else:
            code_part = line

        if _is_dollar_directive_line(code_part):
            continue

        line_out: list[str] = []
        for match in TOKEN_RE.finditer(code_part):
            kind = match.lastgroup
            token = match.group()
            if kind == "STRING":
                line_out.append(token)
            elif kind == "IDENT":
                upper = token.upper()
                line_out.append(upper if upper in PROTEL_KEYWORDS else token)
            else:
                line_out.append(token)

        normalized = "".join(line_out)
        if normalized.strip():
            if not normalized.endswith("\n"):
                normalized += "\n"
            output_parts.append(normalized)

    return "".join(output_parts)