"""PROTEL source file extension recognition (2026 + legacy PLS naming)."""

from __future__ import annotations

import re
from pathlib import Path

# Modern / distribution suffixes (case-insensitive except where noted).
_FIXED_SUFFIXES = frozenset({".protel", ".pt", ".ptl", ".p"})

# PLS edition suffix: .AA01 .. .ZZ99 (two letters + two digits).
_PLS_SUFFIX_RE = re.compile(r"\.[A-Za-z]{2}\d{2}$")

PLS_SUFFIX_DESCRIPTION = ".AA01 through .ZZ99 (two letters + two digits)"


def is_pls_suffix(suffix: str) -> bool:
    """True when suffix matches legacy PLS edition form (e.g. .AA01, .aa01)."""
    return bool(_PLS_SUFFIX_RE.match(suffix))


def is_protel_suffix(suffix: str) -> bool:
    """True when suffix is a recognized PROTEL source extension."""
    if suffix.lower() in _FIXED_SUFFIXES:
        return True
    return is_pls_suffix(suffix)


def is_protel_source(path: str | Path) -> bool:
    """True when path name uses a recognized PROTEL source extension."""
    return is_protel_suffix(Path(path).suffix)


def format_suffix_list() -> str:
    """Human-readable suffix list for CLI messages."""
    fixed = ", ".join(sorted(_FIXED_SUFFIXES))
    return f"{fixed}, {PLS_SUFFIX_DESCRIPTION}"