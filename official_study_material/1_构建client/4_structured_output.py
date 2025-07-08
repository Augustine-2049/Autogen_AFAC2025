"""
Structured output can be enabled by setting the response_format field 
in OpenAIChatCompletionClient and AzureOpenAIChatCompletionClient 
to as a Pydantic BaseModel class.
"""

import asyncio
import os
from typing import Literal

from pydantic import BaseModel
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import UserMessage

# The response format for the agent as a Pydantic base model.
class AgentResponse(BaseModel):
    thoughts: str
    response: Literal["happy", "sad", "neutral"]  # 只能回复这三个值


# Create an agent that uses the OpenAI GPT-4o model with the custom response format.
model_client = OpenAIChatCompletionClient(
    model="gemini-1.5-flash-8b",
    api_key=os.getenv("GEMINI_API_KEY"),
    response_format=AgentResponse,  # type: ignore
)

# Send a message list to the model and await the response.
messages = [
    UserMessage(content="I am happy.", source="user"),
]
async def main() -> None:
    response = await model_client.create(messages=messages)
    print(response)
    assert isinstance(response.content, str)
    parsed_response = AgentResponse.model_validate_json(response.content)
    print(parsed_response.thoughts)
    print(parsed_response.response)

    # Close the connection to the model client.
    await model_client.close()
asyncio.run(main())







