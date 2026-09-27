# Copyright 2026 Ferir. All rights reserved.
# License can be found in the LICENSE file.

from __future__ import annotations

import shutil
from pathlib import Path

from .types import FerirError


class Workspace:
    """The work_dir/id directory holding a run's repo and out directories."""

    def __init__(self, work_dir: str, id: str) -> None:
        self.root = Path(work_dir, id).absolute()
        self.repo_dir = str(self.root / "repo")
        self.out_dir = str(self.root / "out")

    def setup(self) -> tuple[str, str]:
        """Create the job directories and return repo_dir and out_dir."""
        try:
            Path(self.out_dir).mkdir(parents=True, exist_ok=True)
        except OSError as err:
            raise FerirError(f"create out dir: {err}") from err

        return self.repo_dir, self.out_dir

    def remove(self) -> None:
        """Delete the job directory (repo and out). Other ids under work_dir are untouched."""
        try:
            shutil.rmtree(self.root, ignore_errors=False)
        except FileNotFoundError:
            return
        except OSError as err:
            raise FerirError(f"remove job dir: {err}") from err


def setup_workspace(work_dir: str, id: str) -> tuple[str, str]:
    """Resolve work_dir/id/{repo,out} and create the job directories."""
    return Workspace(work_dir, id).setup()


def remove_repo_dir(work_dir: str, id: str) -> None:
    """Delete work_dir/id (repo and out). Other ids under work_dir are untouched."""
    Workspace(work_dir, id).remove()
