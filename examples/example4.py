# Copyright 2026 Fenrir. All rights reserved.
# License can be found in the LICENSE file.

"""The timeout stops a long init script.

Init sleeps for 10 minutes. The timeout is 90 seconds and includes the clone.
A passing run prints "init sleep start", then raises before the sleep finishes.

Prerequisites:
  - clivern/fenrir:v0.1.0 already pulled

Run:

    uv run python examples/example4.py
"""

from __future__ import annotations

import subprocess
import sys
import time
import uuid

import fenrir

REPO_URL = "https://github.com/octocat/Hello-World.git"
TIMEOUT = 90.0
SLEEP_FOR = 10 * 60.0

INIT_BASH = """
echo "init sleep start" >&2
sleep 600
echo "init sleep done" >&2
"""


def main() -> int:
    id = str(uuid.uuid4())
    print(f"job id={id}\ntimeout={TIMEOUT:.0f}s init sleep={SLEEP_FOR:.0f}s")

    start = time.monotonic()
    try:
        fenrir.run(
            fenrir.RunRequest(
                work_dir="/tmp/basement",
                id=id,
                repo_url=REPO_URL,
                prompt="Do not edit files. The init script should be killed before you start.",
                pi_model="openrouter/anthropic/claude-sonnet-4.5",
                proxy_url="http://host.docker.internal:8080/api",
                docker_image="clivern/fenrir:v0.1.0",
                container=fenrir.Container(init_bash=INIT_BASH, memory="2g", cpus="1"),
                cleanup=True,
            ),
            timeout=TIMEOUT,
        )
    except fenrir.FenrirError as err:
        elapsed = time.monotonic() - start
        return report(id, elapsed, err)

    elapsed = time.monotonic() - start
    print(f"expected the timeout to stop the run after {elapsed:.0f}s", file=sys.stderr)
    return 1


def report(id: str, elapsed: float, err: fenrir.FenrirError) -> int:
    if "init sleep start" not in str(err):
        print(f"timeout fired before init started ({elapsed:.0f}s): {err}", file=sys.stderr)
        return 1
    if elapsed >= SLEEP_FOR:
        print(f"waited for the full init sleep ({elapsed:.0f}s): {err}", file=sys.stderr)
        return 1
    if not container_gone(id):
        print(f"container {id} still exists after {elapsed:.0f}s: {err}", file=sys.stderr)
        return 1

    print(f"init sleep killed after {elapsed:.0f}s")
    print(f"error: {err}")
    return 0


def container_gone(id: str) -> bool:
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        gone = subprocess.run(
            ["docker", "inspect", id],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if gone.returncode != 0:
            return True
        time.sleep(0.5)
    return False


if __name__ == "__main__":
    raise SystemExit(main())
