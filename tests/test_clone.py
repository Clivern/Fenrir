# Copyright 2026 Ferir. All rights reserved.
# License can be found in the LICENSE file.

import base64
from pathlib import Path

import pytest

from ferir import GitCloneAuth, clone_auth, ensure_clone


def test_skips_when_git_present(tmp_path: Path) -> None:
    dest = tmp_path / "repo"
    (dest / ".git").mkdir(parents=True)

    ensure_clone("https://example.com/nope.git", str(dest), GitCloneAuth())


@pytest.mark.network
def test_public_repository(tmp_path: Path) -> None:
    dest = tmp_path / "repo"

    ensure_clone("https://github.com/octocat/Hello-World.git", str(dest), GitCloneAuth())
    assert (dest / ".git").is_dir()


def test_public_https_has_no_auth() -> None:
    assert clone_auth("https://github.com/org/repo.git", GitCloneAuth()) == ([], {})


def test_https_token_default_username() -> None:
    args, env = clone_auth("https://github.com/org/private.git", GitCloneAuth(token="secret"))

    assert env == {}
    assert args[0] == "-c"
    assert args[1] == f"http.extraHeader=Authorization: Basic {_basic('x-access-token', 'secret')}"


def test_https_token_custom_username() -> None:
    args, _ = clone_auth(
        "https://gitlab.com/g/r.git",
        GitCloneAuth(token="tok", username="oauth2"),
    )

    assert args[1] == f"http.extraHeader=Authorization: Basic {_basic('oauth2', 'tok')}"


def test_ssh_url_without_key() -> None:
    assert clone_auth("git@github.com:org/repo.git", GitCloneAuth()) == ([], {})


def test_ssh_url_with_key(tmp_path: Path) -> None:
    key = tmp_path / "id_ed25519"
    key.write_text("key")

    args, env = clone_auth("git@github.com:org/repo.git", GitCloneAuth(ssh_private_key_path=str(key)))

    assert args == []
    assert str(key) in env["GIT_SSH_COMMAND"]
    assert "StrictHostKeyChecking=no" in env["GIT_SSH_COMMAND"]


def _basic(user: str, token: str) -> str:
    return base64.b64encode(f"{user}:{token}".encode()).decode()
