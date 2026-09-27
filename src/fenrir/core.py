# Copyright 2026 Fenrir. All rights reserved.
# License can be found in the LICENSE file.

from __future__ import annotations

import time
from pathlib import Path

from .clone import GitClone
from .docker import DockerRun, InitScripts
from .out import PiOutput
from .status import GitStatus
from .types import DockerParams, FenrirError, Result, RunRequest
from .validate import RequestValidator
from .workspace import Workspace


class Deadline:
    """A wall-clock budget shared by the clone and the container."""

    def __init__(self, timeout: float | None) -> None:
        self.expires_at = None if timeout is None else time.monotonic() + timeout

    def remaining(self) -> float | None:
        if self.expires_at is None:
            return None
        return max(self.expires_at - time.monotonic(), 0.0)


class Runner:
    """Clones the repo if needed, runs the Pi container, and collects the patch."""

    def __init__(self, req: RunRequest) -> None:
        self.req = req

    def run(self, timeout: float | None = None) -> Result:
        """Run the request and return its artifacts.

        timeout is the deadline in seconds for the whole run, covering the clone and
        the container. When it expires the container is killed, which ends init
        scripts and Pi.
        """
        req = self.req
        RequestValidator(req).validate()

        deadline = Deadline(timeout)
        workspace = Workspace(req.work_dir, req.id)
        repo_dir, out_dir = workspace.setup()

        GitClone(req.repo_url, repo_dir, req.git_clone_auth).ensure(timeout=deadline.remaining())

        init = InitScripts(repo_dir=repo_dir, out_dir=out_dir)
        init_script = init.resolve_repo_script(req.container.init_script)

        try:
            init.write_bash(req.container.init_bash)
        except OSError as err:
            raise FenrirError(f"write inline init: {err}") from err

        DockerRun(
            DockerParams(
                image=req.docker_image,
                id=req.id,
                proxy_url=req.proxy_url.strip(),
                prompt=req.prompt,
                pi_model=req.pi_model,
                repo_dir=repo_dir,
                out_dir=out_dir,
                container=req.container,
                init_script=init_script,
            ),
        ).execute(timeout=deadline.remaining())

        result = self._collect(repo_dir, out_dir)

        if req.cleanup:
            workspace.remove()

        return result

    def _collect(self, repo_dir: str, out_dir: str) -> Result:
        try:
            patch = Path(out_dir, "patch.diff").read_text(errors="replace")
        except OSError as err:
            raise FenrirError(f"read patch.diff: {err}") from err

        summary, total_tokens = PiOutput(out_dir).read()

        return Result(
            patch=patch,
            summary=summary,
            total_tokens=total_tokens,
            changed_files=GitStatus(repo_dir).changed_files(),
            repo_dir=repo_dir,
            out_dir=out_dir,
        )


def run(req: RunRequest, timeout: float | None = None) -> Result:
    """Clone the repo if needed, run the Pi container, and return the patch.

    timeout is the deadline in seconds for the whole run, covering the clone and
    the container. When it expires the container is killed, which ends init
    scripts and Pi.
    """
    return Runner(req).run(timeout=timeout)
