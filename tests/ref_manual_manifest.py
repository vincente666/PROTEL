"""Reference Manual section and keyword coverage registry (oflpr TOC)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"
REF = EXAMPLES / "ref"

# Every numbered Reference Manual section maps to at least one example or test corpus file.
REFERENCE_MANUAL_SECTIONS: dict[str, list[str]] = {
    "1.0": ["ref/ref_1_0_introduction.protel"],
    "2.0": ["ref/ref_9_1_expressions.protel"],
    "3.0": ["ref/ref_3_0_lexical.protel"],
    "3.1": ["ref/ref_3_0_lexical.protel"],
    "3.2": ["ref/ref_3_0_lexical.protel"],
    "3.3": ["ref/ref_3_0_lexical.protel"],
    "3.4": ["ref/ref_3_0_lexical.protel"],
    "4.0": ["ref/ref_4_0_data_elements.protel"],
    "4.1": ["ref/ref_4_0_data_elements.protel"],
    "4.2": ["ref/ref_4_0_data_elements.protel"],
    "4.3": ["ref/ref_4_0_data_elements.protel"],
    "4.4": ["ref/ref_4_0_data_elements.protel"],
    "4.5": ["ref/ref_4_0_data_elements.protel"],
    "5.0": [
        "ref/ref_5_0_compilation_unit.protel",
        "ref/ref_5_0_directives.aa01",
        "Hello.aa01",
    ],
    "6.0": ["ref/ref_6_0_module_types.protel"],
    "7.0": ["ref/ref_7_0_declarations.protel"],
    "7.1": ["ref/ref_7_1_1_simple_types.protel", "ref/ref_7_1_2_aggregates.protel"],
    "7.1.1": ["ref/ref_7_1_1_simple_types.protel"],
    "7.1.1.1": ["ref/ref_7_1_1_simple_types.protel"],
    "7.1.1.2": ["intro_2_1_types.protel"],
    "7.1.1.3": ["ref/ref_7_1_1_simple_types.protel", "intro_2_1_types.protel"],
    "7.1.1.4": ["ref/ref_7_1_1_simple_types.protel"],
    "7.1.1.5": ["ref/ref_7_1_1_simple_types.protel"],
    "7.1.2": ["ref/ref_7_1_2_aggregates.protel"],
    "7.1.2.1": ["ref/ref_7_1_2_aggregates.protel"],
    "7.1.2.2": ["ref/ref_7_1_2_aggregates.protel", "ref_8_1_task_block_struct.protel"],
    "7.1.2.3": ["intro_2_1_types.protel", "intro_3_2_6_sum_table.protel"],
    "7.1.2.4": ["intro_2_1_types.protel"],
    "7.1.2.5": ["ref/ref_7_1_2_aggregates.protel"],
    "7.1.3": ["ref/ref_7_1_3_procedures.protel"],
    "7.1.3.1": ["ref/ref_7_1_3_procedures.protel"],
    "7.1.3.2": ["ref/ref_7_1_3_procedures.protel"],
    "7.2": ["ref/ref_7_2_data_declarations.protel"],
    "7.2.1": ["ref/ref_7_2_data_declarations.protel"],
    "7.2.2": ["intro_2_2_calculate_average.protel"],
    "7.2.3": ["ref/ref_7_2_data_declarations.protel"],
    "7.3": ["ref/ref_7_3_overlays.protel"],
    "8.0": ["ref/ref_8_0_scope.protel"],
    "8.1": ["ref/ref_8_0_scope.protel"],
    "8.2": ["ref/ref_8_0_scope.protel"],
    "9.0": ["ref/ref_9_0_statements.protel"],
    "9.1": ["ref/ref_9_1_expressions.protel"],
    "9.1.1": ["ref/ref_9_1_expressions.protel"],
    "9.1.1.1": ["ref/ref_4_0_data_elements.protel"],
    "9.1.1.2": ["ref/ref_9_1_expressions.protel"],
    "9.1.1.3": ["ref/ref_7_1_3_procedures.protel"],
    "9.1.2": ["ref/ref_9_1_expressions.protel"],
    "9.2": ["ref/ref_9_2_return.protel", "intro_5_5_2_args_exit.protel"],
    "9.3": ["ref/ref_9_3_if.protel"],
    "9.4": ["ref/ref_9_4_case.protel", "intro_3_2_4_case.protel"],
    "9.5": ["ref/ref_9_5_select.protel"],
    "9.6": ["ref/ref_9_6_exit.protel"],
    "9.7": [
        "ref/ref_9_7_iterative.protel",
        "intro_1_3_factorial.protel",
        "intro_1_3_factorial_cli.protel",
        "intro_3_2_6_sum_table.protel",
    ],
    "10.0": ["ref/ref_10_0_bind_with.protel"],
    "11.0": ["ref/ref_11_0_type_compat.protel"],
    "11.1": ["ref/ref_11_0_type_compat.protel"],
    "11.2": ["ref/ref_11_0_type_compat.protel"],
    "11.3": ["ref/ref_11_0_type_compat.protel"],
    "12.0": ["ref/ref_12_0_intrinsic.protel"],
    "13.0": [
        "ref/ref_13_0_descriptors.protel",
        "interop/protel_for_python.protel",
        "interop/protel_calls_python.protel",
        "Hello.protel",
    ],
    "14.0": ["ref/ref_14_0_keyword_exercise.protel"],
    "15.0": ["tests/test_parser.py"],
    "16.0": ["tests/ref_manual_manifest.py"],
    "OO": ["ref/ref_oo_classes.protel", "ref_oo_class_with_var.protel", "ref_oo_class_method_invoke.protel"],
}

# Keywords exercised outside .protel examples (preprocessor / tooling).
KEYWORD_EXTERNAL_SOURCES: dict[str, list[str]] = {
    "$EJECT": ["ref/ref_5_0_directives.aa01", "tests/test_pb.py"],
    "$LI": ["ref/ref_5_0_directives.aa01", "vdi.aa01", "tests/test_pb.py"],
    "$OBJECT": ["ref/ref_oo_classes.protel", "ref_oo_class_with_var.protel"],
    "$REFDESC": ["ref/ref_9_1_expressions.protel"],
    "$TYPEDESC": ["ref/ref_9_1_expressions.protel"],
    "$UNIVERSAL_PTR": ["ref/ref_9_1_expressions.protel"],
    "$VARDESC": ["ref/ref_9_1_expressions.protel"],
}

# All ref_* and intro_* example files that must parse.
REF_EXAMPLE_SOURCES: list[str] = sorted(
    p.relative_to(EXAMPLES).as_posix()
    for p in EXAMPLES.rglob("*.protel")
    if p.is_file() and not p.name.endswith("~")
)