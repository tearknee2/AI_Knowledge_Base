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

    def authenticate(self, username: str, password: str):
        """验证用户身份"""

        # 1.根据用户名查询用户
        user = self.repository.get_by_username(username)

        # 2.用户不存在：登录失败
        if not user:
            raise BusinessException("用户名或密码错误")

        # 3.验证原始密码与数据库哈希是否匹配
        is_valid = self.password_hash.verify(
            password,
            user.password_hash
        )

        if not is_valid:
            raise BusinessException("用户名或密码错误")

        # 4.返回用户对象
        return user
