# user.py
"""
定义了用户相关的Schema数据结构和校验规则，告诉FastAPI：
客户端注册时应该提交什么数据，
输入数据需要满足什么条件
接口返回用户信息时，允许返回哪些字段
"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):

    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    created_at: datetime