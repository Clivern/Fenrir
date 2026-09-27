# Copyright 2026 Ferir. All rights reserved.
# License can be found in the LICENSE file.

from __future__ import annotations

from dataclasses import dataclass, field


class FerirError(Exception):
    """Raised for every failure returned by this package."""


@dataclass
class GitCloneAuth:
    """Credentials for cloning private repositories."""

    token: str = ""
    username: str = ""
    ssh_private_key_path: str = ""


@dataclass
class Container:
    """Init hooks and docker run limits."""

    init_script: str = ""
    init_bash: str = ""
    memory: str = ""
    cpus: str = ""


@dataclass
class RunRequest:
    """Configures a Pi Docker run against a cloned repository."""

    work_dir: str = ""
    # id identifies this run. It names the container and Pi sends it as the
    # OpenRouter API key (Authorization: Bearer <id>).
    id: str = ""
    repo_url: str = ""
    prompt: str = ""
    pi_model: str = ""
    # proxy_url is Pi's OpenRouter base URL.
    # Example: http://host.docker.internal:8080/api
    proxy_url: str = ""
    docker_image: str = ""
    git_clone_auth: GitCloneAuth = field(default_factory=GitCloneAuth)
    container: Container = field(default_factory=Container)
    cleanup: bool = False


@dataclass
class ChangedFile:
    """One path touched by the agent."""

    path: str
    status: str
    content: str = ""


@dataclass
class Result:
    """Artifacts from a successful run."""

    patch: str
    summary: str
    total_tokens: int
    changed_files: list[ChangedFile]
    repo_dir: str
    out_dir: str


@dataclass
class DockerParams:
    image: str = ""
    id: str = ""
    proxy_url: str = ""
    prompt: str = ""
    pi_model: str = ""
    repo_dir: str = ""
    out_dir: str = ""
    container: Container = field(default_factory=Container)
    init_script: str = ""
