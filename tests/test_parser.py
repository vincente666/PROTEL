"""Parser tests correlated to PROTEL 2026 manuals."""

from pathlib import Path

import pytest

from src.parser import parse_protel
from src import ast_nodes as ast

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def _read(name: str) -> str:
    return (EXAMPLES / name).read_text(encoding="utf-8")


def test_parse_section_uses_and_of():
    tree = parse_protel(
        "SECTION ref_provider;\n"
        "SECTION ref_consumer OF ref_provider USES ref_provider;\n"
    )
    assert tree[1].of_modules == ["ref_provider"]
    assert tree[1].uses_modules == ["ref_provider"]


def test_parse_factorial_example():
    tree = parse_protel(_read("intro_1_3_factorial.P"))
    assert len(tree) == 1
    section = tree[0]
    assert isinstance(section, ast.Section)
    assert section.name == "factorial_demo"

    proc = next(d for d in section.declarations if isinstance(d, ast.ProcDecl))
    assert proc.name == "factorial"
    assert proc.return_type is not None
    assert isinstance(proc.body, ast.Block)
    assert any(isinstance(s, ast.LoopStmt) for s in proc.body.statements)


def test_parse_types_example():
    tree = parse_protel(_read("intro_2_1_types.P"))
    section = tree[0]
    type_names = {d.names[0] for d in section.declarations if isinstance(d, ast.TypeDecl)}
    assert "integer" in type_names
    assert "digit_register" in type_names
    assert "features_table" in type_names


def test_parse_calculate_average():
    tree = parse_protel(_read("intro_2_2_calculate_average.P"))
    proc = next(
        d for d in tree[0].declarations if isinstance(d, ast.ProcDecl)
    )
    assert proc.name == "calculate_average"
    assert len(proc.parms) == 1
    assert proc.parms[0][0] == ["number_1", "number_2"]


def test_classical_keyword_casing():
    source = """
    section demo;
    type integer {-32768 to 32767};
    dcl x integer;
    """
    tree = parse_protel(source, classical=True)
    assert tree[0].name == "demo"
    type_decl = next(d for d in tree[0].declarations if isinstance(d, ast.TypeDecl))
    assert type_decl.names == ["integer"]


def test_parse_case_statement():
    tree = parse_protel(_read("intro_3_2_4_case.P"))
    proc = next(d for d in tree[0].declarations if isinstance(d, ast.ProcDecl))
    case_stmt = proc.body.statements[0]
    assert isinstance(case_stmt, ast.CaseStmt)
    assert len(case_stmt.arms) == 3
    assert case_stmt.out_statements == []


def test_parse_for_loop_with_upb():
    tree = parse_protel(_read("intro_3_2_6_sum_table.P"))
    proc = next(d for d in tree[0].declarations if isinstance(d, ast.ProcDecl))
    for_stmt = next(s for s in proc.body.statements if isinstance(s, ast.ForStmt))
    assert for_stmt.var == "i"
    assert isinstance(for_stmt.to_expr, ast.BuiltinExpr)
    assert for_stmt.to_expr.name == "UPB"


def test_parse_struct_type():
    tree = parse_protel(_read("ref_8_1_task_block_struct.P"))
    task_block = next(
        d for d in tree[0].declarations
        if isinstance(d, ast.TypeDecl) and d.names == ["task_block"]
    )
    assert isinstance(task_block.type_spec, ast.StructType)
    assert len(task_block.type_spec.fields) == 5


def test_var_init_not_wrapped_in_tree():
    tree = parse_protel(_read("intro_2_1_types.P"))
    primes = next(d for d in tree[0].declarations if isinstance(d, ast.VarDecl) and "primes" in d.names)
    assert isinstance(primes.init, ast.TupleLit)


def test_parse_class_type_with_operations():
    tree = parse_protel(_read("ref_oo_class_with_var.P"))
    section = tree[0]
    assert section.section_kind == "INTERFACE"
    class_decl = next(
        d for d in section.declarations
        if isinstance(d, ast.TypeDecl) and d.names == ["class_with_var"]
    )
    spec = class_decl.type_spec
    assert isinstance(spec, ast.ClassType)
    assert spec.end_name == "class_with_var"
    assert spec.base.name == "$OBJECT"
    assert len(spec.data_parts) == 2
    assert spec.data_parts[0].access_attrs == ["PROTECTED"]
    method = spec.operations[0].methods[0]
    assert method.names == ["class_method"]
    assert method.attrs == ["CLASS"]
    assert len(section.class_impls) == 1
    assert section.class_impls[0].class_name == "class_with_var"


def test_parse_class_method_invocation():
    tree = parse_protel(_read("ref_oo_class_method_invoke.P"))
    proc = next(d for d in tree[0].declarations if isinstance(d, ast.ProcDecl))
    assert isinstance(proc.body.statements[0], ast.MethodCall)
    assert proc.body.statements[0].name == "class_method"
    assert isinstance(proc.body.statements[1], ast.MethodCall)


def test_parse_self_member_assignment():
    tree = parse_protel(_read("ref_oo_class_with_var.P"))
    impl = tree[0].class_impls[0]
    stmt = impl.declarations[0].body.statements[0]
    assert isinstance(stmt, ast.AssignExpr)
    assert isinstance(stmt.target, ast.MemberRef)
    assert stmt.target.member == "class_var"


def test_assignment_expression_chaining():
    source = """
    SECTION demo;
    TYPE integer {-32768 TO 32767};
    DCL p PROC() IS
    BLOCK
       DCL a, b, c integer;
       1 -> a -> b -> c;
    ENDBLOCK;
    """
    tree = parse_protel(source)
    proc = next(d for d in tree[0].declarations if isinstance(d, ast.ProcDecl))
    stmt = proc.body.statements[0]
    assert isinstance(stmt, ast.AssignExpr)
    assert isinstance(stmt.target, ast.VarRef)
    assert stmt.target.name == "c"