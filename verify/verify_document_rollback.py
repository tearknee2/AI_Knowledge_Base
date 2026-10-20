from app.repositories.document_repository import DocumentRepository
from app.models.document import Document

class FakeSession:
    def __init__(self):
        self.rollback_called = False

    def add(self, document):
        pass

    def commit(self):
        raise RuntimeError("模拟数据库提交失败")

    def refresh(self, document):
        pass

    def rollback(self):
        self.rollback_called = True

fake_session = FakeSession()
repository = DocumentRepository(fake_session)

document_data = {
    "knowledge_base_id": 1,
    "file_name": "rollback_test.txt",
    "file_path": "temporary/rollback_test.txt",
    "file_type": "txt",
    "file_size": 10,
    "status": "PENDING",
}

try:
    repository.create(document_data)
except RuntimeError as exc:
    print("捕获到预期异常：", exc)

print("rollback 是否被调用：", fake_session.rollback_called)

if fake_session.rollback_called:
    print("rollback 验证 PASS")
else:
    print("rollback 验证 FAIL")