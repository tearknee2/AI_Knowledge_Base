import json
import httpx
from app.core.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL
)


class LLMServiceError(RuntimeError):
    """大模型服务调用或响应异常"""
    pass

async def chat_with_llm(messages: list[dict]) -> dict:
    """调用Deepseek，返回assistant消息"""

    if not DEEPSEEK_API_KEY:
        raise LLMServiceError('未配置DEEPSEEK_API_KEY')

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
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

    except httpx.TimeoutException as exc:
        raise LLMServiceError("大模型服务请求超时") from exc

    except httpx.HTTPStatusError as exc:
        raise LLMServiceError("大模型服务返回错误状态码") from exc

    except httpx.RequestError as exc:
        raise LLMServiceError("无法连接大模型服务") from exc

    try:
        data = response.json()
        message = data["choices"][0]["message"]
        if (
                not isinstance(message, dict)
                or message.get("role") != "assistant"
                or not isinstance(message.get('content'), str)
                or not message.get('content').strip()
        ):

            raise LLMServiceError("返回的文本为空或者格式不正确")
    except json.JSONDecodeError as exc:
        raise LLMServiceError("响应体不是合法JSON") from exc
    except (KeyError,IndexError,TypeError) as exc:
        raise LLMServiceError("响应体有问题") from exc


    return {
        "role": message["role"],
        "content": message["content"],
    }
