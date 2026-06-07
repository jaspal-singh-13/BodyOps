from datetime import date

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel

from .deps import AgentDeps
from .llm import get_model

SYSTEM_PROMPT = """You are the BodyOps AI coach. Help the user track their fitness journey.
Use tools to get real data before giving advice. Be encouraging and specific.
Today is {today}."""


def build_agent() -> Agent[AgentDeps, str]:  # type: ignore[type-arg]
    a: Agent[AgentDeps, str] = Agent(
        get_model(),
        system_prompt=SYSTEM_PROMPT.format(today=date.today().isoformat()),
        deps_type=AgentDeps,
    )
    return a


agent = build_agent()
