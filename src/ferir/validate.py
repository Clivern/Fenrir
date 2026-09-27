# Copyright 2026 Ferir. All rights reserved.
# License can be found in the LICENSE file.

from __future__ import annotations

from .types import FerirError, RunRequest


class RequestValidator:
    """Checks that a RunRequest carries every field a run needs."""

    def __init__(self, req: RunRequest) -> None:
        self.req = req

    def validate(self) -> None:
        for name, value in self._required():
            if not value.strip():
                raise FerirError(f"{name} is required")

    def _required(self) -> list[tuple[str, str]]:
        req = self.req
        return [
            ("Repository URL", req.repo_url),
            ("Prompt", req.prompt),
            ("PI Model", req.pi_model),
            ("ID", req.id),
            ("ProxyURL", req.proxy_url),
            ("Docker Image", req.docker_image),
            ("Container.Memory", req.container.memory),
            ("Container.CPUs", req.container.cpus),
        ]


def validate(req: RunRequest) -> None:
    RequestValidator(req).validate()
