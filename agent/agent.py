"""
Pydantic AI agent definition for BodyOps.

This module creates the singleton ``agent`` instance used across the app.
Tools are registered in ``tools.py`` by importing that module after this one;
the ``@agent.tool`` decorator wires them in at import time.

The system prompt is baked in at startup with today's date so the agent always
knows the current date without needing a tool call.
"""

from datetime import date

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel

from .deps import AgentDeps
from .llm import get_model

SYSTEM_PROMPT = """You are the BodyOps AI coach. Help the user track their fitness journey.
Use tools to get real data before giving advice. Be encouraging and specific.
Today is {today}."""


def build_agent() -> Agent[AgentDeps, str]:  # type: ignore[type-arg]
    """
    Construct and return the Pydantic AI ``Agent`` instance.

    Injects today's ISO date into the system prompt and binds ``AgentDeps``
    as the dependency type so all tool functions receive a typed
    ``RunContext[AgentDeps]``.

    Returns:
        A configured ``Agent[AgentDeps, str]`` ready to have tools registered
        against it via ``@agent.tool``.
    """
    a: Agent[AgentDeps, str] = Agent(
        get_model(),
        system_prompt=SYSTEM_PROMPT.format(today=date.today().isoformat()),
        deps_type=AgentDeps,
    )
    return a


agent = build_agent()
