from app.services.document_service import DocumentService
from app.services.knowledge_base_service import BusinessException


class FakeKnowledgeBaseService:
    def __init__(self, should_raise=False):
        self.should_raise = should_raise

    def get_knowledge_base_by_id(self, knowledge_base_id: int, user_id: int):
        if self.should_raise:
            raise BusinessException("没有权限访问该知识库")
        else:
            return

class FakeDocumentRepository:
    def __init__(self, documents):
        self.documents = documents
        self.called = False
    def get_by_knowledge_base_id(self, knowledge_base_id: int):
        self.called = True
        return self.documents

def test_list_documents_success():

    fake_knowledge_base_service = FakeKnowledgeBaseService(
        should_raise=False
    )
    fake_document_repository = FakeDocumentRepository(
        documents=[{"id":1},{"id":2}]
    )

    document_service = DocumentService(fake_document_repository,fake_knowledge_base_service)

    knowledge_base_id = 1
    user_id = 1
    result = document_service.list_documents(knowledge_base_id, user_id)
    assert result == [{"id":1},{"id":2}]
    assert fake_document_repository.called is True


def test_list_documents_empty():
    fake_knowledge_base_service = FakeKnowledgeBaseService(
        should_raise=False
    )
    fake_document_repository = FakeDocumentRepository(
        documents=[]
    )

    document_service = DocumentService(fake_document_repository,fake_knowledge_base_service)

    knowledge_base_id = 1
    user_id = 1
    result = document_service.list_documents(knowledge_base_id, user_id)
    assert result == []
    assert fake_document_repository.called is True

def test_list_documents_permission_denied():
    fake_knowledge_base_service = FakeKnowledgeBaseService(
        should_raise=True
    )
    fake_document_repository = FakeDocumentRepository(
        documents=[{"id":1},{"id":2}]
    )

    document_service = DocumentService(fake_document_repository,fake_knowledge_base_service)

    knowledge_base_id = 1
    user_id = 1
    exception_raised = False

    try:
        document_service.list_documents(knowledge_base_id, user_id)
    except BusinessException:
        exception_raised = True
        assert fake_document_repository.called is False

    assert exception_raised is True

test_list_documents_success()
test_list_documents_empty()
test_list_documents_permission_denied()