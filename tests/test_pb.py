"""Pb beautifier tests."""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parent.parent


def _load_pb() -> ModuleType:
    path = ROOT / "Pb"
    spec = importlib.util.spec_from_loader("pb_module", loader=None)
    module = importlib.util.module_from_spec(spec)
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), module.__dict__)
    return module


def test_dollar_li_line_is_fully_uppercased():
    pb = _load_pb()
    source = "section VDI;\n$li modentry restart\nDCL x BOOL;\n"
    result = pb.beautify_protel(source)
    assert "$LI MODENTRY RESTART\n" in result
    assert "$li modentry" not in result
    assert "DCL" in result


def test_dollar_li_line_with_leading_whitespace():
    pb = _load_pb()
    source = "  $Li modentry restart\n"
    result = pb.beautify_protel(source)
    assert result == "  $LI MODENTRY RESTART\n"


def test_pb_preserves_shebang_first_line():
    pb = _load_pb()
    source = "#!/usr/bin/env protel-run\nsection s;\nDCL x BOOL;\n"
    result = pb.beautify_protel(source)
    assert result.startswith("#!/usr/bin/env protel-run\n")
    assert "SECTION" in result
    assert "DCL" in result


def test_vdi_aa01_dollar_li_directive():
    pb = _load_pb()
    vdi = (ROOT / "vdi.aa01").read_text(encoding="utf-8")
    result = pb.beautify_protel(vdi)
    assert "$LI MODENTRY RESTART" in result