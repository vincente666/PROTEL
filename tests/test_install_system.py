"""System-wide install Makefile targets (staged under DESTDIR)."""

import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _make(*targets: str, env: dict | None = None) -> subprocess.CompletedProcess:
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    return subprocess.run(
        ["make", *targets],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env=run_env,
    )


def test_install_system_staged_layout():
    stage = ROOT / "build" / "install-stage"
    if stage.exists():
        shutil.rmtree(stage)
    prefix = "/usr/local/protel"
    result = _make(
        "install-system",
        env={
            "DESTDIR": str(stage),
            "SYSPREFIX": prefix,
            "SYSBINDIR": "/usr/local/bin",
            "SYSMANPREFIX": "/usr/local/share/man",
        },
    )
    assert result.returncode == 0, result.stderr + result.stdout

    toolkit = stage / prefix.lstrip("/")
    bindir = stage / "usr/local/bin"
    mandir = stage / "usr/local/share/man/man1"

    for name in ("Pc", "Pb", "Pc!"):
        tool = toolkit / name
        assert tool.is_file(), f"missing {tool}"
        assert os.access(tool, os.X_OK)
        link = bindir / name
        assert link.is_symlink(), f"missing symlink {link}"
        assert os.readlink(link) == f"{prefix}/{name}"

    assert (toolkit / "src" / "parser.py").is_file()
    assert (toolkit / "examples" / "Hello.P").is_file()
    assert (toolkit / "emacs" / "protel-mode.el").is_file()
    assert (toolkit / ".venv" / "bin" / "python3").is_file()
    assert (mandir / "Pc.1").is_file()
    assert (mandir / "Pb.1").is_file()

    shutil.rmtree(stage)


def test_makefile_declares_install_system_target():
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "install-system:" in makefile
    assert "install-man-system:" in makefile
    assert "uninstall-system:" in makefile
    assert "SYSPREFIX ?=" in makefile
    assert "/usr/local/protel" in makefile