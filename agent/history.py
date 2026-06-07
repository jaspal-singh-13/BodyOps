from pydantic_ai.messages import ModelMessage

_sessions: dict[str, list[ModelMessage]] = {}


def get_session(session_id: str) -> list[ModelMessage]:
    return _sessions.get(session_id, [])


def update_session(session_id: str, new_messages: list[ModelMessage]) -> None:
    existing = _sessions.setdefault(session_id, [])
    existing.extend(new_messages)


def clear_all_sessions() -> None:
    _sessions.clear()
