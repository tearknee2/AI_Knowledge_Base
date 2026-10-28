
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.services.llm_service import LLMServiceError

client = TestClient(app)


def test_llm_failure_returns_502():
    with patch(
        "app.main.answer_question",
        new_callable=AsyncMock,
    ) as mock_answer:

        mock_answer.side_effect = LLMServiceError(
            "模拟的大模型服务异常"
        )

        response = client.post(
            "/knowledge-bases/12/chat",
            json={
                "question": "测试大模型调用失败",
            },
        )

    print("HTTP 状态码：", response.status_code)
    print("响应内容：", response.json())

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "大模型服务暂时无法正常处理请求"
    )

    print("PASS：大模型异常被正确转换为 HTTP 502")


def test_unexpected_error_returns_500():
    with patch(
        "app.main.answer_question",
        new_callable=AsyncMock,
    ) as mock_answer:

        mock_answer.side_effect = ValueError(
            "模拟的内部异常"
        )

        response = client.post(
            "/knowledge-bases/12/chat",
            json={
                "question": "测试内部异常",
            },
        )

    print("HTTP 状态码：", response.status_code)
    print("响应内容：", response.json())

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "知识库问答失败"
    )

    print("PASS：意外异常被正确转换为 HTTP 500")


if __name__ == "__main__":
    test_llm_failure_returns_502()
