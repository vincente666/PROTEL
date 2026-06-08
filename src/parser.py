"""PROTEL 2026 Lark parser and AST builder."""

from __future__ import annotations

from pathlib import Path

from lark import Lark, Transformer, Tree

from . import ast_nodes as ast
from .preprocess import normalize_keywords

_GRAMMAR_PATH = Path(__file__).parent / "grammar" / "protel.lark"


def _token_values(children) -> list:
    out = []
    for child in children:
        if isinstance(child, str):
            out.append(child)
        elif hasattr(child, "type") and child.type not in {"RULE"}:
            out.append(str(child))
        elif isinstance(child, list):
            out.extend(_token_values(child))
        elif isinstance(child, Tree):
            out.extend(_token_values(child.children))
    return out


def _only_nodes(children):
    return [c for c in children if not isinstance(c, str) and not hasattr(c, "type")]


class ProtelASTBuilder(Transformer):
    def compilation_unit(self, children):
        sections: list[ast.Section] = []
        current: ast.Section | None = None
        for item in children:
            if isinstance(item, dict) and "section_kind" in item:
                current = ast.Section(
                    module_type=item["module_type"],
                    section_kind=item["section_kind"],
                    name=item["name"],
                    of_modules=item.get("of_modules", []),
                    uses_modules=item.get("uses_modules", []),
                )
                sections.append(current)
            elif current is None:
                raise ValueError("PROTEL declaration or statement appears before SECTION/INTERFACE header")
            elif isinstance(item, ast.ClassImplSection):
                current.class_impls.append(item)
            elif isinstance(item, (ast.TypeDecl, ast.VarDecl, ast.ProcDecl)):
                current.declarations.append(item)
            else:
                current.statements.append(item)
        return sections

    def unit_item(self, children):
        return children[0]

    def interface_kind(self, _children=None):
        return "INTERFACE"

    def section_kind_kw(self, _children=None):
        return "SECTION"

    def module_type(self, children):
        return str(children[0]) if children else "FAST"

    def _section_head_meta(
        self,
        children,
        *,
        of_modules: list[str] | None = None,
        uses_modules: list[str] | None = None,
    ) -> dict:
        module_type = "FAST"
        section_kind = "SECTION"
        name = ""
        for child in children:
            if isinstance(child, list):
                continue
            text = str(child)
            if text in {"FAST", "SWAPPABLE", "PERPROCESS", "DEFINITIONS"}:
                module_type = text
            elif text in {"INTERFACE", "SECTION"}:
                section_kind = text
            elif not name:
                name = text
        return {
            "module_type": module_type,
            "section_kind": section_kind,
            "name": name,
            "of_modules": of_modules or [],
            "uses_modules": uses_modules or [],
        }

    def section_plain(self, children):
        return self._section_head_meta(children)

    def section_uses(self, children):
        id_lists = [c for c in children if isinstance(c, list)]
        return self._section_head_meta(children, uses_modules=id_lists[0])

    def section_of(self, children):
        id_lists = [c for c in children if isinstance(c, list)]
        return self._section_head_meta(children, of_modules=id_lists[0])

    def section_of_uses(self, children):
        id_lists = [c for c in children if isinstance(c, list)]
        return self._section_head_meta(
            children,
            of_modules=id_lists[0],
            uses_modules=id_lists[1],
        )

    def declaration(self, children):
        return children[0]

    def type_dcl_stmt(self, children):
        return children[-1]

    def type_dcl_list_tail(self, children):
        return children[-1]

    def type_dcl(self, children):
        return ast.TypeDecl(names=list(children[0]), type_spec=children[1])

    def variable_dcl_stmt(self, children):
        return children[-1]

    def variable_dcl_list_tail(self, children):
        return children[-1]

    def variable_init_init(self, children):
        return ("INIT", children[0])

    def variable_init_is(self, children):
        return ("IS", children[0])

    def _var_decl_from_parts(
        self,
        names,
        type_spec,
        *,
        storage_class: str | None = None,
        init_tail=None,
    ):
        init = None
        if init_tail is not None:
            kind, value = init_tail
            if kind == "INIT":
                init = value
            else:
                init = value
        return ast.VarDecl(
            names=list(names),
            type_spec=type_spec,
            init=init,
            storage_class=storage_class,
        )

    def variable_dcl_literal(self, children):
        init_tail = children[2] if len(children) > 2 else None
        return self._var_decl_from_parts(
            children[0],
            children[1],
            storage_class="LITERAL",
            init_tail=init_tail,
        )

    def variable_dcl_variable(self, children):
        init_tail = children[2] if len(children) > 2 else None
        return self._var_decl_from_parts(
            children[0],
            children[1],
            storage_class="VARIABLE",
            init_tail=init_tail,
        )

    def variable_dcl_ovly(self, children):
        return ast.VarDecl(
            names=[],
            type_spec=children[0],
            ovly_fields=list(children[1]),
        )

    def variable_dcl(self, children):
        if len(children) == 3 and isinstance(children[2], tuple):
            return self._var_decl_from_parts(
                children[0], children[1], init_tail=children[2]
            )
        names = list(children[0])
        type_spec = children[1]
        return ast.VarDecl(names=names, type_spec=type_spec)

    def proc_dcl_stmt(self, children):
        return children[-1]

    def proc_dcl_intrinsic(self, children):
        names = children[0]
        proc_sig = children[1]
        return ast.ProcDecl(
            name=names[0],
            parms=proc_sig["parms"],
            return_type=proc_sig["return_type"],
            body=None,
            pclass=proc_sig.get("pclass"),
            intrinsic=True,
        )

    def proc_dcl_external(self, children):
        names = children[0]
        proc_sig = children[1]
        return ast.ProcDecl(
            name=names[0],
            parms=proc_sig["parms"],
            return_type=proc_sig["return_type"],
            body=None,
            pclass=proc_sig.get("pclass"),
            external=True,
        )

    def proc_dcl_forward(self, children):
        names = children[0]
        proc_sig = children[1]
        return ast.ProcDecl(
            name=names[0],
            parms=proc_sig["parms"],
            return_type=proc_sig["return_type"],
            body=None,
            pclass=proc_sig.get("pclass"),
            forward=True,
        )

    def proc_dcl_entry(self, children):
        names = children[0]
        proc_sig = children[1]
        return ast.ProcDecl(
            name=names[0],
            parms=proc_sig["parms"],
            return_type=None,
            body=None,
            pclass=proc_sig.get("pclass"),
            entry=True,
        )

    def proc_dcl_export(self, children):
        names = children[0]
        proc_sig = children[1]
        return ast.ProcDecl(
            name=names[0],
            parms=proc_sig["parms"],
            return_type=proc_sig["return_type"],
            body=None,
            pclass=proc_sig.get("pclass"),
            export=True,
        )

    def proc_dcl(self, children):
        names = children[0]
        proc_sig = children[1]
        body = children[-1] if len(children) > 2 else None
        if body == proc_sig or isinstance(body, str):
            body = None
        return ast.ProcDecl(
            name=names[0],
            parms=proc_sig["parms"],
            return_type=proc_sig["return_type"],
            body=body,
            pclass=proc_sig.get("pclass"),
            intrinsic=False,
        )

    def proc_sig(self, children):
        return self._build_proc_sig(children)

    def paren_parms(self, children):
        for child in children:
            if isinstance(child, list) and child and isinstance(child[0], tuple):
                return child
            if isinstance(child, list) and (not child or not isinstance(child[0], str)):
                return child
        return []

    def _build_proc_sig(self, children):
        tokens = _token_values(children)
        pclass = None
        if tokens and tokens[0] in {"QUICK", "OPERAND"}:
            pclass = tokens[0]
        parms: list = []
        return_type = None
        for child in children:
            if isinstance(child, list) and child and isinstance(child[0], tuple):
                parms = child
            elif not isinstance(child, (str, list)) and child is not None:
                if not isinstance(child, dict):
                    return_type = child
        return {"pclass": pclass, "parms": parms, "return_type": return_type}

    def parm_list(self, children):
        return list(children)

    def parm_updates(self, children):
        return (list(children[0]), children[1], "UPDATES")

    def parm(self, children):
        if children[0] == "REF":
            return (list(children[1]), children[2], True)
        return (list(children[0]), children[1], False)

    def bind_stmt(self, children):
        return ast.BindStmt(bindings=list(children[0]))

    def bind_list(self, children):
        return list(children)

    def bind_item(self, children):
        name = str(children[0])
        ref = children[1]
        as_type = children[2] if len(children) > 2 else None
        return (name, ref, as_type)

    def opt_as_clause(self, children):
        return children[0] if children else None

    def with_stmt(self, children):
        return ast.WithStmt(refs=list(children[0]))

    def with_ref_list(self, children):
        return list(children)

    def block(self, children):
        innards = children[-1]
        decls, stmts = innards
        return ast.Block(declarations=list(decls), statements=list(stmts))

    def block_innards(self, children):
        decls = []
        stmts = []
        for item in children:
            if isinstance(item, (ast.TypeDecl, ast.VarDecl, ast.ProcDecl)):
                decls.append(item)
            else:
                stmts.append(item)
        return decls, stmts

    def if_stmt(self, children):
        condition = children[0]
        then_part = list(children[1])
        else_part = list(children[2]) if len(children) > 2 else []
        return ast.IfStmt(condition=condition, then_part=then_part, else_part=else_part)

    def statement_list(self, children):
        return list(children)

    def loop_stmt(self, children):
        if len(children) >= 2 and not isinstance(children[0], list):
            return ast.LoopStmt(while_expr=children[0], body=list(children[-1]))
        return ast.LoopStmt(while_expr=None, body=list(children[-1]))

    def for_over_range(self, children):
        return {"over_type": children[0]}

    def for_index_range(self, children):
        parts = children[0]
        return {
            "from_expr": parts[0],
            "direction": parts[1][0] if parts[1] else None,
            "to_expr": parts[1][1] if parts[1] else None,
            "by_expr": parts[2],
            "while_expr": parts[3],
            "over_type": None,
        }

    def from_to_parts(self, children):
        from_expr = None
        to_part = None
        by_expr = None
        while_expr = None
        idx = 0
        if idx < len(children):
            if isinstance(children[idx], tuple) and children[idx][0] in {"UP", "DOWN"}:
                to_part = children[idx]
                idx += 1
            else:
                from_expr = children[idx]
                idx += 1
        if idx < len(children):
            to_part = children[idx]
            idx += 1
        if idx < len(children):
            by_expr = children[idx]
            idx += 1
        if idx < len(children):
            while_expr = children[idx]
        return (from_expr, to_part, by_expr, while_expr)

    def opt_from_clause(self, children):
        return children[0] if children else None

    def up_to_clause(self, children):
        return ("UP", children[0])

    def down_to_clause(self, children):
        return ("DOWN", children[0])

    def opt_by_clause(self, children):
        return children[0] if children else None

    def opt_while_clause(self, children):
        return children[0] if children else None

    def for_stmt(self, children):
        var = str(children[0])
        range_info = children[1]
        body = list(children[-1])
        if range_info.get("over_type") is not None:
            return ast.ForStmt(
                var=var,
                from_expr=None,
                to_expr=None,
                direction=None,
                by_expr=None,
                while_expr=None,
                over_type=range_info["over_type"],
                body=body,
            )
        return ast.ForStmt(
            var=var,
            from_expr=range_info.get("from_expr"),
            to_expr=range_info.get("to_expr"),
            direction=range_info.get("direction"),
            by_expr=range_info.get("by_expr"),
            while_expr=range_info.get("while_expr"),
            over_type=None,
            body=body,
        )

    def over_stmt(self, children):
        return ast.OverStmt(over_type=children[0], body=list(children[-1]))

    def case_list(self, children):
        if len(children) == 1:
            item = children[0]
            return [item] if isinstance(item, ast.CaseArm) else list(item)
        left = children[0]
        right = children[1]
        if not isinstance(left, list):
            left = [left]
        return left + [right]

    def case_body(self, children):
        arms = children[0] if children else []
        if isinstance(arms, ast.CaseArm):
            arms = [arms]
        out_statements: list = []
        if len(children) > 1:
            out_statements = children[1] if isinstance(children[1], list) else []
        return list(arms), out_statements

    def case_item_empty(self, children):
        return ast.CaseArm(labels=children[0], statements=[])

    def case_item_nonempty(self, children):
        return ast.CaseArm(labels=children[0], statements=list(children[1]))

    def case_arm_nonempty(self, children):
        return list(children)

    def out_case_empty(self, children):
        return []

    def out_case_with_stmts(self, children):
        return list(children)

    def case_stmt(self, children):
        arms, out_statements = children[1]
        return ast.CaseStmt(selector=children[0], arms=arms, out_statements=out_statements, is_select=False)

    def select_stmt(self, children):
        arms, out_statements = children[1]
        return ast.CaseStmt(selector=children[0], arms=arms, out_statements=out_statements, is_select=True)

    def exit_stmt(self, children):
        return ast.ExitStmt()

    def upb_expr(self, children):
        return ast.BuiltinExpr(name="UPB", operand=children[0])

    def tdsize_expr(self, children):
        return ast.BuiltinExpr(name="TDSIZE", operand=children[0])

    def typedesc_expr(self, children):
        return ast.BuiltinExpr(name="TYPEDESC", operand=children[0])

    def vardesc_expr(self, children):
        return ast.BuiltinExpr(name="VARDESC", operand=children[0])

    def refdesc_expr(self, children):
        return ast.BuiltinExpr(name="REFDESC", operand=children[0])

    def cast_expr(self, children):
        return ast.CastExpr(operand=children[0], target_type=children[1])

    def bin_incl(self, children):
        return self._bin("INCL", children)

    def bin_notincl(self, children):
        return self._bin("NOTINCL", children)

    def return_stmt(self, children):
        if not children:
            return ast.ReturnStmt(value=None)
        return ast.ReturnStmt(value=children[0])

    def expr_stmt(self, children):
        return children[0]

    def id_list(self, children):
        return [str(c) for c in children]

    def statement(self, children):
        return children[0]

    def unpacked_type(self, children):
        return children[0]



    def pack_type(self, children):
        width_child = children[0]
        if isinstance(width_child, ast.Literal) and width_child.kind == "int":
            width = int(width_child.value)
        else:
            width = int(str(width_child))
        unpacked = children[1]
        if isinstance(unpacked, ast.BoolType):
            unpacked.packed = width
        elif isinstance(unpacked, ast.TableType):
            unpacked.packed = width
        elif isinstance(unpacked, ast.RangeType):
            unpacked.packed = width
        return unpacked

    def val_type(self, children):
        return children[0]

    def type_spec(self, children):
        return children[0]

    def range_type(self, children):
        low, high = children[0]
        return ast.RangeType(low=low, high=high)

    def symbolic_range(self, children):
        return ast.SymbolicRange(members=list(children[0]))

    def bool_type(self, children):
        return ast.BoolType()

    def ptr_type(self, children):
        return ast.PtrType(target=children[-1])

    def set_type(self, children):
        return ast.SetType(member_type=children[-1])

    def area_unrestricted(self, _children=None):
        return "UNRESTRICTED"

    def area_nontransparent(self, _children=None):
        return "NONTRANSPARENT"

    def area_field(self, children):
        return (list(children[0]), children[1])

    def area_field_list(self, children):
        return list(children)

    def area_type(self, children):
        options: list[str] = []
        idx = 0
        while idx < len(children) and isinstance(children[idx], str):
            options.append(children[idx])
            idx += 1
        size_expr = children[idx]
        fields = children[idx + 1]
        return ast.AreaType(options=options, size_expr=size_expr, fields=fields)

    def ovly_field(self, children):
        return (children[0], list(children[1]), children[2])

    def ovly_body(self, children):
        return list(children)

    def struct_type(self, children):
        return ast.StructType(fields=list(children[0]))

    def struct_field_list(self, children):
        return list(children)

    def struct_field(self, children):
        return (list(children[0]), children[1])

    def opt_refines(self, children):
        return children[0] if children else None

    def seg_protected(self, _children=None):
        return "PROTECTED"

    def seg_shared(self, _children=None):
        return "SHARED"

    def seg_private(self, _children=None):
        return "PRIVATE"

    def seg_exclusive(self, _children=None):
        return "EXCLUSIVE"

    def seg_readable(self, _children=None):
        return "READABLE"

    def seg_writable(self, _children=None):
        return "WRITABLE"

    def segment_attr_list(self, children):
        return [str(c) for c in children]

    def meth_abstract(self, _children=None):
        return "ABSTRACT"

    def meth_class(self, _children=None):
        return "CLASS"

    def meth_create(self, _children=None):
        return "CREATE"

    def meth_exclusive(self, _children=None):
        return "EXCLUSIVE"

    def meth_fixed(self, _children=None):
        return "FIXED"

    def meth_hidden(self, _children=None):
        return "HIDDEN"

    def meth_overriding(self, _children=None):
        return "OVERRIDING"

    def segment_flags(self, children):
        return list(children[0]) if children else []

    def class_field(self, children):
        return (list(children[0]), children[1])

    def class_field_list(self, children):
        return list(children)

    def class_data_section(self, children):
        return ast.ClassDataPart(access_attrs=list(children[0]), fields=list(children[1]))

    def class_data_sections(self, children):
        return list(children)

    def method_attr_list(self, children):
        return [str(c) for c in children]

    def method_segment_flags(self, children):
        return list(children[0]) if children else []

    def method_id_list(self, children):
        return [str(c) for c in children]

    def opt_method_parms(self, children):
        return children[0] if children else []

    def opt_method_returns(self, children):
        return children[0] if children else None

    def method_decl_sig(self, children):
        parms = []
        return_type = None
        for child in children:
            if isinstance(child, list) and (not child or isinstance(child[0], tuple)):
                parms = child
            elif child is not None and not isinstance(child, str):
                return_type = child
        return {"parms": parms, "return_type": return_type}

    def method_group(self, children):
        names = list(children[0])
        sig = children[1]
        return ast.MethodDecl(
            names=names,
            parms=sig["parms"],
            return_type=sig["return_type"],
        )

    def method_group_list(self, children):
        return list(children)

    def method_section(self, children):
        attrs = list(children[0])
        methods = list(children[1])
        for method in methods:
            method.attrs = attrs
        return ast.MethodSection(attrs=attrs, methods=methods)

    def method_section_list(self, children):
        return list(children)

    def operations_section(self, children):
        return list(children[0]) if children else []

    def class_type(self, children):
        if len(children) == 3:
            base = None
            data_parts, operations, end_name = children
        else:
            base, data_parts, operations, end_name = children
        return ast.ClassType(
            end_name=str(end_name),
            base=base,
            data_parts=list(data_parts),
            operations=list(operations),
        )

    def class_impl_section(self, children):
        class_name = str(children[0])
        decls: list = []
        stmts: list = []
        for item in children[1:]:
            if isinstance(item, ast.MethodImplDecl):
                decls.append(item)
            elif isinstance(item, (ast.TypeDecl, ast.VarDecl, ast.ProcDecl)):
                decls.append(item)
            else:
                stmts.append(item)
        return ast.ClassImplSection(class_name=class_name, declarations=decls, statements=stmts)

    def in_impl_item(self, children):
        return children[0]

    def method_impl_dcl(self, children):
        return ast.MethodImplDecl(name=str(children[0]), body=children[1])

    def init_value(self, children):
        return children[0]

    def table_type(self, children):
        low, high = children[0]
        return ast.TableType(low=low, high=high, element_type=children[1])

    def desc_type(self, children):
        if len(children) == 1:
            return ast.DescType(low=None, high=None, element_type=children[0])
        low, high = children[0]
        return ast.DescType(low=low, high=high, element_type=children[1])

    def bounds(self, children):
        return children[0]

    def defined_type(self, children):
        if not children:
            return ast.DefinedType(name="")
        return ast.DefinedType(name=str(children[0]))

    def constant_subrange(self, children):
        if len(children) >= 3:
            return self._const_value(children[0]), self._const_value(children[2])
        return self._const_value(children[0]), self._const_value(children[1])

    def constant_expr_atom(self, children):
        return self._const_value(children[0])

    def _const_value(self, node):
        if isinstance(node, ast.Literal):
            return node
        if isinstance(node, Tree):
            return self._const_value(node.children[0])
        return self.literal([node])

    def assign_expr(self, children):
        expr = children[0]
        for tail in children[1:]:
            expr = ast.AssignExpr(value=expr, target=tail)
        return expr

    def assign_tail(self, children):
        return children[-1]

    def or_expr(self, children):
        expr = children[0]
        for rhs in children[1:]:
            expr = ast.BinExpr(op="|", left=expr, right=rhs)
        return expr

    def and_expr(self, children):
        expr = children[0]
        for rhs in children[1:]:
            expr = ast.BinExpr(op="&", left=expr, right=rhs)
        return expr

    def xor_expr(self, children):
        expr = children[0]
        for rhs in children[1:]:
            expr = ast.BinExpr(op="^", left=expr, right=rhs)
        return expr

    def _bin(self, op: str, children):
        return ast.BinExpr(op=op, left=children[0], right=children[1])

    def bin_or(self, c):
        return self._bin("|", c)

    def bin_and(self, c):
        return self._bin("&", c)

    def bin_xor(self, c):
        return self._bin("^", c)

    def bin_eq(self, c):
        return self._bin("=", c)

    def bin_ne(self, c):
        return self._bin("^=", c)

    def bin_gt(self, c):
        return self._bin(">", c)

    def bin_ge(self, c):
        return self._bin(">=", c)

    def bin_lt(self, c):
        return self._bin("<", c)

    def bin_le(self, c):
        return self._bin("<=", c)

    def bin_add(self, c):
        return self._bin("+", c)

    def bin_sub(self, c):
        return self._bin("-", c)

    def bin_mul(self, c):
        return self._bin("*", c)

    def bin_div(self, c):
        return self._bin("/", c)

    def bin_mod(self, c):
        return self._bin("MOD", c)

    def unary_expr(self, children):
        if len(children) == 1:
            return children[0]
        return ast.UnaryExpr(op=str(children[0]), operand=children[1])

    def ref_segment(self, children):
        name = str(children[0])
        if name == "SELF":
            return ast.VarRef(name="SELF", is_self=True)
        if name == "SUPER":
            return ast.VarRef(name="SUPER", is_super=True)
        return ast.VarRef(name=name)

    def self_ref(self, _children=None):
        return ast.VarRef(name="SELF", is_self=True)

    def super_ref(self, _children=None):
        return ast.VarRef(name="SUPER", is_super=True)

    def qual_index(self, children):
        return ("index", children[0])

    def dot_suffix(self, children):
        return ("dot", str(children[0]))

    def call_suffix(self, children):
        if not children:
            return ("call", [])
        return ("call", list(children[0]))

    def _normalize_suffix(self, suffix):
        if isinstance(suffix, tuple):
            return suffix
        if isinstance(suffix, Tree):
            if suffix.data == "dot_suffix":
                return ("dot", str(suffix.children[0]))
            if suffix.data in {"qual_index", "index_suffix"}:
                return ("index", suffix.children[0])
            if suffix.data == "call_suffix":
                if not suffix.children:
                    return ("call", [])
                args = suffix.children[0]
                return ("call", list(args) if isinstance(args, list) else [])
        return suffix

    def _flatten_suffixes(self, nodes):
        out = []
        for node in nodes:
            if isinstance(node, Tree) and node.data == "qual_suffix":
                out.extend(self._flatten_suffixes(node.children))
            else:
                out.append(self._normalize_suffix(node))
        return out

    def qualified_ref(self, children):
        root = children[0]
        suffixes = self._flatten_suffixes(children[1:])
        if suffixes and isinstance(suffixes[-1], tuple) and suffixes[-1][0] == "call":
            args = suffixes[-1][1]
            path = suffixes[:-1]
            if not path:
                name = root.name if isinstance(root, ast.VarRef) else "?"
                return ast.ProcCall(name=name, args=args)
            if path[-1][0] != "dot":
                return ast.ProcCall(name="?", args=args)
            method_name = path[-1][1]
            receiver = self._build_qualified(root, path[:-1])
            return ast.MethodCall(receiver=receiver, name=method_name, args=args)
        return self._build_qualified(root, suffixes)

    def _build_qualified(self, root, suffixes):
        result = root
        for suffix in suffixes:
            if not isinstance(suffix, tuple):
                continue
            if suffix[0] == "dot":
                result = ast.MemberRef(base=result, member=suffix[1])
            elif suffix[0] == "index" and isinstance(result, ast.VarRef):
                result.indices.append(suffix[1])
        return result

    def index_suffix(self, children):
        if len(children) == 1:
            return children[0]
        return (children[0], children[1])

    def actual_list(self, children):
        return list(children)

    def true_lit(self, _children=None):
        return ast.Literal(kind="true", value="TRUE")

    def false_lit(self, _children=None):
        return ast.Literal(kind="false", value="FALSE")

    def nil_lit(self, _children=None):
        return ast.Literal(kind="nil", value="NIL")

    def literal(self, children):
        text = str(children[0])
        if text.startswith("'"):
            return ast.Literal(kind="string", value=text)
        if any(ch in text for ch in ".eE"):
            return ast.Literal(kind="float", value=text)
        return ast.Literal(kind="int", value=text)

    def tuple(self, children):
        if not children:
            return ast.TupleLit(elements=[])
        return ast.TupleLit(elements=list(children[0]))

    def tuple_body_list(self, children):
        return list(children)

    def tuple_elem(self, children):
        return children[0]

    def NUMBER(self, token):
        return str(token)

    def STRING(self, token):
        return str(token)

    def IDENT(self, token):
        return str(token)


class ProtelParser:
    def __init__(self, *, classical: bool = False):
        self.classical = classical
        grammar = _GRAMMAR_PATH.read_text(encoding="utf-8")
        # Earley is required for CASE/SELECT bodies with multiple labelled arms.
        self._lark = Lark(grammar, start="start", parser="earley", lexer="basic")
        self._transformer = ProtelASTBuilder()

    def parse(self, source: str):
        normalized = normalize_keywords(source, classical=self.classical)
        tree = self._lark.parse(normalized)
        return self._transformer.transform(tree)


def parse_protel(source: str, *, classical: bool = False):
    return ProtelParser(classical=classical).parse(source)