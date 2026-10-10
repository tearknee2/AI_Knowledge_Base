# knowledge_base_service.py

class KnowledgeBaseService:
    def __init__(self, repository):
        self.repository = repository

    def create_knowledge_base(self, knowledge_base_data: dict):
        """
        接收知识库数据，
        调用Respository创建知识库，
        :return: 返回创建好的知识库对象
        """
        return self.repository.create(knowledge_base_data)
