# Copyright 2026 Ferir. All rights reserved.
# License can be found in the LICENSE file.

from pathlib import Path

from ferir import remove_repo_dir, setup_workspace


def test_setup_workspace(tmp_path: Path) -> None:
    repo, out = setup_workspace(str(tmp_path), "abc-123")

    assert repo == str(tmp_path / "abc-123" / "repo")
    assert out == str(tmp_path / "abc-123" / "out")
    assert Path(out).is_dir()

    remove_repo_dir(str(tmp_path), "abc-123")
    assert not (tmp_path / "abc-123").exists()
