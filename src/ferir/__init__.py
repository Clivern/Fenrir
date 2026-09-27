# Copyright 2026 Ferir. All rights reserved.
# License can be found in the LICENSE file.

from .clone import GitClone, clone_auth, ensure_clone
from .core import Runner, run
from .docker import (
    DockerRun,
    InitScripts,
    resolve_repo_init_script,
    run_docker,
    write_init_bash,
)
from .out import PiOutput, assistant_text, read_out
from .status import GitStatus, changed_files_in_repo, file_status_letter
from .types import (
    ChangedFile,
    Container,
    DockerParams,
    FerirError,
    GitCloneAuth,
    Result,
    RunRequest,
)
from .validate import RequestValidator, validate
from .workspace import Workspace, remove_repo_dir, setup_workspace

__version__ = "0.2.0"

__all__ = [
    "ChangedFile",
    "Container",
    "DockerParams",
    "DockerRun",
    "FerirError",
    "GitClone",
    "GitCloneAuth",
    "GitStatus",
    "InitScripts",
    "PiOutput",
    "RequestValidator",
    "Result",
    "RunRequest",
    "Runner",
    "Workspace",
    "assistant_text",
    "changed_files_in_repo",
    "clone_auth",
    "ensure_clone",
    "file_status_letter",
    "read_out",
    "remove_repo_dir",
    "resolve_repo_init_script",
    "run",
    "run_docker",
    "setup_workspace",
    "validate",
    "write_init_bash",
]
