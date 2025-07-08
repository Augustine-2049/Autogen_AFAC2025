import asyncio
import os
import logging

from autogen_core import EVENT_LOGGER_NAME
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(EVENT_LOGGER_NAME)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)




# model_client = OpenAIChatCompletionClient(
#     model="gemini-1.5-flash-8b",
#     api_key=os.getenv("GEMINI_API_KEY") or "",
# )

# response = model_client.create([UserMessage(content="What is the capital of France?", source="user")])
# print(response)
# await model_client.close()


async def main() -> None:
    # 创建一个 AssistantAgent 实例，名字为 "assistant"，使用 OpenAIChatCompletionClient 作为大模型后端
    agent = AssistantAgent(
        "assistant",  # Agent 名称
        OpenAIChatCompletionClient(
            model="gemini-1.5-flash-8b",  # 指定使用的模型（如 Gemini、GPT-4o 等）
            api_key=os.getenv("GEMINI_API_KEY"),  # 从环境变量获取 API KEY
        )
    )
    # 运行 agent，传入任务描述，异步等待结果并打印
    print(await agent.run(task="Say 'Hello World!'"))

# 启动异步主程序
asyncio.run(main())