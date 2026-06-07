"""
Central LLM model factory.

To swap the provider (e.g. from Azure OpenAI to Anthropic), edit only this
file — all other agent code imports ``get_model()`` and is unaffected.

Required environment variables:
    AZURE_OPENAI_API_KEY      — Azure OpenAI resource key.
    AZURE_OPENAI_ENDPOINT     — Resource endpoint, e.g. https://<name>.openai.azure.com.
    AZURE_OPENAI_DEPLOYMENT   — Deployment name (model alias), e.g. ``gpt-4o``.
    AZURE_OPENAI_API_VERSION  — (optional) API version; defaults to ``2024-08-01-preview``.
"""

import os

from openai import AsyncAzureOpenAI
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider


def get_model() -> OpenAIChatModel:
    """
    Build and return a configured ``OpenAIChatModel`` backed by Azure OpenAI.

    Creates a new ``AsyncAzureOpenAI`` client from environment variables,
    wraps it in an ``OpenAIProvider``, and returns an ``OpenAIChatModel``
    pointed at the configured deployment.

    Returns:
        A ready-to-use ``OpenAIChatModel`` instance.

    Raises:
        KeyError: If any required environment variable is missing.
    """
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
