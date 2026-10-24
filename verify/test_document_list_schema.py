from app.schemas.document import DocumentListItem
import datetime

document = DocumentListItem(
    id=1,
    knowledge_base_id=2,
    file_name='test_document_list_schema.txt',
    file_type='txt',
    file_size=3,
    status="PENDING",
    error_message = None,
    created_at=datetime.datetime.now(),
    updated_at=datetime.datetime.now(),
)
print("\n测试1：直接创建DocumentListItem")
print(document)

assert document.id == 1
assert document.knowledge_base_id == 2
assert document.status == "PENDING"
assert document.error_message is None
assert "file_path" not in document.model_dump()
# model_dump() 是 Pydantic 提供的方法，用于把模型对象转换成 Python 字典。
# 这里是在检查：转换后的对外数据中，不存在 file_path 字段。
expected_fields = {
    "id",
    "knowledge_base_id",
    "file_name",
    "file_type",
    "file_size",
    "status",
    "error_message",
    "created_at",
    "updated_at",
}

assert set(document.model_dump().keys()) == expected_fields

from pydantic import ValidationError

try:
    DocumentListItem(
        id=1,
        knowledge_base_id=2,
        file_name="test.txt",
        file_type="txt",
        file_size=3,
        status="UNKNOWN",
        error_message=None,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )
except ValidationError:
    print("非法状态被正确拒绝")
else:
    raise AssertionError("非法状态没有被拒绝")