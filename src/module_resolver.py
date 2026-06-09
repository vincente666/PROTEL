"""Resolve USES module links and merge embedded PROTEL sections."""

from __future__ import annotations

import sys
from pathlib import Path

from . import ast_nodes as ast
from .extensions import is_protel_source, uses_module_candidates
from .parser import parse_protel
from .transpiler import TranspileError

_ROOT = Path(__file__).resolve().parent.parent
_SECTION_INDEX: dict[str, Path] | None = None


def _search_dirs(source_path: Path | None) -> list[Path]:
    dirs: list[Path] = []
    if source_path is not None:
        dirs.append(source_path.parent.resolve())
    examples = _ROOT / "examples"
    if examples.is_dir():
        dirs.append(examples.resolve())
    return dirs


def _build_section_index(search_dirs: list[Path]) -> dict[str, Path]:
    index: dict[str, Path] = {}
    for base in search_dirs:
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or not is_protel_source(path):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for line in text.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("%"):
                    continue
                upper = stripped.upper()
                if upper.startswith("SECTION ") or upper.startswith("INTERFACE "):
                    parts = stripped.split()
                    if len(parts) >= 2:
                        name = parts[1].rstrip(";")
                        index.setdefault(name, path.resolve())
                    break
    return index


def _find_module_path(
    module_name: str,
    *,
    source_path: Path | None,
    index: dict[str, Path],
) -> Path | None:
    if module_name in index:
        return index[module_name]
    for base in _search_dirs(source_path):
        for candidate in uses_module_candidates(module_name):
            path = base / candidate
            if path.is_file():
                return path.resolve()
    return None


def _load_named_section(
    path: Path,
    module_name: str,
    *,
    classical: bool,
) -> ast.Section:
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise TranspileError(
            f"cannot read USES module {module_name!r} from '{path}': {exc}"
        ) from exc
    try:
        sections = parse_protel(source, classical=classical)
    except Exception as exc:
        raise TranspileError(
            f"parse error in USES module {module_name!r} ({path.name}): {exc}"
        ) from exc
    for section in sections:
        if section.name == module_name:
            return section
    names = ", ".join(section.name for section in sections) or "(none)"
    raise TranspileError(
        f"USES module {module_name!r} not found in '{path.name}' "
        f"(sections: {names})"
    )


def _collect_uses_modules(sections: list[ast.Section]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for section in sections:
        for module_name in section.uses_modules:
            if module_name not in seen:
                seen.add(module_name)
                ordered.append(module_name)
    return ordered


def resolve_compilation_unit(
    sections: list[ast.Section],
    *,
    source_path: Path | None = None,
    classical: bool = False,
) -> list[ast.Section]:
    """Expand USES links by loading embedded sections from other PROTEL sources."""
    uses = _collect_uses_modules(sections)
    if not uses:
        return sections

    search_dirs = _search_dirs(source_path)
    index = _build_section_index(search_dirs)

    merged: list[ast.Section] = []
    merged_names: set[str] = set()
    visiting: set[str] = set()

    def embed(module_name: str) -> None:
        if module_name in merged_names:
            return
        if module_name in visiting:
            raise TranspileError(
                f"circular USES imbedding involving module {module_name!r}"
            )
        visiting.add(module_name)
        path = _find_module_path(module_name, source_path=source_path, index=index)
        if path is None:
            print(
                f"Pc: warning: USES module {module_name!r} not found; "
                f"skipping embed",
                file=sys.stderr,
            )
            visiting.remove(module_name)
            return
        section = _load_named_section(path, module_name, classical=classical)
        for dep in section.uses_modules:
            embed(dep)
        if module_name not in merged_names:
            merged.append(section)
            merged_names.add(module_name)
        visiting.remove(module_name)

    for module_name in uses:
        embed(module_name)

    for section in sections:
        if section.name not in merged_names:
            merged.append(section)
            merged_names.add(section.name)

    return merged