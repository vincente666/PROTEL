"""Static type checking for PROTEL 2026 (Reference Manual §11, strong typing)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import ast_nodes as ast
from .transpiler import TranspileError, TypeContext


class TypeCheckError(TranspileError):
    """Raised when a PROTEL construct violates type-compatibility rules."""


@dataclass(frozen=True)
class TypeInfo:
    kind: str
    name: str | None = None
    low: int | None = None
    high: int | None = None
    packed_bits: int | None = None
    pointee: TypeInfo | None = None

    def label(self) -> str:
        if self.name:
            return self.name
        if self.kind == "bool":
            return "BOOL"
        if self.kind == "numeric" and self.low is not None and self.high is not None:
            suffix = f" PACK({self.packed_bits})" if self.packed_bits else ""
            return f"{{{self.low} TO {self.high}}}{suffix}"
        if self.kind == "ptr" and self.pointee is not None:
            return f"PTR TO {self.pointee.label()}"
        return self.kind


class TypeChecker:
    def __init__(self, *, source_name: str = "input.protel"):
        self.source_name = source_name
        self.types = TypeContext()
        self._scopes: list[dict[str, TypeInfo]] = [{}]
        self._return_type: TypeInfo | None = None
        self._proc_name: str | None = None

    def check(self, compilation_unit: list[ast.Section]) -> None:
        for section in compilation_unit:
            self._check_section(section)

    def _fail(self, message: str) -> None:
        raise TypeCheckError(f"{message} ({self.source_name})")

    def _literal_int(self, value: Any) -> int | None:
        if isinstance(value, ast.Literal) and value.kind == "int":
            return int(value.value)
        return None

    def _resolve_spec(self, spec: Any) -> Any:
        from lark import Tree

        while isinstance(spec, Tree):
            spec = spec.children[0] if spec.children else spec
        return self.types.resolve(spec)

    def _type_info(self, spec: Any) -> TypeInfo:
        spec = self._resolve_spec(spec)
        if isinstance(spec, ast.BoolType):
            return TypeInfo(
                kind="bool",
                name="BOOL",
                packed_bits=getattr(spec, "packed", None),
            )
        if isinstance(spec, ast.RangeType):
            return TypeInfo(
                kind="numeric",
                low=self._literal_int(spec.low),
                high=self._literal_int(spec.high),
                packed_bits=getattr(spec, "packed", None),
            )
        if isinstance(spec, ast.DefinedType):
            alias = self.types.aliases.get(spec.name)
            if alias is not None:
                base = self._type_info(alias)
                return TypeInfo(
                    kind=base.kind,
                    name=spec.name,
                    low=base.low,
                    high=base.high,
                    packed_bits=base.packed_bits,
                    pointee=base.pointee,
                )
            return TypeInfo(kind="defined", name=spec.name)
        if isinstance(spec, ast.PtrType):
            return TypeInfo(
                kind="ptr",
                pointee=self._type_info(spec.target),
            )
        if isinstance(spec, ast.SymbolicRange):
            return TypeInfo(kind="symbolic", name="{" + ", ".join(spec.members) + "}")
        return TypeInfo(kind="unknown")

    def _bounds(self, info: TypeInfo) -> tuple[int, int] | None:
        if info.low is not None and info.high is not None:
            return info.low, info.high
        if info.name and info.name in self.types.aliases:
            return self._bounds(self._type_info(self.types.aliases[info.name]))
        if info.name == "integer":
            return -32768, 32767
        return None

    def _is_char_type(self, info: TypeInfo) -> bool:
        if info.name == "char":
            return True
        bounds = self._bounds(info)
        return bounds == (0, 255)

    def _is_wide_integer(self, info: TypeInfo) -> bool:
        if info.name == "integer":
            return True
        bounds = self._bounds(info)
        if bounds is None:
            return False
        low, high = bounds
        if low == high:
            return False
        return low < 0 or high > 255 or (high - low) > 255

    def _pointee_compatible(self, dest: TypeInfo, src: TypeInfo) -> bool:
        if dest.name and src.name:
            return dest.name == src.name
        if dest.kind == "numeric" and src.kind == "numeric":
            return dest.low == src.low and dest.high == src.high
        return dest.kind == src.kind and dest.label() == src.label()

    def _compatible(self, dest: TypeInfo, src: TypeInfo) -> bool:
        if dest.kind == "unknown" or src.kind == "unknown":
            return True
        if dest.kind == "bool":
            return src.kind == "bool"
        if dest.kind == "ptr" and src.kind == "ptr":
            if src.pointee is not None and src.pointee.kind == "unknown":
                return True
            return (
                dest.pointee is not None
                and src.pointee is not None
                and self._pointee_compatible(dest.pointee, src.pointee)
            )
        if self._is_char_type(dest) and self._is_wide_integer(src):
            return False
        if dest.packed_bits and self._is_wide_integer(src):
            return False
        if dest.name and src.name and dest.name == src.name:
            return True
        if dest.kind == "numeric" and src.kind == "numeric":
            db = self._bounds(dest)
            sb = self._bounds(src)
            if db and sb:
                return db[0] <= sb[0] and sb[1] <= db[1]
        if dest.name and dest.name in self.types.aliases:
            return self._compatible(self._type_info(self.types.aliases[dest.name]), src)
        return False

    def _declare_types(self, decl: ast.TypeDecl) -> None:
        self.types.declare(decl.names, decl.type_spec)

    def _declare_vars(self, names: list[str], type_spec: Any) -> None:
        info = self._type_info(type_spec)
        for name in names:
            self._scopes[-1][name] = info

    def _lookup(self, name: str) -> TypeInfo | None:
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        return None

    def _expr_type(self, expr: Any) -> TypeInfo:
        if isinstance(expr, ast.Literal):
            if expr.kind == "int":
                value = int(expr.value)
                return TypeInfo(kind="numeric", low=value, high=value)
            if expr.kind in {"true", "false"}:
                return TypeInfo(kind="bool", name="BOOL")
            if expr.kind == "NIL".lower():
                return TypeInfo(kind="ptr", pointee=TypeInfo(kind="unknown"))
        if isinstance(expr, ast.VarRef) and not expr.is_self and not expr.is_super:
            return self._lookup(expr.name) or TypeInfo(kind="unknown")
        if isinstance(expr, ast.BinExpr) and expr.op in {"+", "-", "*", "/", "MOD"}:
            left = self._expr_type(expr.left)
            right = self._expr_type(expr.right)
            if self._is_wide_integer(left) or self._is_wide_integer(right):
                return TypeInfo(kind="numeric", name="integer", low=-32768, high=32767)
            lb = [t.low for t in (left, right) if t.low is not None]
            hb = [t.high for t in (left, right) if t.high is not None]
            if lb and hb:
                return TypeInfo(kind="numeric", low=min(lb), high=max(hb))
        if isinstance(expr, ast.CastExpr):
            return self._type_info(expr.target_type)
        return TypeInfo(kind="unknown")

    def _check_assignment(self, target: Any, value: Any, *, context: str) -> None:
        if not isinstance(target, ast.VarRef) or target.is_self or target.is_super:
            return
        dest = self._lookup(target.name)
        if dest is None:
            self._fail(f"unknown identifier {target.name!r} in {context}")
        src = self._expr_type(value)
        if dest.packed_bits and self._is_wide_integer(src):
            self._fail(
                f"cannot assign wide integer to packed byte-sized type "
                f"{dest.label()} in {context}"
            )
        if self._is_char_type(dest) and self._is_wide_integer(src):
            self._fail(f"cannot assign integer to char in {context}")
        if (
            dest.kind == "numeric"
            and src.kind == "numeric"
            and src.low is not None
            and src.high is not None
            and src.low == src.high
        ):
            db = self._bounds(dest)
            if db and (src.low < db[0] or src.high > db[1]):
                self._fail(
                    f"value {src.low}..{src.high} is out of range for "
                    f"{dest.label()} in {context}"
                )
        if not self._compatible(dest, src):
            self._fail(
                f"cannot assign {src.label()} to {dest.label()} in {context}"
            )

    def _check_return(self, value: Any | None) -> None:
        if self._return_type is None:
            if value is not None:
                self._fail(f"procedure {self._proc_name!r} cannot RETURN a value")
            return
        if value is None:
            self._fail(
                f"procedure {self._proc_name!r} must RETURN {self._return_type.label()}"
            )
        src = self._expr_type(value)
        if not self._compatible(self._return_type, src):
            self._fail(
                f"RETURN type {src.label()} is not compatible with "
                f"RETURNS {self._return_type.label()} in procedure {self._proc_name!r}"
            )

    def _check_block(self, block: ast.Block) -> None:
        self._scopes.append({})
        for decl in block.declarations:
            if isinstance(decl, ast.TypeDecl):
                self._declare_types(decl)
            elif isinstance(decl, ast.VarDecl) and decl.names:
                self._declare_vars(decl.names, decl.type_spec)
                if decl.init is not None:
                    for name in decl.names:
                        self._check_assignment(
                            ast.VarRef(name=name),
                            decl.init,
                            context=f"initialization of {name!r}",
                        )
        for stmt in block.statements:
            self._check_stmt(stmt)
        self._scopes.pop()

    def _check_stmt(self, stmt: Any) -> None:
        if isinstance(stmt, ast.Block):
            self._check_block(stmt)
        elif isinstance(stmt, ast.IfStmt):
            for part in (stmt.then_part, stmt.else_part):
                for inner in part:
                    self._check_stmt(inner)
        elif isinstance(stmt, ast.LoopStmt):
            for inner in stmt.body:
                self._check_stmt(inner)
        elif isinstance(stmt, ast.ForStmt):
            for inner in stmt.body:
                self._check_stmt(inner)
        elif isinstance(stmt, ast.OverStmt):
            for inner in stmt.body:
                self._check_stmt(inner)
        elif isinstance(stmt, ast.CaseStmt):
            for arm in stmt.arms:
                for inner in arm.statements:
                    self._check_stmt(inner)
            for inner in stmt.out_statements:
                self._check_stmt(inner)
        elif isinstance(stmt, ast.ReturnStmt):
            self._check_return(stmt.value)
        elif isinstance(stmt, ast.AssignExpr):
            self._check_assignment(
                stmt.target, stmt.value, context="assignment statement"
            )

    def _check_procedure(self, proc: ast.ProcDecl) -> None:
        if proc.body is None:
            return
        self._scopes.append({})
        self._proc_name = proc.name
        self._return_type = (
            self._type_info(proc.return_type) if proc.return_type else None
        )
        for names, type_spec, _mode in proc.parms:
            self._declare_vars(names, type_spec)
        self._check_block(proc.body)
        self._return_type = None
        self._proc_name = None
        self._scopes.pop()

    def _check_section(self, section: ast.Section) -> None:
        self._scopes.append({})
        for decl in section.declarations:
            if isinstance(decl, ast.TypeDecl):
                self._declare_types(decl)
            elif isinstance(decl, ast.VarDecl) and decl.names:
                self._declare_vars(decl.names, decl.type_spec)
                if decl.init is not None:
                    for name in decl.names:
                        self._check_assignment(
                            ast.VarRef(name=name),
                            decl.init,
                            context=f"initialization of {name!r}",
                        )
            elif isinstance(decl, ast.ProcDecl) and decl.body is not None:
                if not (
                    decl.external or decl.export or decl.forward or decl.intrinsic
                ):
                    self._check_procedure(decl)
        self._scopes.pop()


def check_types(
    compilation_unit: list[ast.Section],
    *,
    source_name: str = "input.protel",
) -> None:
    TypeChecker(source_name=source_name).check(compilation_unit)