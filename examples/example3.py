# Copyright 2026 Ferir. All rights reserved.
# License can be found in the LICENSE file.

"""Edit Diffsay and run its tests inside the container.

Init installs Python; Pi then edits const.py and runs pytest.

Prerequisites:
  - clivern/ferir:v0.2.0

Run:

    uv run python examples/example3.py
"""

from __future__ import annotations

import sys
import uuid

import ferir

DIFFSAY_REPO = "https://github.com/Clivern/Diffsay.git"
TIMEOUT = 90 * 60

INIT_BASH = """
apt-get update
apt-get install -y --no-install-recommends python3 python3-pip python3-venv
pip3 install --break-system-packages uv ruff
"""

PROMPT = (
    'Add "Gemfile.lock" to LOW_PRIORITY_FILES in src/diffsay/const.py if missing '
    "and run the tests and provide the full test results"
)


def main() -> int:
    id = str(uuid.uuid4())
    print(f"job id={id}\ncloning {DIFFSAY_REPO} …")

    try:
        result = ferir.run(
            ferir.RunRequest(
                work_dir="/tmp/basement",
                id=id,
                repo_url=DIFFSAY_REPO,
                prompt=PROMPT,
                pi_model="openrouter/anthropic/claude-sonnet-4.5",
                proxy_url="http://host.docker.internal:8080/api",
                docker_image="clivern/ferir:v0.2.0",
                container=ferir.Container(init_bash=INIT_BASH, memory="2g", cpus="1"),
                cleanup=True,
            ),
            timeout=TIMEOUT,
        )
    except ferir.FerirError as err:
        print(f"run failed: {err}", file=sys.stderr)
        return 1

    print("=" * 72)
    print("--- summary ---")
    print(result.summary.strip())
    print(f"total_tokens={result.total_tokens}")
    print("--- changed files ---")
    if not result.changed_files:
        print("(none)")
    else:
        for file in result.changed_files:
            print(f"{file.status}\t{file.path}")
    print("--- patch ---")
    print(result.patch.strip() or "(empty)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
