# Copyright 2026 Fenrir. All rights reserved.
# License can be found in the LICENSE file.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .types import FenrirError


class PiOutput:
    """The pi.jsonl event stream Pi writes to the out directory."""

    def __init__(self, out_dir: str) -> None:
        self.out_dir = out_dir

    def read(self) -> tuple[str, int]:
        """Return the assistant summary and total token count."""
        path = Path(self.out_dir, "pi.jsonl")

        try:
            raw = path.read_text(errors="replace")
        except OSError as err:
            raise FenrirError(f"read pi.jsonl: {err}") from err

        assistant: list[str] = []
        total_tokens = 0

        for event in self._events(raw):
            if event.get("type") == "message_update":
                usage = event.get("usage")
                if isinstance(usage, dict) and isinstance(usage.get("totalTokens"), int):
                    total_tokens = usage["totalTokens"]
            elif event.get("type") == "message_end":
                text = self.assistant_text(event.get("message"))
                if text:
                    assistant.append(text)

        return "\n\n".join(assistant).strip(), total_tokens

    @staticmethod
    def _events(raw: str) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []

        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue

            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict):
                events.append(event)

        return events

    @staticmethod
    def assistant_text(message: Any) -> str:
        """Return the text of an assistant message, whose content is a string or text blocks."""
        if not isinstance(message, dict):
            return ""

        role = message.get("role", "")
        if role and role != "assistant":
            return ""

        content = message.get("content")
        if isinstance(content, str):
            return content.strip()
        if not isinstance(content, list):
            return ""

        blocks = [block.get("text", "") for block in content if isinstance(block, dict)]
        return "\n".join(text for text in blocks if text).strip()


def read_out(out_dir: str) -> tuple[str, int]:
    """Return the assistant summary and total token count from pi.jsonl."""
    return PiOutput(out_dir).read()


def assistant_text(message: Any) -> str:
    """Return the text of an assistant message, whose content is a string or text blocks."""
    return PiOutput.assistant_text(message)
