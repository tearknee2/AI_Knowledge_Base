import httpx

from app.core.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL
)

async def chat_with_llm(messages: list[dict]) -> dict:
    """调用Deepseek，返回assistant消息"""

    if not DEEPSEEK_API_KEY:
        raise RuntimeError('未配置DEEPSEEK_API_KEY')

    url = f"{DEEPSEEK_BASE_URL.rstrip('/')}/chat/completions"

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "stream": False
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            url,
            headers=headers,
            json=payload,
        )
        response.raise_for_status()

    data = response.json()
    message = data["choices"][0]["message"]

    return {
        "role": message["role"],
        "content": message["content"],
    }
