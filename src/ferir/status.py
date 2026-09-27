# Copyright 2026 Ferir. All rights reserved.
# License can be found in the LICENSE file.

from __future__ import annotations

import subprocess
from pathlib import Path

from .types import ChangedFile, FerirError


class GitStatus:
    """The git status of a cloned repository after the agent has run."""

    RENAMED = ("R", "C")

    def __init__(self, repo_dir: str) -> None:
        self.repo_dir = repo_dir

    def changed_files(self) -> list[ChangedFile]:
        """List every path with a non-clean git status, sorted by path."""
        files: list[ChangedFile] = []

        for letter, path in self._parse_porcelain(self._porcelain()):
            content = ""
            if letter != "D":
                try:
                    content = Path(self.repo_dir, path).read_text(errors="replace")
                except OSError as err:
                    raise FerirError(f"{path}: {err}") from err
            files.append(ChangedFile(path=path, status=letter, content=content))

        files.sort(key=lambda f: f.path)
        return files

    def _porcelain(self) -> str:
        try:
            proc = subprocess.run(
                ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
                cwd=self.repo_dir,
                capture_output=True,
                check=False,
            )
        except FileNotFoundError as err:
            raise FerirError("status: git is not installed") from err

        if proc.returncode != 0:
            raise FerirError(f"status: {(proc.stderr or b'').decode(errors='replace').strip()}")

        return proc.stdout.decode(errors="replace")

    @classmethod
    def _parse_porcelain(cls, stdout: str) -> list[tuple[str, str]]:
        entries = [e for e in stdout.split("\0") if e]
        out: list[tuple[str, str]] = []

        index = 0
        while index < len(entries):
            entry = entries[index]
            index += 1
            if len(entry) < 4:
                continue

            letter = cls.status_letter(entry[0], entry[1])
            path = entry[3:]
            # In -z mode a rename or copy is followed by its original path.
            if entry[0] in cls.RENAMED or entry[1] in cls.RENAMED:
                index += 1
            if letter:
                out.append((letter, path))

        return out

    @staticmethod
    def status_letter(staging: str, worktree: str) -> str:
        """Return the porcelain status code, staging first. "" means unmodified."""
        code = worktree
        if staging != " ":
            code = staging
        if code == " ":
            return ""
        return code


def changed_files_in_repo(repo_dir: str) -> list[ChangedFile]:
    """List every path with a non-clean git status, sorted by path."""
    return GitStatus(repo_dir).changed_files()


def file_status_letter(staging: str, worktree: str) -> str:
    """Return the porcelain status code, staging first. "" means unmodified."""
    return GitStatus.status_letter(staging, worktree)
