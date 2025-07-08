import asyncio
import os
from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(
    model="gemini-1.5-flash-8b",  # gpt-4o
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3
)  # assuming OPENAI_API_KEY is set in the environment.


async def main() -> None:
    # use create() to call model client
    # async to wait result
    result = await model_client.create([UserMessage(content="What is the capital of France?", source="user")])
    print(result)

asyncio.run(main())

