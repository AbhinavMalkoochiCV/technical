from collections.abc import Iterable
from typing import Any

import pytest

from backend import tools
from backend.agent import Agent, Reply, ToolCall


class FakeChatbot:
    def __init__(self, replies: Iterable[Reply]) -> None:
        self.replies = iter(replies)
        self.inputs: list[list[Any]] = []

    def complete(self, messages: list[Any]) -> Reply:
        self.inputs.append(messages.copy())
        return next(self.replies)


def test_conversation_history_is_in_order() -> None:
    chatbot = FakeChatbot([Reply("First", []), Reply("Second", [])])
    agent = Agent(chatbot)
    agent.chat("abc", "Explain pricing.py")
    agent.chat("abc", "Modify that function")
    users = [item["content"] for item in chatbot.inputs[1] if item.get("role") == "user"]
    assert users == ["Explain pricing.py", "Modify that function"]


def test_list_files_dispatch(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tools, "ROOT", tmp_path)
    (tmp_path / "pricing.py").write_text("price = 1")
    assert tools.run_tool("list_files", {}) == "pricing.py"


def test_write_tool_dispatches_content(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tools, "ROOT", tmp_path)
    result = tools.run_tool("write_file", {"path": "pricing.py", "content": "value = 1"})
    assert result == "Wrote pricing.py"
    assert (tmp_path / "pricing.py").read_text() == "value = 1"


def test_all_tool_results_reach_chatbot(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tools, "ROOT", tmp_path)
    (tmp_path / "auth.py").write_text("def session_duration(): return TOKEN_EXPIRY_MINUTES")
    (tmp_path / "config.py").write_text("TOKEN_EXPIRY_MINUTES = 30")
    chatbot = FakeChatbot([
        Reply("", [
            ToolCall("1", "read_file", {"path": "auth.py"}),
            ToolCall("2", "read_file", {"path": "config.py"}),
        ]),
        Reply("Done", []),
    ])
    Agent(chatbot).chat("abc", "Explain auth.py and config.py")
    outputs = [item["output"] for item in chatbot.inputs[1] if item.get("type") == "function_call_output"]
    assert outputs == [
        "def session_duration(): return TOKEN_EXPIRY_MINUTES",
        "TOKEN_EXPIRY_MINUTES = 30",
    ]


def test_delete_file_tool(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tools, "ROOT", tmp_path)
    path = tmp_path / "old.py"
    path.write_text("old = True")
    assert any(tool["name"] == "delete_file" for tool in tools.TOOLS)
    assert tools.run_tool("delete_file", {"path": "old.py"}) == "Deleted old.py"
    assert not path.exists()
