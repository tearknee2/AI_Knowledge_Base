from app.schemas.chat import ChatResponse,ChatRequest
from pydantic import ValidationError

chat_request = ChatRequest(
    conversation_id = 1,
    question = "What is your name?"
)
print(chat_request)


chat_request_1 = ChatRequest(
    question = "What is your name?"
)
print(chat_request_1)

chat_response = ChatResponse(
    conversation_id = 1,
    question = "What is your name?",
    answer = "Hello World"
)
print(chat_response)

chat_request_5 = ChatRequest(
    conversation_id = 1,
    question = "什么是RAG？"
)
print(chat_request_5)

try:
    chat_request_6 = ChatRequest(
        conversation_id = 12,
        question = ""
    )
except ValidationError as e:
    print(e)


try:
    chat_request_3 = ChatRequest(
    question = "What is your name?",
    user_id = 2
    )
except ValidationError as e:
    print("测试3通过：额外字段被拒绝")
    print(e)
else:
    print("测试3失败：额外字段没有被拒绝")