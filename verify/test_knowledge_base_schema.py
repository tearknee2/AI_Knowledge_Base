from pydantic import ValidationError
from app.schemas.knowledge_base import KnowledgeBaseCreate,KnowledgeBaseResponse
from datetime import datetime

# 测试1：同时提供名称和描述
kb1 = KnowledgeBaseCreate(
    name="技术文档",
    description="存放项目技术资料"
)

print("测试1：正常数据")
print(kb1.model_dump())

# 测试2：省略描述
kb2 = KnowledgeBaseCreate(
    name="技术文档",
)
print("\n测试2：省略描述")
print(kb2.model_dump())

# 测试3：显式传入None
kb3 = KnowledgeBaseCreate(
    name="技术文档",
    description=None
)
print("\n测试3：描述为None")
print(kb3.model_dump())

# 测试4：名称超过20个字符
try:
    KnowledgeBaseCreate(
        name="这是一个超过二十个字符长度的知识库名称,现在才是",
        description="测试"
    )
except ValidationError as e:
    print("\n测试4：名称过长")
    print(e)


class FakeKnowledgeBase:
    def __init__(self):
        self.id = 1
        self.user_id = 10
        self.name = "技术文档"
        self.description = "存放项目技术文档"
        self.status = "ACTIVE"
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

fake_kb = FakeKnowledgeBase()

response = KnowledgeBaseResponse.model_validate(fake_kb)

print("\n测试5：从对象转换响应 Schema")
print(response)
print(response.model_dump())


fake_kb.description = None

response = KnowledgeBaseResponse.model_validate(fake_kb)

print("\n测试6：描述为空")
print(response.model_dump())