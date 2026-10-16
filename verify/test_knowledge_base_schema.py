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
print("响应字段:",response.model_dump().keys())


fake_kb.description = None

response = KnowledgeBaseResponse.model_validate(fake_kb)

print("\n测试6：描述为空")
print(response.model_dump())


kb7 = KnowledgeBaseCreate(
    name="数学",
)

print("\n测试7通过")
print(kb7)


try:
    KnowledgeBaseCreate(
        name="",
    )
except ValidationError as e:
    print("\n测试8通过:空名称被拒绝")
    print(e)


# 测试9：额外传入数据
try:
    kb9 = KnowledgeBaseCreate(
    name="技术文档",
    description="存放项目技术资料",
    status="PENDING"
    )
except ValidationError as e:
    print("测试9通过：额外字段被拒绝")
    print(e)
else:
    print("测试9失败：额外字段没有被拒绝")



fake_kb.status = "PENDING"
try:
    response = KnowledgeBaseResponse.model_validate(fake_kb)
except ValidationError as e:
    print("\n测试成功：拒绝非法status值")
    print(e)
else:
    print("测试失败，非法status值被接收")