"""
In-memory conversation history store.

Keeps ``ModelMessage`` lists keyed by ``session_id`` for the lifetime of the
FastAPI process. Each call to ``agent.run_stream()`` passes the stored messages
as ``message_history`` so the agent has full context across multiple turns.

Limitations:
    - History is lost on process restart (HF Spaces sleeps after 48 h inactivity).
    - No per-user isolation beyond the ``session_id`` the client generates.
    - Flushing to the Chat History Sheet is deferred to a future phase.
"""

from pydantic_ai.messages import ModelMessage

_sessions: dict[str, list[ModelMessage]] = {}


def get_session(session_id: str) -> list[ModelMessage]:
    """
    Return the stored message history for a session.

    Args:
        session_id: Client-generated UUID identifying the chat session.

    Returns:
        List of ``ModelMessage`` objects for the session, or an empty list if
        the session has not been seen before.
    """
    return _sessions.get(session_id, [])


def update_session(session_id: str, new_messages: list[ModelMessage]) -> None:
    """
    Append new messages to an existing session, creating it if necessary.

    Called after each ``agent.run_stream()`` completes with
    ``result.new_messages()`` so subsequent turns carry full context.

    Args:
        session_id: Client-generated UUID identifying the chat session.
        new_messages: Messages returned by ``result.new_messages()`` from the
            most recent agent run.
    """
    existing = _sessions.setdefault(session_id, [])
    existing.extend(new_messages)


def clear_all_sessions() -> None:
    """
    Wipe all in-memory session history.

    Called by ``DELETE /agent/history``. Does not flush to the Chat History
    Sheet — that is handled separately by the API router.
    """
    _sessions.clear()
