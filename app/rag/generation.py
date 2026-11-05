from app.services.llm_service import chat_with_llm

def build_context(chunks: list[str]) -> str:
    """将检索到的文本块拼接为模型可读的上下文"""
    return "\n\n".join(chunks)

async def generate_answer(
    query:str,
    context:str,
    history_messages:list[dict]
) -> str:
    """根据用户问题和检索到的知识生成答案"""

    messages = (
        [
            {
                "role": "system",
                "content": """你是公司的一名知识库助手。
        请严格依据提供的知识回答问题，不要使用外部知识或自行推测。
        如果知识中没有足够的信息回答，请明确说明：知识库中没有相关信息。
        不要编造公司制度中不存在的规定。""",
            }
        ] +
        history_messages +
        [
            {
                "role": "user",
                "content": f"""以下是从知识库检索到的知识：
        {context}
    
        用户问题：
        {query}""",
            },
        ]
    )

    assistant_message = await chat_with_llm(messages)

    answer = assistant_message.get("content")

    if not isinstance(answer, str) or not answer.strip():
        raise RuntimeError("大模型未返回有效答案")

    return answer.strip()