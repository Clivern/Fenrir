#!/usr/bin/env bash
# Copyright 2026 Ferir. All rights reserved.
# License can be found in the LICENSE file.
set -euo pipefail

if [[ -z "${RUN_ID:-}" ]]; then
  echo "RUN_ID is required" >&2
  exit 1
fi
if [[ -z "${PROXY_URL:-}" ]]; then
  echo "PROXY_URL is required" >&2
  exit 1
fi
if [[ -z "${PROMPT:-}" ]]; then
  echo "PROMPT is required" >&2
  exit 1
fi
if [[ -z "${PI_MODEL:-}" ]]; then
  echo "PI_MODEL is required" >&2
  exit 1
fi
if [[ ! -d /repo/.git ]]; then
  echo "/repo must be a mount of a git repository" >&2
  exit 1
fi

if [[ -n "${INIT_SCRIPT:-}" ]]; then
  repo_script="/repo/${INIT_SCRIPT}"
  if [[ ! -f "$repo_script" ]]; then
    echo "INIT_SCRIPT not found: $repo_script" >&2
    exit 1
  fi
  bash "$repo_script"
fi
if [[ -f /out/init.sh ]]; then
  bash /out/init.sh
fi

mkdir -p "${HOME}/.pi/agent"
echo "{\"providers\":{\"openrouter\":{\"baseUrl\":\"${PROXY_URL}\",\"apiKey\":\"\$RUN_ID\"}}}" > "${HOME}/.pi/agent/models.json"
echo "{\"openrouter\":{\"type\":\"api_key\",\"key\":\"${RUN_ID}\"}}" > "${HOME}/.pi/agent/auth.json"

cd /repo
BASE="$(git rev-parse HEAD)"

echo "Running Pi (model=${PI_MODEL}) in /repo ..." >&2
pi -p --model "$PI_MODEL" --no-session --mode json "$PROMPT" > /out/pi.jsonl

DIFF="$(git diff "$BASE")"
if [[ -d /out ]]; then
  printf '%s' "$DIFF" > /out/patch.diff
  echo "Wrote /out/patch.diff and /out/pi.jsonl" >&2
else
  echo "--- patch.diff ---" >&2
  printf '%s' "$DIFF"
fi

if [[ -z "$DIFF" ]]; then
  echo "warning: empty diff (no tracked file changes?)" >&2
fi
