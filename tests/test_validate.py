# Copyright 2026 Ferir. All rights reserved.
# License can be found in the LICENSE file.

import pytest

from ferir import Container, FerirError, RunRequest, validate


def valid_run_request() -> RunRequest:
    return RunRequest(
        work_dir="/tmp/basement",
        id="job-1",
        repo_url="https://github.com/example/repo.git",
        prompt="do something",
        pi_model="openrouter/anthropic/claude-sonnet-4.5",
        proxy_url="https://openrouter.ai/api/v1",
        docker_image="ferir-pi:local",
        container=Container(memory="2g", cpus="1"),
    )


def test_valid_request() -> None:
    validate(valid_run_request())


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("repo_url", "", "Repository URL is required"),
        ("prompt", "  ", "Prompt is required"),
        ("pi_model", "", "PI Model is required"),
        ("id", "", "ID is required"),
        ("proxy_url", "  ", "ProxyURL is required"),
        ("docker_image", "", "Docker Image is required"),
    ],
)
def test_missing_field(field: str, value: str, message: str) -> None:
    req = valid_run_request()
    setattr(req, field, value)

    with pytest.raises(FerirError, match=message):
        validate(req)


def test_missing_container_limits() -> None:
    req = valid_run_request()
    req.container.memory = ""

    with pytest.raises(FerirError, match="Container.Memory is required"):
        validate(req)
