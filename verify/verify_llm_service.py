
import asyncio

from app.services.llm_service import chat_with_llm


async def main():
    messages = [
        {
            "role": "user",
            "content": "请用一句话解释什么是 Python。",
        }
    ]

    result = await chat_with_llm(messages)

    print("角色：", result["role"])
    print("回答：", result["content"])


if __name__ == "__main__":
    asyncio.run(main())
