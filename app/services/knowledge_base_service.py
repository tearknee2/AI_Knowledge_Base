from app.core.exceptions import ConflictError, ResourceNotFoundError

class KnowledgeBaseService:
    def __init__(self, repository):
        self.repository = repository

    def create_knowledge_base(self, knowledge_base_data: dict):
        """
        接收知识库数据，调用Repository创建知识库，
        :return: 返回创建好的知识库对象
        """
        user_id = knowledge_base_data['user_id']
        name = knowledge_base_data['name']
        existing = self.repository.get_by_name_and_user(
            user_id,
            name
        )

        if existing:
            raise ConflictError()

        knowledge_base_data['status'] = "ACTIVE"

        return self.repository.create(knowledge_base_data)

    def get_knowledge_bases_by_user(self, user_id: int):
        """查询指定用户的知识库列表"""
        return self.repository.get_by_user(user_id)


    def get_knowledge_base_by_id(self, knowledge_base_id: int, user_id: int):
        """根据知识库ID查询对应的知识库记录"""
        result = self.repository.get_by_id(knowledge_base_id)
        if result is None or user_id != result.user_id:
            raise ResourceNotFoundError()
        return result