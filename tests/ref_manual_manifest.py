"""Reference Manual section and keyword coverage registry (oflpr TOC)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"
REF = EXAMPLES / "ref"

# Every numbered Reference Manual section maps to at least one example or test corpus file.
REFERENCE_MANUAL_SECTIONS: dict[str, list[str]] = {
    "1.0": ["ref/ref_1_0_introduction.P"],
    "2.0": ["ref/ref_9_1_expressions.P"],
    "3.0": ["ref/ref_3_0_lexical.P"],
    "3.1": ["ref/ref_3_0_lexical.P"],
    "3.2": ["ref/ref_3_0_lexical.P"],
    "3.3": ["ref/ref_3_0_lexical.P"],
    "3.4": ["ref/ref_3_0_lexical.P"],
    "4.0": ["ref/ref_4_0_data_elements.P"],
    "4.1": ["ref/ref_4_0_data_elements.P"],
    "4.2": ["ref/ref_4_0_data_elements.P"],
    "4.3": ["ref/ref_4_0_data_elements.P"],
    "4.4": ["ref/ref_4_0_data_elements.P"],
    "4.5": ["ref/ref_4_0_data_elements.P"],
    "5.0": [
        "ref/ref_5_0_compilation_unit.P",
        "ref/ref_5_0_directives.aa01",
        "Hello.aa01",
    ],
    "6.0": ["ref/ref_6_0_module_types.P"],
    "7.0": ["ref/ref_7_0_declarations.P"],
    "7.1": ["ref/ref_7_1_1_simple_types.P", "ref/ref_7_1_2_aggregates.P"],
    "7.1.1": ["ref/ref_7_1_1_simple_types.P"],
    "7.1.1.1": ["ref/ref_7_1_1_simple_types.P"],
    "7.1.1.2": ["intro_2_1_types.P"],
    "7.1.1.3": ["ref/ref_7_1_1_simple_types.P", "intro_2_1_types.P"],
    "7.1.1.4": ["ref/ref_7_1_1_simple_types.P"],
    "7.1.1.5": ["ref/ref_7_1_1_simple_types.P"],
    "7.1.2": ["ref/ref_7_1_2_aggregates.P"],
    "7.1.2.1": ["ref/ref_7_1_2_aggregates.P"],
    "7.1.2.2": ["ref/ref_7_1_2_aggregates.P", "ref_8_1_task_block_struct.P"],
    "7.1.2.3": ["intro_2_1_types.P", "intro_3_2_6_sum_table.P"],
    "7.1.2.4": ["intro_2_1_types.P"],
    "7.1.2.5": ["ref/ref_7_1_2_aggregates.P"],
    "7.1.3": ["ref/ref_7_1_3_procedures.P"],
    "7.1.3.1": ["ref/ref_7_1_3_procedures.P"],
    "7.1.3.2": ["ref/ref_7_1_3_procedures.P"],
    "7.2": ["ref/ref_7_2_data_declarations.P"],
    "7.2.1": ["ref/ref_7_2_data_declarations.P"],
    "7.2.2": ["intro_2_2_calculate_average.P"],
    "7.2.3": ["ref/ref_7_2_data_declarations.P"],
    "7.3": ["ref/ref_7_3_overlays.P"],
    "8.0": ["ref/ref_8_0_scope.P"],
    "8.1": ["ref/ref_8_0_scope.P"],
    "8.2": ["ref/ref_8_0_scope.P"],
    "9.0": ["ref/ref_9_0_statements.P"],
    "9.1": ["ref/ref_9_1_expressions.P"],
    "9.1.1": ["ref/ref_9_1_expressions.P"],
    "9.1.1.1": ["ref/ref_4_0_data_elements.P"],
    "9.1.1.2": ["ref/ref_9_1_expressions.P"],
    "9.1.1.3": ["ref/ref_7_1_3_procedures.P"],
    "9.1.2": ["ref/ref_9_1_expressions.P"],
    "9.2": ["ref/ref_9_2_return.P", "intro_5_5_2_args_exit.P"],
    "9.3": ["ref/ref_9_3_if.P"],
    "9.4": ["ref/ref_9_4_case.P", "intro_3_2_4_case.P"],
    "9.5": ["ref/ref_9_5_select.P"],
    "9.6": ["ref/ref_9_6_exit.P"],
    "9.7": [
        "ref/ref_9_7_iterative.P",
        "intro_1_3_factorial.P",
        "intro_1_3_factorial_cli.P",
        "intro_3_2_6_sum_table.P",
    ],
    "10.0": ["ref/ref_10_0_bind_with.P"],
    "11.0": ["ref/ref_11_0_type_compat.P"],
    "11.1": ["ref/ref_11_0_type_compat.P"],
    "11.2": ["ref/ref_11_0_type_compat.P"],
    "11.3": ["ref/ref_11_0_type_compat.P"],
    "12.0": ["ref/ref_12_0_intrinsic.P"],
    "13.0": [
        "ref/ref_13_0_descriptors.P",
        "interop/protel_for_python.P",
        "interop/protel_calls_python.P",
        "Hello.P",
    ],
    "14.0": ["ref/ref_14_0_keyword_exercise.P"],
    "15.0": ["tests/test_parser.py"],
    "16.0": ["tests/ref_manual_manifest.py"],
    "OO": ["ref/ref_oo_classes.P", "ref_oo_class_with_var.P", "ref_oo_class_method_invoke.P"],
}

# Keywords exercised outside .P examples (preprocessor / tooling).
KEYWORD_EXTERNAL_SOURCES: dict[str, list[str]] = {
    "$EJECT": ["ref/ref_5_0_directives.aa01", "tests/test_pb.py"],
    "$LI": ["ref/ref_5_0_directives.aa01", "vdi.aa01", "tests/test_pb.py"],
    "$OBJECT": ["ref/ref_oo_classes.P", "ref_oo_class_with_var.P"],
    "$REFDESC": ["ref/ref_9_1_expressions.P"],
    "$TYPEDESC": ["ref/ref_9_1_expressions.P"],
    "$UNIVERSAL_PTR": ["ref/ref_9_1_expressions.P"],
    "$VARDESC": ["ref/ref_9_1_expressions.P"],
}

# All ref_* and intro_* example files that must parse.
REF_EXAMPLE_SOURCES: list[str] = sorted(
    p.relative_to(EXAMPLES).as_posix()
    for p in EXAMPLES.rglob("*.P")
    if p.is_file() and not p.name.endswith("~")
)