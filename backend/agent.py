from dataclasses import dataclass
from typing import Any, Protocol

from backend.tools import run_tool

Message = dict[str, Any]
SYSTEM: Message = {
    "role": "developer",
    "content": "You are MiniCoder, a coding chatbot for the workspace.",
}


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class Reply:
    text: str
    calls: list[ToolCall]


class Completer(Protocol):
    def complete(self, messages: list[Any]) -> Reply: ...


class Agent:
    def __init__(self, chatbot: Completer) -> None:
        self.chatbot = chatbot
        self.sessions: dict[str, list[Message]] = {}

    def chat(self, session_id: str, user_message: str) -> str:
        history = self.sessions.setdefault(session_id, [])
        messages: list[Any] = [SYSTEM, {"role": "user", "content": user_message}]
        for _ in range(4):
            reply = self.chatbot.complete(messages)
            if not reply.calls:
                history.extend([
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": reply.text},
                ])
                return reply.text

            messages.extend({
                "type": "function_call",
                "call_id": call.id,
                "name": call.name,
                "arguments": call.arguments,
            } for call in reply.calls)
            tool_results = [
                {
                    "type": "function_call_output",
                    "call_id": call.id,
                    "output": run_tool(call.name, call.arguments),
                }
                for call in reply.calls
            ]
            messages.append(tool_results[-1])
        return "Stopped after four steps."
