from pydantic import ValidationError
from app.schemas.document import DocumentResponse,DocumentUploadResponse
from datetime import datetime

document = DocumentResponse(
    id=1,
    file_name="test.txt",
    file_type="txt",
    file_size=100,
    status="PENDING",
    created_at=datetime.now()
)

print("\n测试1：直接创建DocumentResponse")
print(document)

class FakeDocument:
    def __init__(self):
        self.id = 1
        self.file_name = "test.txt"
        self.file_type = "txt"
        self.file_size = 100
        self.status = "PENDING"
        self.created_at = datetime.now()

        # 模拟数据库对象中的内部字段
        self.file_path = "uploads/test.txt"
        self.error_message = None

fake_document = FakeDocument()

# response_from_object = DocumentResponse.model_validate(fake_document)
# print("\n测试2：从普通对象转换DocumentResponse，响应Schema")
# print(response_from_object)
# print(response_from_object.model_dump().keys())
response_from_object = DocumentResponse.model_validate(fake_document)

actual_fields = set(response_from_object.model_dump().keys())

expected_fields = {
    "id",
    "file_name",
    "file_type",
    "file_size",
    "status",
    "created_at",
}

assert actual_fields == expected_fields, (
    f"DocumentResponse 响应字段不符合预期，实际字段：{actual_fields}"
)

assert "file_path" not in actual_fields
assert "error_message" not in actual_fields

print("\n测试2成功：DocumentResponse 响应字段集合完全符合预期")
print(actual_fields)

try:
    fake_document.status = "active"
    response_from_object = DocumentResponse.model_validate(fake_document)
except ValidationError as e:
    print("\n测试成功：拒绝非法status")
    print(e)
else:
    print("测试失败，接收了非法status")



fake_document.status = "PENDING"
fake_document.file_size = 5000000000

response_from_object = DocumentResponse.model_validate(fake_document)
print("\n测试3：从对象转换响应Schema，验证大文件")
print(response_from_object)




response = DocumentUploadResponse(
    id=1,
    knowledge_base_id=11,
    file_name="test.txt",
    status="PENDING",
    created_at=datetime.now()
)

print("\n测试4：创建DocumentUploadResponse")
print(response.model_dump().keys())

class FakeUpload:
    def __init__(self):
        self.id = 1
        self.knowledge_base_id = 1
        self.file_name = "test.txt"
        self.status = "PENDING"
        self.created_at = datetime.now()

        # 模拟数据库对象中的内部字段
        self.file_path = "uploads/test.txt"
        self.error_message = None

fake_upload = FakeUpload()

# response_from_object = DocumentUploadResponse.model_validate(fake_upload)
# print("\n测试5：从对象转换DocumentUploadResponse,响应Schema")
# print(response_from_object)
response_from_object = DocumentUploadResponse.model_validate(fake_upload)

actual_fields = set(response_from_object.model_dump().keys())

expected_fields = {
    "id",
    "knowledge_base_id",
    "file_name",
    "status",
    "created_at",
}

assert actual_fields == expected_fields, (
    f"DocumentUploadResponse 相应字段不符合预期，实际字段:{actual_fields}"
)

assert "file_path" not in actual_fields
assert "error_message" not in actual_fields

print("\n测试5成功：DocumentUploadResponse 相应字段集合完全符合预期")
print(actual_fields)

try:
    fake_upload.status = "ACTIVE"
    response_from_object = DocumentUploadResponse.model_validate(fake_upload)
except ValidationError as e:
    print("\n测试成功，非法status被拒绝")
    print(e)
else:
    print("测试失败，非法status被接收")