"""Private deterministic harness used to run the assessment without AI."""

import re
from typing import Any

from backend.agent import Reply, ToolCall


def python_paths(text: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"\b[\w.-]+\.py\b", text.lower())))


class ScriptedChatbot:
    def complete(self, messages: list[Any]) -> Reply:
        users = [item for item in messages if isinstance(item, dict) and item.get("role") == "user"]
        prompt = str(users[-1]["content"]).lower()
        context = "\n".join(str(item["content"]) for item in users).lower()
        paths = python_paths(context)
        outputs = [
            str(item["output"])
            for item in messages
            if isinstance(item, dict) and item.get("type") == "function_call_output"
        ]

        if not paths and any(word in prompt for word in ("that function", "the function", "rounding", "rouding")):
            return Reply("Which file or function do you mean?", [])
        if outputs and outputs[-1].startswith("Wrote "):
            return Reply(f"Updated `{paths[0]}`.", [])

        listing = "list" in prompt and "file" in prompt
        if outputs and listing:
            return Reply(outputs[-1], [])

        editing = any(word in prompt for word in ("change", "modify", "update", "set"))
        if outputs and editing:
            content = outputs[0]
            if "decimal" in prompt or "round" in prompt or "roud" in prompt:
                content = re.sub(
                    r"(?m)^(\s*)return (?!round\()(.+)$",
                    r"\1return round(\2, 2)",
                    content,
                    count=1,
                )
            elif "default_markup" in prompt:
                value = re.search(r"\b0\.\d+\b", prompt)
                if value:
                    content = re.sub(
                        r"(?m)^DEFAULT_MARKUP\s*=.*$",
                        f"DEFAULT_MARKUP = {value.group()}",
                        content,
                    )
            return Reply("", [ToolCall("write-1", "write_file", {"path": paths[0], "content": content})])

        if not outputs and listing:
            return Reply("", [ToolCall("list-1", "list_files", {})])
        if not outputs and paths:
            if "delete" in prompt:
                return Reply("", [ToolCall("delete-1", "delete_file", {"path": paths[0]})])
            return Reply("", [
                ToolCall(f"read-{index}", "read_file", {"path": path})
                for index, path in enumerate(paths, start=1)
            ])

        if len(paths) == 2:
            if len(outputs) != 2:
                return Reply("I could not read both requested files.", [])
            return Reply(
                "`auth.py` reads `TOKEN_EXPIRY_MINUTES` from `config.py`; sessions last 30 minutes.",
                [],
            )
        if paths == ["pricing.py"] and outputs:
            return Reply("`calculate_price(cost)` adds the 10% `DEFAULT_MARKUP` to the cost.", [])
        return Reply("Ask me to read or edit a workspace Python file.", [])
