from io import BytesIO
from pathlib import Path

from starlette.datastructures import UploadFile

from app.services.document_service import DocumentService

class FakeKnowledgeBaseService:
    def get_knowledge_base_by_id(self, knowledge_base_id, user_id=1):
        return object()

class FakeDocumentRepository:
    def create(self, document_data):
        self.file_path = Path(document_data["file_path"])

        self.file_existed_before_failure = Path(
            document_data["file_path"]
        ).exists()

        raise RuntimeError("模拟数据库写入失败")

fake_document_repository = FakeDocumentRepository()
fake_knowledge_base_service = FakeKnowledgeBaseService()
document_service = DocumentService(fake_document_repository, fake_knowledge_base_service)



# upload_dir = Path(__file__).parent.parent / "uploads" / "1"
# before_files = set(upload_dir.iterdir()) if upload_dir.exists() else set()

knowledge_base_id = 1
file = UploadFile(
    filename="test.txt",
    file=BytesIO(b"hello world")
)
try:
    document_service.upload_document(knowledge_base_id, file)
except RuntimeError as exc:
    print("捕获到预期异常：",exc)

print(
    "异常发生前，文件是否存在：",
    fake_document_repository.file_existed_before_failure
)

print(
    "异常处理后，文件是否存在：",
    fake_document_repository.file_path.exists()
)

if (
    fake_document_repository.file_existed_before_failure
    and not fake_document_repository.file_path.exists()
):
    print("文件清理验证 PASS")
else:
    print("文件清理验证 FAIL")



#
# after_files = set(upload_dir.iterdir()) if upload_dir.exists() else set()
#
# new_files = after_files - before_files
#
# if not new_files:
#     print("文件清理检查 PASS")
# else:
#     print("文件清理检查 FAIL，残留文件：", new_files)