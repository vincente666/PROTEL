"""PROTEL source file extension recognition (2026 + legacy PLS naming)."""

from __future__ import annotations

import re
from pathlib import Path

# Default distribution suffix (historical Nortel/BNR). The compiler does not
# require any particular extension; these are conventions for tooling and Emacs.
DEFAULT_SUFFIX = ".P"

# Recognized suffixes (case-insensitive except where noted).
_FIXED_SUFFIXES = frozenset({".p", ".protel", ".pt", ".ptl"})

# PLS edition suffix: .AA01 .. .ZZ99 (two letters + two digits).
_PLS_SUFFIX_RE = re.compile(r"\.[A-Za-z]{2}\d{2}$")

PLS_SUFFIX_DESCRIPTION = ".AA01 through .ZZ99 (two letters + two digits)"

# USES module lookup order when the section index has no entry.
_USES_SUFFIXES = (DEFAULT_SUFFIX, ".protel", ".pt", ".ptl")


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
    """Human-readable suffix list for CLI messages (.P listed first as default)."""
    others = sorted(s for s in _FIXED_SUFFIXES if s.lower() != DEFAULT_SUFFIX.lower())
    fixed = f"{DEFAULT_SUFFIX} (default), " + ", ".join(others)
    return f"{fixed}, {PLS_SUFFIX_DESCRIPTION}"


def uses_module_candidates(module_name: str) -> list[Path]:
    """Candidate filenames for USES module resolution (stem only; caller adds directory)."""
    return [Path(f"{module_name}{suffix}") for suffix in _USES_SUFFIXES]