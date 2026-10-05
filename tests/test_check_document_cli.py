"""CLI regressions for report paths that could overwrite the source."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "check_document.py"


def invoke(source: Path, output: Path, *, apply: bool = False) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(SCRIPT), str(source), "--output", str(output)]
    if apply:
        command.append("--apply")
    return subprocess.run(command, text=True, capture_output=True, check=False)


def test_rejects_identical_path_before_apply_and_preserves_bytes(tmp_path: Path) -> None:
    source = tmp_path / "document.md"
    original = "必要なら設定を確認できます。\n".encode("utf-8")
    source.write_bytes(original)
    result = invoke(source, source, apply=True)
    assert result.returncode != 0
    assert b"--output must not refer" in result.stderr.encode()
    assert source.read_bytes() == original


def test_rejects_relative_alias_and_preserves_bytes(tmp_path: Path) -> None:
    source = tmp_path / "document.md"
    original = "必要なら設定を確認できます。\n".encode("utf-8")
    source.write_bytes(original)
    result = invoke(source, tmp_path / "." / "document.md")
    assert result.returncode != 0
    assert source.read_bytes() == original


def test_rejects_symlink_alias_and_preserves_bytes(tmp_path: Path) -> None:
    source = tmp_path / "document.md"
    alias = tmp_path / "alias.md"
    original = "必要なら設定を確認できます。\n".encode("utf-8")
    source.write_bytes(original)
    alias.symlink_to(source)
    result = invoke(source, alias)
    assert result.returncode != 0
    assert source.read_bytes() == original


def test_rejects_hardlink_alias_and_preserves_bytes(tmp_path: Path) -> None:
    source = tmp_path / "document.md"
    alias = tmp_path / "hardlink.md"
    original = "必要なら設定を確認できます。\n".encode("utf-8")
    source.write_bytes(original)
    os.link(source, alias)
    result = invoke(source, alias, apply=True)
    assert result.returncode != 0
    assert source.read_bytes() == original
    assert alias.read_bytes() == original


def test_distinct_output_and_dry_run_still_work(tmp_path: Path) -> None:
    source = tmp_path / "document.md"
    output = tmp_path / "report.json"
    original = "必要なら設定を確認できます。\n".encode("utf-8")
    source.write_bytes(original)
    result = invoke(source, output)
    assert result.returncode == 0, result.stderr
    assert output.is_file()
    assert source.read_bytes() == original


def test_distinct_output_with_apply_rewrites_source(tmp_path: Path) -> None:
    source = tmp_path / "document.md"
    output = tmp_path / "report.json"
    original = "必要なら設定を確認できます。\n".encode("utf-8")
    source.write_bytes(original)
    result = invoke(source, output, apply=True)
    assert result.returncode == 0, result.stderr
    assert source.read_bytes() != original
    assert output.is_file()
