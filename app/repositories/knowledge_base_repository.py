# knowledge_base_repository.py
from sqlalchemy.orm import Session
from app.models.knowledge_base import KnowledgeBase

class KnowledgeBaseRepository:
    def __init__(self, db: Session):
        # 保存传入的数据库会话
        self.db = db

    def get_by_id(self, knowledge_base_id: int):
        # 根据ID查询知识库
        # result = self.db.query(KnowledgeBase).filter(
        #     KnowledgeBase.id == knowledge_base_id).first()
        # 查询KnowledgeBase模型
        # self.db.query(KnowledgeBase)
        result = self.db.query(KnowledgeBase).filter(
            KnowledgeBase.id == knowledge_base_id
        ).first()
        if result:
            return result
        return None
        # SQLAlchemy 的 .first() 在没有匹配记录时会返回 None，因此这里可以写得更简洁：
        # return result

    def create(self, knowledge_base_data: dict):
        # 创建知识库对象
        # 加入会话、提交、刷新
        data = KnowledgeBase(**knowledge_base_data)
        self.db.add(data)
        self.db.commit()
        self.db.refresh(data)
        return data