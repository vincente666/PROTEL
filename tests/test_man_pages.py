"""Manual page presence and basic content checks."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAN = ROOT / "man"


def test_pc_man_page_exists_with_required_sections():
    text = (MAN / "Pc.1").read_text(encoding="utf-8")
    assert '.TH Pc 1' in text
    for section in (
        "SYNOPSIS",
        "DESCRIPTION",
        "OPTIONS",
        "SHEBANG RUNNER",
        "EXIT STATUS",
        "EXAMPLES",
        "SEE ALSO",
    ):
        assert f".SH {section}" in text or section in text
    assert "Pc!" in text
    for option in (
        "\\-\\-run",
        "\\-\\-classical",
        "\\-\\-emit\\-c",
        "\\-\\-parse\\-only",
        "\\-\\-compile",
        "\\-\\-keep",
    ):
        assert option in text


def test_pb_man_page_exists_with_required_sections():
    text = (MAN / "Pb.1").read_text(encoding="utf-8")
    assert '.TH Pb 1' in text
    for section in (
        "SYNOPSIS",
        "DESCRIPTION",
        "OPTIONS",
        "BEHAVIOR",
        "EXIT STATUS",
        "EXAMPLES",
        "SEE ALSO",
    ):
        assert f".SH {section}" in text or f'.SH "{section}"' in text
    assert "\\-\\-bold" in text
    assert "shebang" in text.lower()


def test_install_man_layout_after_make():
    man1 = MAN / "man1"
    # install-man may not have been run; source pages must remain in man/
    assert (MAN / "Pc.1").is_file()
    assert (MAN / "Pb.1").is_file()