# Copyright 2026 Ferir. All rights reserved.
# License can be found in the LICENSE file.

from pathlib import Path

from ferir import assistant_text, read_out

JSONL = """{"type":"message_update","usage":{"totalTokens":105}}
{"type":"message_end","message":{"role":"assistant","content":[{"type":"text","text":"Done editing const.py."}]}}
"""


def test_read_out(tmp_path: Path) -> None:
    (tmp_path / "pi.jsonl").write_text(JSONL)

    summary, total = read_out(str(tmp_path))
    assert summary == "Done editing const.py."
    assert total == 105


def test_assistant_text_string_content() -> None:
    assert assistant_text({"role": "assistant", "content": " hi "}) == "hi"


def test_assistant_text_joins_blocks() -> None:
    message = {"content": [{"text": "one"}, {"text": ""}, {"text": "two"}]}
    assert assistant_text(message) == "one\ntwo"


def test_assistant_text_skips_other_roles() -> None:
    assert assistant_text({"role": "user", "content": "hi"}) == ""
