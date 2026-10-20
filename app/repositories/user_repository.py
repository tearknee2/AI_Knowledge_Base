# user_repository.py
from sqlalchemy.orm import Session
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str):
        """根据用户名查询用户"""
        result = self.db.query(User).filter(
            User.username == username
        ).first()
        return result

    def create(self, user_data: dict):
        """根据传入数据创建用户"""
        data = User(**user_data)
        self.db.add(data)
        self.db.commit()
        self.db.refresh(data)
        return data