# Copyright 2026 Fenrir. All rights reserved.
# License can be found in the LICENSE file.

"""Read-only codebase question against github.com/Clivern/Ziee (PR triage audit).

Run:

    uv run python examples/example2.py
"""

from __future__ import annotations

import sys
import uuid

import fenrir

ZIEE_REPO = "https://github.com/Clivern/Ziee.git"
PROMPT = "Does the PR triage functionality is done?"
TIMEOUT = 90 * 60


def main() -> int:
    id = str(uuid.uuid4())
    print(f"job id={id}\ncloning {ZIEE_REPO} …")

    try:
        result = fenrir.run(
            fenrir.RunRequest(
                work_dir="/tmp/basement",
                id=id,
                repo_url=ZIEE_REPO,
                prompt=PROMPT,
                pi_model="openrouter/anthropic/claude-sonnet-4.5",
                proxy_url="http://host.docker.internal:8080/api",
                docker_image="clivern/fenrir:v0.1.0",
                container=fenrir.Container(memory="2g", cpus="1"),
                cleanup=True,
            ),
            timeout=TIMEOUT,
        )
    except fenrir.FenrirError as err:
        print(f"run failed: {err}", file=sys.stderr)
        return 1

    print("=" * 72)
    print("--- answer (result.summary) ---")
    print(result.summary.strip())
    print(f"total_tokens={result.total_tokens}")

    if result.patch.strip() or result.changed_files:
        print("\nwarning: agent modified the tree")
        print(f"changed_files={len(result.changed_files)} patch_bytes={len(result.patch)}")
    else:
        print("\n(no repo changes)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
