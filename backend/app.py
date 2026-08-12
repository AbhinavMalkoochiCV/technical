import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend._chatbot import ScriptedChatbot
from backend.agent import Agent
from backend.tools import list_files, read_file

app = FastAPI()
agent = Agent(ScriptedChatbot())
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1)


@app.get("/api/files")
def files() -> list[str]:
    return list_files()


@app.get("/api/files/{path}")
def file(path: str) -> dict[str, str]:
    try:
        return {"content": read_file(path)}
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(404, "File not found") from error


@app.post("/api/chat")
def chat(request: ChatRequest) -> dict[str, str]:
    try:
        return {"answer": agent.chat(request.session_id, request.message)}
    except Exception as error:
        logger.exception("Agent request failed")
        raise HTTPException(502, "MiniCoder is unavailable. Try again.") from error
