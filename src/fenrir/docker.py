# Copyright 2026 Fenrir. All rights reserved.
# License can be found in the LICENSE file.

from __future__ import annotations

import subprocess
from pathlib import Path

from .types import DockerParams, FenrirError


class DockerRun:
    """One `docker run` of the Pi image against a cloned repository."""

    # Grace period for the docker client to exit after the container is killed.
    CLIENT_GRACE_SECONDS = 15.0

    def __init__(self, params: DockerParams) -> None:
        self.params = params

    def execute(self, timeout: float | None = None) -> None:
        try:
            proc = subprocess.Popen(self._args(), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        except FileNotFoundError as err:
            raise FenrirError("docker run: docker is not installed") from err

        try:
            _, stderr = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            # Killing the docker client leaves the container running. Stop the
            # container itself so a deadline ends init scripts and Pi.
            self._kill()
            stderr = self._drain(proc)
            raise FenrirError(f"docker run: {self._message(stderr) or 'timed out'}")

        if proc.returncode != 0:
            raise FenrirError(f"docker run: {self._message(stderr) or proc.returncode}")

    def _args(self) -> list[str]:
        params = self.params
        container = params.container

        args = [
            "docker",
            "run",
            "--rm",
            "--name",
            params.id,
            "--memory",
            container.memory,
            "--cpus",
            container.cpus,
        ]

        for name, value in self._env().items():
            args += ["-e", f"{name}={value}"]

        repo = str(Path(params.repo_dir).absolute())
        out = str(Path(params.out_dir).absolute())
        args += ["-v", f"{repo}:/repo", "-v", f"{out}:/out", params.image]

        return args

    def _env(self) -> dict[str, str]:
        params = self.params
        env = {
            "RUN_ID": params.id,
            "PROXY_URL": params.proxy_url,
            "PROMPT": params.prompt,
            "PI_MODEL": params.pi_model,
        }

        if params.init_script:
            env["INIT_SCRIPT"] = params.init_script

        return env

    def _kill(self) -> None:
        try:
            subprocess.run(
                ["docker", "kill", self.params.id],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=self.CLIENT_GRACE_SECONDS,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            pass

    def _drain(self, proc: subprocess.Popen[bytes]) -> bytes | None:
        try:
            _, stderr = proc.communicate(timeout=self.CLIENT_GRACE_SECONDS)
            return stderr
        except subprocess.TimeoutExpired:
            proc.kill()
            _, stderr = proc.communicate()
            return stderr

    @staticmethod
    def _message(stderr: bytes | None) -> str:
        return (stderr or b"").decode(errors="replace").strip()


class InitScripts:
    """The container's init hooks: a script inside the repo and inline bash written to out."""

    def __init__(self, repo_dir: str = "", out_dir: str = "") -> None:
        self.repo_dir = repo_dir
        self.out_dir = out_dir

    def write_bash(self, bash: str) -> None:
        if not bash.strip():
            return

        path = Path(self.out_dir, "init.sh")
        path.write_text("#!/usr/bin/env bash\nset -euo pipefail\n" + bash + "\n")
        path.chmod(0o755)

    def resolve_repo_script(self, rel: str) -> str:
        rel = rel.strip()
        if not rel:
            return ""

        if Path(rel).is_absolute() or ".." in rel:
            raise FenrirError("Container.InitScript must be a path inside the repo")

        rel = rel.replace("\\", "/")
        host = Path(self.repo_dir, rel)

        if not host.exists():
            raise FenrirError(f"Container.InitScript: {host} does not exist")
        if host.is_dir():
            raise FenrirError("Container.InitScript must be a file")

        return rel


def run_docker(params: DockerParams, timeout: float | None = None) -> None:
    DockerRun(params).execute(timeout=timeout)


def write_init_bash(out_dir: str, bash: str) -> None:
    InitScripts(out_dir=out_dir).write_bash(bash)


def resolve_repo_init_script(repo_dir: str, rel: str) -> str:
    return InitScripts(repo_dir=repo_dir).resolve_repo_script(rel)
