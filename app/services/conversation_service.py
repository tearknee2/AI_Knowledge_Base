from pydantic import Field

from app.repositories.conversation_repository import ConversationRepository
from app.services.knowledge_base_service import BusinessException, KnowledgeBaseService

class ConversationService:
    def __init__(
        self,
        repository: ConversationRepository,
        knowledge_base_service: KnowledgeBaseService
    ):
        self.repository = repository
        self.knowledge_base_service = knowledge_base_service


    def get_or_create_conversation(
        self,
        knowledge_base_id: int,
        title: str,
        conversation_id: int | None = None,
        user_id : int = 1,
    ):
        self.knowledge_base_service.get_knowledge_base_by_id(
            knowledge_base_id,
            user_id
        )
        if conversation_id is None:
            conversation = self.repository.create(
                user_id=user_id,
                knowledge_base_id=knowledge_base_id,
                title=title[:255],
            )
        else:
            conversation = self.repository.get_by_id(conversation_id)

            if (
                conversation is None
                or conversation.user_id != user_id
                or conversation.knowledge_base_id != knowledge_base_id
            ):
                raise BusinessException(
                    "Conversation not found or access denied"
                )

        return conversation
