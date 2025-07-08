import asyncio
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# from autogen_core.models import UserMessage
# from autogen_ext.models.openai import OpenAIChatCompletionClient

# model_client = OpenAIChatCompletionClient(
#     model="gemini-1.5-flash-8b",
#     # api_key="GEMINI_API_KEY",
# )

# response = await model_client.create([UserMessage(content="What is the capital of France?", source="user")])
# print(response)
# await model_client.close()


async def main() -> None:
    agent = AssistantAgent("assistant", OpenAIChatCompletionClient(
        model="gemini-1.5-flash-8b",  # gpt-4o
        api_key=os.getenv("GEMINI_API_KEY"),
    ))
    print(await agent.run(task="Say 'Hello World!'"))

asyncio.run(main())
