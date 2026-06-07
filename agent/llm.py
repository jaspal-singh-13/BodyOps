"""Central LLM model factory. Edit this file to swap providers."""
import os

from openai import AsyncAzureOpenAI
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider


def get_model() -> OpenAIChatModel:
    client = AsyncAzureOpenAI(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
    )
    provider = OpenAIProvider(openai_client=client)
    return OpenAIChatModel(
        os.environ["AZURE_OPENAI_DEPLOYMENT"],
        provider=provider,
    )
