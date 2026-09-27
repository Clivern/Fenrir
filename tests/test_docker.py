# Copyright 2026 Ferir. All rights reserved.
# License can be found in the LICENSE file.

from pathlib import Path

import pytest

from ferir import FerirError, resolve_repo_init_script, write_init_bash


def test_write_init_bash(tmp_path: Path) -> None:
    write_init_bash(str(tmp_path), "echo hi")

    script = tmp_path / "init.sh"
    assert script.read_text() == "#!/usr/bin/env bash\nset -euo pipefail\necho hi\n"
    assert script.stat().st_mode & 0o111


def test_write_init_bash_skips_blank(tmp_path: Path) -> None:
    write_init_bash(str(tmp_path), "  ")
    assert not (tmp_path / "init.sh").exists()


def test_resolve_repo_init_script(tmp_path: Path) -> None:
    (tmp_path / ".ferir").mkdir()
    (tmp_path / ".ferir" / "init.sh").write_text("echo hi\n")

    assert resolve_repo_init_script(str(tmp_path), " .ferir/init.sh ") == ".ferir/init.sh"


def test_resolve_repo_init_script_blank(tmp_path: Path) -> None:
    assert resolve_repo_init_script(str(tmp_path), "") == ""


@pytest.mark.parametrize("rel", ["/etc/init.sh", "../init.sh"])
def test_resolve_repo_init_script_outside_repo(tmp_path: Path, rel: str) -> None:
    with pytest.raises(FerirError, match="must be a path inside the repo"):
        resolve_repo_init_script(str(tmp_path), rel)


def test_resolve_repo_init_script_missing(tmp_path: Path) -> None:
    with pytest.raises(FerirError, match="does not exist"):
        resolve_repo_init_script(str(tmp_path), "init.sh")


def test_resolve_repo_init_script_directory(tmp_path: Path) -> None:
    (tmp_path / "scripts").mkdir()

    with pytest.raises(FerirError, match="must be a file"):
        resolve_repo_init_script(str(tmp_path), "scripts")
