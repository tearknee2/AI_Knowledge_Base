# knowledge_base_repository.py
from sqlalchemy.orm import Session

class KnowledgeBaseRepository:
    def __init__(self, db: Session):
        # 保存传入的数据库会话
        self.db = db

    def get_by_id(self, knowledge_base_id: int):
        # 根据ID查询知识库
        result = self.db.query(KnowledgeBaseRepository).filter(id=knowledge_base_id)
        return result

    def create_(self, knowledge_base_data: dict):
        # 创建知识库对象
        # 加入会话、提交、刷新
        session = Session(knowledge_base_data)
        self.db.add(KnowledgeBaseRepository(session))
        self.db.commit()
        self.db.refresh(KnowledgeBaseRepository(session))