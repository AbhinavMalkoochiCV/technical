from typing import NoReturn

import pytest
from fastapi import HTTPException

from backend import app


class BrokenAgent:
    def chat(self, session_id: str, message: str) -> NoReturn:
        raise RuntimeError("provider payload " * 1000)


def test_error_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app, "agent", BrokenAgent())
    with pytest.raises(HTTPException) as caught:
        app.chat(app.ChatRequest(session_id="abc", message="hello"))
    assert caught.value.status_code == 502
    assert caught.value.detail == "MiniCoder is unavailable. Try again."
