# Copyright 2026 Fenrir. All rights reserved.
# License can be found in the LICENSE file.

from __future__ import annotations

import base64
import os
import subprocess
from pathlib import Path

from .types import FenrirError, GitCloneAuth


class GitClone:
    """A shallow clone of repo_url into dest."""

    def __init__(self, repo_url: str, dest: str, auth: GitCloneAuth) -> None:
        self.repo_url = repo_url
        self.dest = dest
        self.auth = auth

    def ensure(self, timeout: float | None = None) -> None:
        """Clone the repository unless dest is already a git repository."""
        if Path(self.dest, ".git").is_dir():
            return

        config_args, env_overrides = self.auth_args()
        env = {**os.environ, **env_overrides}
        args = ["git", *config_args, "clone", "--depth", "1", self.repo_url, self.dest]

        try:
            proc = subprocess.run(
                args,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as err:
            raise FenrirError("clone: timed out") from err
        except FileNotFoundError as err:
            raise FenrirError("clone: git is not installed") from err

        if proc.returncode != 0:
            raise FenrirError(f"clone: {self._message(proc.stderr) or proc.returncode}")

    def auth_args(self) -> tuple[list[str], dict[str, str]]:
        """Return git config args and env for SSH key auth on git@/ssh: URLs, token auth for HTTPS,
        or nothing for public repos."""
        if self.repo_url.startswith(("git@", "ssh:")):
            return self._ssh_args()

        if not self.auth.token:
            return [], {}

        user = self.auth.username or "x-access-token"
        # Sent per request instead of written to .git/config, so the token does not
        # outlive the clone.
        basic = base64.b64encode(f"{user}:{self.auth.token}".encode()).decode()
        return ["-c", f"http.extraHeader=Authorization: Basic {basic}"], {}

    def _ssh_args(self) -> tuple[list[str], dict[str, str]]:
        if not self.auth.ssh_private_key_path:
            return [], {}

        key = Path(self.auth.ssh_private_key_path)
        if not key.is_file():
            raise FenrirError(f"load SSH key: {key} does not exist")

        command = (
            f"ssh -i {key} -o IdentitiesOnly=yes"
            " -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
        )
        return [], {"GIT_SSH_COMMAND": command}

    @staticmethod
    def _message(stderr: bytes | None) -> str:
        return (stderr or b"").decode(errors="replace").strip()


def ensure_clone(
    repo_url: str,
    dest: str,
    auth: GitCloneAuth,
    timeout: float | None = None,
) -> None:
    """Shallow-clone repo_url into dest unless dest is already a git repository."""
    GitClone(repo_url, dest, auth).ensure(timeout=timeout)


def clone_auth(repo_url: str, auth: GitCloneAuth) -> tuple[list[str], dict[str, str]]:
    """Return git config args and env for SSH key auth on git@/ssh: URLs, token auth for HTTPS,
    or nothing for public repos."""
    return GitClone(repo_url, "", auth).auth_args()
