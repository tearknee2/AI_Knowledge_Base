from pwdlib import PasswordHash
from app.repositories.user_repository import UserRepository

class BusinessException(Exception):
    pass

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
        self.password_hash = PasswordHash.recommended()

    def create(self, user_data: dict):
        """创建用户"""
        # 判断用户名是否存在
        existing = self.repository.get_by_username(user_data['username'])
        if existing:
            raise BusinessException("该用户已存在")

        # 处理密码哈希
        data = user_data.copy() # 浅拷贝
        data['password_hash'] = self.password_hash.hash(data['password'])
        data.pop('password',None)

        # 组织注册业务
        result = self.repository.create(data)
        return result