from enum import Enum


class OpenAiGenerativeModelName(str, Enum):
    """An enum of OpenAI generative model names."""

    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_TURBO = "gpt-4-turbo"
