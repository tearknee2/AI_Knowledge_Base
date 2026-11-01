import asyncio
import pytest
from unittest.mock import AsyncMock
from app.rag import generation


def test_generate_answer_returns_answer_and_users_prompt(monkeypatch):
    # 1.创建模拟的大模型调用
    chat_with_llm_mock = AsyncMock(
    return_value={"content":"知识库中没有相关信息"},
    )

    # 2.临时替换真正的大模型调用
    monkeypatch.setattr(
        generation,
        "chat_with_llm",
        chat_with_llm_mock
    )

    # 3.执行被测函数
    result = asyncio.run(
        generation.generate_answer(
            query="星河计划的预算是多少",
            context="项目名称：星河计划。项目代号：XH-7319。"
        )
    )

    # 4.验收最终返回值
    assert result == "知识库中没有相关信息"

    # 5.验收大模型调用次数
    chat_with_llm_mock.assert_awaited_once()

    # 6.取出传给大模型的消息
    messages = chat_with_llm_mock.await_args.args[0]

    # 7.验收系统提示词
    system_prompt = messages[0]["content"]
    assert "严格依据提供的知识回答问题" in system_prompt
    assert "知识库中没有相关信息" in system_prompt

    # 8.验收用户问题和上下文
    user_message = messages[1]["content"]
    assert "星河计划的预算是多少" in user_message
    assert "项目名称：星河计划" in user_message
    assert "项目代号：XH-7319" in user_message


def test_generate_answer_raises_when_content_is_empty(monkeypatch):
    # 1. 模拟大模型返回空字符串
    chat_with_llm_mock = AsyncMock(
        return_value={"content": ""}
    )

    # 2. 临时替换真实的大模型调用
    monkeypatch.setattr(
        generation,
        "chat_with_llm",
        chat_with_llm_mock,
    )

    # 3. TODO：执行 generate_answer()，并检查是否抛出
    # RuntimeError("大模型未返回有效答案")
    with pytest.raises(RuntimeError, match="大模型未返回有效答案"):
        asyncio.run(
            generation.generate_answer(
                query="星河计划的预算是多少",
                context="项目名称：星河计划。项目代号：XH-7319。"
            )
        )



def test_generate_answer_raises_when_content_is_none(monkeypatch):
    # 1. 模拟大模型返回none
    chat_with_llm_mock = AsyncMock(
        return_value={"content": None}
    )

    # 2. 临时替换真实的大模型调用
    monkeypatch.setattr(
        generation,
        "chat_with_llm",
        chat_with_llm_mock,
    )

    # 3. TODO：执行 generate_answer()，并检查是否抛出
    # RuntimeError("大模型未返回有效答案")
    with pytest.raises(RuntimeError, match="大模型未返回有效答案"):
        asyncio.run(
            generation.generate_answer(
                query="星河计划的预算是多少",
                context="项目名称：星河计划。项目代号：XH-7319。"
            )
        )


def test_generate_answer_raises_when_content_is_missing(monkeypatch):
    # 1. 模拟大模型返回空字典
    chat_with_llm_mock = AsyncMock(
        return_value={}
    )

    # 2. 临时替换真实的大模型调用
    monkeypatch.setattr(
        generation,
        "chat_with_llm",
        chat_with_llm_mock,
    )

    # 3. TODO：执行 generate_answer()，并检查是否抛出
    # RuntimeError("大模型未返回有效答案")
    with pytest.raises(RuntimeError, match="大模型未返回有效答案"):
        asyncio.run(
            generation.generate_answer(
                query="星河计划的预算是多少",
                context="项目名称：星河计划。项目代号：XH-7319。"
            )
        )
