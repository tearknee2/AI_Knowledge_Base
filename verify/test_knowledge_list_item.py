from datetime import datetime

from pydantic import ValidationError
from app.schemas.knowledge_base import KnowledgeListItem

class FakeListItem:
    def __init__(self):
        self.id = 1
        self.user_id = 100 # 模拟ORM对象中的内部字段
        self.name = '数学'
        self.description = '数学是世界上最好的学科'
        self.status = "ACTIVE"
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

fake_item = FakeListItem()

response_from_object = KnowledgeListItem.model_validate(fake_item)
# print(response_from_object)
# print(response_from_object.model_dump())
# print(response_from_object.model_dump().keys())
actual_fields = set(response_from_object.model_dump().keys())

expected_fields = {
    "id",
    "name",
    "description",
    "status",
    "created_at",
    "updated_at",
}

assert actual_fields == expected_fields, (
    f"响应字段不符合预期，实际字段：{actual_fields}"
)

assert "user_id" not in actual_fields

print("测试成功：响应字段集合完全符合预期")
print(actual_fields)

fake_item.status = "PENDING"
try:
    response_from_object = KnowledgeListItem.model_validate(fake_item)
except ValidationError as e:
    print("测试成功:拒绝非法status")
    print(e)
else:
    print("测试失败：接收非法status")