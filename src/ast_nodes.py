"""AST node definitions for PROTEL 2026."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Section:
    module_type: str
    section_kind: str
    name: str
    of_modules: list[str] = field(default_factory=list)
    uses_modules: list[str] = field(default_factory=list)
    declarations: list[Any] = field(default_factory=list)
    statements: list[Any] = field(default_factory=list)
    class_impls: list[Any] = field(default_factory=list)


@dataclass
class TypeDecl:
    names: list[str]
    type_spec: Any


@dataclass
class VarDecl:
    names: list[str]
    type_spec: Any
    init: Any | None = None
    storage_class: str | None = None
    ovly_fields: list[tuple[Any, list[str], Any]] | None = None


@dataclass
class ProcDecl:
    name: str
    parms: list[tuple[list[str], Any, Any]]
    return_type: Any | None
    body: Any | None
    pclass: str | None = None
    intrinsic: bool = False
    forward: bool = False
    external: bool = False
    entry: bool = False
    export: bool = False


@dataclass
class ClassDataPart:
    access_attrs: list[str]
    fields: list[tuple[list[str], Any]]


@dataclass
class MethodDecl:
    names: list[str]
    parms: list[tuple[list[str], Any, bool]]
    return_type: Any | None
    attrs: list[str] = field(default_factory=list)


@dataclass
class MethodSection:
    attrs: list[str]
    methods: list[MethodDecl]


@dataclass
class ClassType:
    end_name: str
    base: Any | None
    data_parts: list[ClassDataPart]
    operations: list[MethodSection]


@dataclass
class MethodImplDecl:
    name: str
    body: Any


@dataclass
class ClassImplSection:
    class_name: str
    declarations: list[Any]
    statements: list[Any] = field(default_factory=list)


@dataclass
class Block:
    declarations: list[Any]
    statements: list[Any]


@dataclass
class IfStmt:
    condition: Any
    then_part: list[Any]
    else_part: list[Any] = field(default_factory=list)


@dataclass
class LoopStmt:
    while_expr: Any | None
    body: list[Any]


@dataclass
class ForStmt:
    var: str
    from_expr: Any | None
    to_expr: Any | None
    direction: str | None
    by_expr: Any | None
    while_expr: Any | None
    over_type: Any | None
    body: list[Any]


@dataclass
class OverStmt:
    over_type: Any
    body: list[Any]


@dataclass
class CaseArm:
    labels: Any
    statements: list[Any]


@dataclass
class CaseStmt:
    selector: Any
    arms: list[CaseArm]
    out_statements: list[Any]
    is_select: bool = False


@dataclass
class ExitStmt:
    pass


@dataclass
class BindStmt:
    bindings: list[tuple[str, Any, Any | None]]


@dataclass
class WithStmt:
    refs: list[Any]


@dataclass
class CastExpr:
    operand: Any
    target_type: Any


@dataclass
class AreaType:
    options: list[str]
    size_expr: Any
    fields: list[tuple[list[str], Any]]


@dataclass
class ReturnStmt:
    value: Any | None = None


@dataclass
class AssignExpr:
    value: Any
    target: Any


@dataclass
class BinExpr:
    op: str
    left: Any
    right: Any


@dataclass
class UnaryExpr:
    op: str
    operand: Any


@dataclass
class BuiltinExpr:
    name: str
    operand: Any


@dataclass
class VarRef:
    name: str
    indices: list[Any] = field(default_factory=list)
    is_self: bool = False
    is_super: bool = False


@dataclass
class MemberRef:
    base: Any
    member: str


@dataclass
class MethodCall:
    receiver: Any | None
    name: str
    args: list[Any] = field(default_factory=list)


@dataclass
class ProcCall:
    name: str
    args: list[Any] = field(default_factory=list)


@dataclass
class Literal:
    kind: str
    value: Any


@dataclass
class TupleLit:
    elements: list[Any]


@dataclass
class RangeType:
    low: Any
    high: Any
    packed: int | None = None


@dataclass
class SymbolicRange:
    members: list[str]


@dataclass
class DefinedType:
    name: str


@dataclass
class BoolType:
    packed: int | None = None


@dataclass
class PtrType:
    target: Any


@dataclass
class SetType:
    member_type: Any


@dataclass
class StructType:
    fields: list[tuple[list[str], Any]]


@dataclass
class TableType:
    low: Any
    high: Any
    element_type: Any
    packed: int | None = None


@dataclass
class DescType:
    low: Any | None
    high: Any | None
    element_type: Any


@dataclass
class ProcTypeSig:
    parms: list[tuple[list[str], Any, Any]]
    return_type: Any | None
    pclass: str | None = None