from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent / "workspace"
TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "name": "read_file",
        "description": "Read a file from the workspace",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "write_file",
        "description": "Write a file in the workspace",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "list_files",
        "description": "List workspace files",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        "strict": True,
    },
]


def path_for(name: str) -> Path:
    path = (ROOT / name).resolve()
    if path.parent != ROOT.resolve():
        raise ValueError("Invalid path")
    return path


def read_file(path: str) -> str:
    return path_for(path).read_text()


def write_file(path: str, content: str) -> str:
    path_for(path).write_text(content)
    return f"Wrote {path}"


def list_files() -> list[str]:
    return sorted(path.name for path in ROOT.iterdir() if path.is_file())


def run_tool(name: str, arguments: dict[str, Any]) -> str:
    if name == "read_file":
        return read_file(str(arguments["path"]))
    if name == "write_file":
        return write_file(str(arguments["path"]), str(arguments["content"]))
    if name == "list_file":
        return "\n".join(list_files())
    return f"Unknown tool: {name}"
