# Copyright 2026 Ferir. All rights reserved.
# License can be found in the LICENSE file.

import subprocess
from pathlib import Path

from ferir import changed_files_in_repo, file_status_letter


def test_file_status_letter_prefers_staging() -> None:
    assert file_status_letter("M", " ") == "M"
    assert file_status_letter(" ", "M") == "M"
    assert file_status_letter("?", "?") == "?"
    assert file_status_letter(" ", " ") == ""


def test_changed_files_in_repo(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "ferir@example.com")
    _git(tmp_path, "config", "user.name", "Ferir")

    (tmp_path / "keep.txt").write_text("one\n")
    (tmp_path / "gone.txt").write_text("two\n")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "init")

    (tmp_path / "keep.txt").write_text("changed\n")
    (tmp_path / "gone.txt").unlink()
    (tmp_path / "new.txt").write_text("fresh\n")

    files = changed_files_in_repo(str(tmp_path))
    by_path = {f.path: f for f in files}

    assert [f.path for f in files] == sorted(by_path)
    assert by_path["keep.txt"].status == "M"
    assert by_path["keep.txt"].content == "changed\n"
    assert by_path["gone.txt"].status == "D"
    assert by_path["gone.txt"].content == ""
    assert by_path["new.txt"].status == "?"
    assert by_path["new.txt"].content == "fresh\n"


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, stdout=subprocess.DEVNULL)
