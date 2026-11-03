from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import(
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
)

def create_access_token(data: dict):
    """创建JWT访问令牌"""

    if not JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY 未配置")

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    encode_jwt = jwt.encode(
        to_encode,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )
    return encode_jwt

def decode_access_token(token: str):
    """验证并解码JWT访问令牌"""

    if not JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY未配置")

    payload = jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM]
    )
    return payload