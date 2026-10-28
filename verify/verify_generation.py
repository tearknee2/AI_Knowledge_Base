
import asyncio

from app.rag.generation import build_context, generate_answer


async def main():
    chunks = [
        "公司每周五下午举行项目复盘会议。",
        "项目复盘会议由项目负责人主持。",
    ]

    query = "公司什么时候举行项目复盘会议？"

    context = build_context(chunks)

    print("组织后的知识上下文：")
    print(context)

    answer = await generate_answer(query, context)

    print("\n模型回答：")
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())
