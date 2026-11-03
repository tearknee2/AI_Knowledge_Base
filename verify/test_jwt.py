import pytest
import jwt
from datetime import datetime, timedelta, timezone

from app.core.security import (
    create_access_token,
    decode_access_token
)
from app.core.config import JWT_SECRET_KEY, JWT_ALGORITHM


def test_create_and_decode_token():
    token = create_access_token(
        data={"sub": "1"}
    )

    payload = decode_access_token(token)

    assert payload["sub"] == "1"
    assert "exp" in payload

    print("JWT 创建和解码成功")


def test_invalid_signature():
    # 使用错误的密钥创建一个 Token
    token = jwt.encode(
        {"sub": "1"},
        "wrong-secret-key",
        algorithm=JWT_ALGORITHM
    )

    # 验证时应该因为签名不正确而失败
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)

    print("非法签名 Token 已被拒绝")


def test_expired_token():
    # 创建一个已经过期的 Token
    expired_time = datetime.now(timezone.utc) - timedelta(minutes=1)

    token = jwt.encode(
        {
            "sub": "1",
            "exp": expired_time
        },
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

    # 验证时应该因为 Token 已过期而失败
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)

    print("过期 Token 已被拒绝")


