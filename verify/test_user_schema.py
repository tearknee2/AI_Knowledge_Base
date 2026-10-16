# test_user_schema.py
from pydantic import ValidationError
from app.schemas.user import UserCreate
from datetime import datetime
from app.schemas.user import UserResponse

# 测试1：正常数据
user = UserCreate(
    username="alice",
    password="password123"
)

print("测试1：正常数据")
print(user)

# 测试2：用户名太短
try:
    UserCreate(
        username="ab",
        password="password123"
    )
except ValidationError as e:
    print("\n测试2：用户名太短")
    print(e)

# 测试3：密码太短
try:
    UserCreate(
        username='alice',
        password='123'
    )
except ValidationError as e:
    print("\n测试3：密码太短")
    print(e)

response = UserResponse(
    id=1,
    username="alice",
    password_hash="some-hash-value",
    created_at=datetime.now()
)
print("\n测试4：用户响应")
print(response,type(response))
print(response.model_dump())
print("响应字段:",response.model_dump().keys())

class FakeUser:
    def __init__(self):
        self.id = 2
        self.username = "alice"
        self.created_at = datetime.now()
        self.password_hash = "fake-hash"

fake_user = FakeUser()

response_from_object = UserResponse.model_validate(fake_user)
# model_validate() 是 Pydantic v2 的数据校验与模型创建方法

print("\n测试5：从对象转换响应Schema")
print(response_from_object)
print(response_from_object.model_dump())


# 测试6：额外传入user_id数据
try:
    user = UserCreate(
    username="alice",
    password="password123",
    user_id=1
    )
except ValidationError as e:
    print("测试6通过：额外字段被拒绝")
    print(e)
else:
    print("测试6失败：额外字段没有被拒绝")
