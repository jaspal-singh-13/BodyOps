"""
Pydantic AI agent definition for BodyOps.

This module creates the singleton ``agent`` instance used across the app.
Tools are registered in ``tools.py`` by importing that module after this one;
the ``@agent.tool`` decorator wires them in at import time.

The system prompt is supplied as a per-run instructions callable so today's
date is re-evaluated on every chat request — a long-running server process
never serves a stale date (which previously caused chat-logged weights to be
written under the server's startup date).
"""

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel

from .deps import AgentDeps
from .llm import get_model
from .prompts import get_system_prompt


def build_agent() -> Agent[AgentDeps, str]:  # type: ignore[type-arg]
    """
    Construct and return the Pydantic AI ``Agent`` instance.

    Passes ``get_system_prompt`` as a callable so it is evaluated on every
    run, keeping the injected "Today is ..." date current. Binds ``AgentDeps``
    as the dependency type so all tool functions receive a typed
    ``RunContext[AgentDeps]``.

    Returns:
        A configured ``Agent[AgentDeps, str]`` ready to have tools registered
        against it via ``@agent.tool``.
    """
    a: Agent[AgentDeps, str] = Agent(
        get_model(),
        instructions=get_system_prompt,
        deps_type=AgentDeps,
    )
    return a


agent = build_agent()
