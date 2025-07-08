"""
use the create_stream() method to create a chat completion request with streaming token chunks.
"""

import asyncio
import os
from autogen_core.models import CreateResult, UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient


model_client = OpenAIChatCompletionClient(
    model="gemini-1.5-flash-8b",  # gpt-4o
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3
)  # assuming OPENAI_API_KEY is set in the environment.

messages = [
    UserMessage(content="Write a very short story about a dragon.", source="user"),
]

# Create a stream.
stream = model_client.create_stream(messages=messages)

async def main() -> None:
    # Iterate over the stream and print the responses.
    print("Streamed responses:")
    async for chunk in stream:  # type: ignore
        if isinstance(chunk, str):
            # The chunk is a string.
            print(chunk, flush=True, end="")
        else:
            # The final chunk is a CreateResult object.
            assert isinstance(chunk, CreateResult) and isinstance(chunk.content, str)
            # The last response is a CreateResult object with the complete message.
            print("\n\n------------\n")
            print("The complete response:", flush=True)
            print(chunk.content, flush=True)

asyncio.run(main())

