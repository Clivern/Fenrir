# Copyright 2026 Fenrir. All rights reserved.
# License can be found in the LICENSE file.

"""Five concurrent agent runs against github.com/Clivern/Diffsay.

Run:

    uv run python examples/example1.py
"""

from __future__ import annotations

import itertools
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

import fenrir

REPO_URL = "https://github.com/Clivern/Diffsay.git"
DOCKER_IMAGE = "clivern/fenrir:v0.1.0"
TIMEOUT = 2 * 60 * 60

TASKS = [
    """Add "Gemfile.lock" to LOW_PRIORITY_FILES in src/diffsay/const.py if missing.
Only edit that file.""",
    """Add "Poetry.lock" to LOW_PRIORITY_FILES in src/diffsay/const.py if missing.
Only edit that file.""",
    """In tests/test_cli.py add function test_uv_lock_in_low_priority_files:
import LOW_PRIORITY_FILES from diffsay.const and assert "uv.lock" in LOW_PRIORITY_FILES.
Only edit tests/test_cli.py.""",
    """Add a one-sentence docstring to the module at the top of src/diffsay/const.py
explaining LOW_PRIORITY_FILES.""",
    """In README.md under ### Develop add this line immediately after the heading (before the code block):
"Use uv to sync dependencies and run checks."
Do not skip; README must change even if pytest is mentioned in the code block below.""",
]


@dataclass
class TaskOutcome:
    n: int
    id: str
    result: fenrir.Result | None
    error: Exception | None


class Progress:
    """Spinner showing how many tasks are running, done, failed, and pending."""

    FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

    def __init__(self, total: int) -> None:
        self.lock = threading.Lock()
        self.total = total
        self.in_flight = 0
        self.ok = 0
        self.failed = 0
        self.stopping = threading.Event()
        self.thread = threading.Thread(target=self._spin, daemon=True)

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> None:
        self.stopping.set()
        self.thread.join()
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()

    def start_task(self) -> None:
        with self.lock:
            self.in_flight += 1

    def finish_task(self, ok: bool) -> None:
        with self.lock:
            self.in_flight -= 1
            if ok:
                self.ok += 1
            else:
                self.failed += 1

    def _spin(self) -> None:
        for frame in itertools.cycle(self.FRAMES):
            if self.stopping.is_set():
                return
            with self.lock:
                pending = self.total - self.in_flight - self.ok - self.failed
                suffix = (
                    f"{self.in_flight} running · {self.ok} done "
                    f"· {self.failed} failed · {pending} pending"
                )
            sys.stdout.write(f"\r\033[K{frame} {suffix}")
            sys.stdout.flush()
            time.sleep(0.1)


def main() -> int:
    progress = Progress(len(TASKS))
    progress.start()

    def run_task(n: int, prompt: str) -> TaskOutcome:
        id = str(uuid.uuid4())
        progress.start_task()
        try:
            result = fenrir.run(
                fenrir.RunRequest(
                    work_dir="/tmp/basement",
                    id=id,
                    repo_url=REPO_URL,
                    prompt=prompt,
                    pi_model="openrouter/anthropic/claude-sonnet-4.5",
                    proxy_url="http://host.docker.internal:8080/api",
                    docker_image=DOCKER_IMAGE,
                    container=fenrir.Container(memory="2g", cpus="1"),
                    cleanup=True,
                ),
                timeout=TIMEOUT,
            )
        except Exception as err:  # noqa: BLE001 - report every task, keep the others running
            progress.finish_task(ok=False)
            return TaskOutcome(n=n, id=id, result=None, error=err)

        progress.finish_task(ok=True)
        return TaskOutcome(n=n, id=id, result=result, error=None)

    with ThreadPoolExecutor(max_workers=len(TASKS)) as pool:
        outcomes = list(pool.map(run_task, itertools.count(1), TASKS))

    progress.stop()
    outcomes.sort(key=lambda o: o.n)

    failed = 0
    for outcome in outcomes:
        if outcome.error is not None:
            failed += 1
            print(f"[task {outcome.n}] id={outcome.id} error: {outcome.error}")
            continue
        print_task_result(outcome.n, outcome.id, outcome.result)

    if failed:
        print(f"\n{failed} of {len(TASKS)} tasks failed")
        return 1

    print("all tasks finished")
    return 0


def print_task_result(n: int, id: str, result: fenrir.Result) -> None:
    bar = "=" * 72
    print(f"\n{bar}\n[task {n}] id={id}\nout: {result.out_dir}\n{bar}")
    print("--- summary ---")
    print(result.summary.strip())
    print(f"total_tokens={result.total_tokens}")
    print("--- changed files ---")
    if not result.changed_files:
        print("(none)")
    else:
        for file in result.changed_files:
            print(f"{file.status}\t{file.path} ({len(file.content)} bytes)")
            print(file.content.strip() or "(no content)")
            print()
    print("--- patch ---")
    print(result.patch.strip() or "(empty)")


if __name__ == "__main__":
    raise SystemExit(main())
