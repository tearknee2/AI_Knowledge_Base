# config.py
import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(
    dotenv_path=str(BASE_DIR / '.env')
)

# 读取出来的都是str
APP_NAME = os.getenv('APP_NAME')

MYSQL_HOST = os.getenv('MYSQL_HOST')

MYSQL_PORT = os.getenv('MYSQL_PORT')

MYSQL_USER = os.getenv('MYSQL_USER')

MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')

MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')

TEST_PASSWORD_HASH = os.getenv('TEST_PASSWORD_HASH')

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

DEEPSEEK_BASE_URL = os.getenv(
    'DEEPSEEK_BASE_URL',
    'https://api.deepseek.com'
)

DEEPSEEK_MODEL = os.getenv(
    'DEEPSEEK_MODEL',
    "deepseek-v4-flash"
)

# JWT 认证配置
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256"
)

JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
        "30"
    )
)

ENABLE_RERANK = os.getenv("ENABLE_RERANK", "false").lower() == "true"

BGE_RERANKER_PATH = os.getenv(
    "BGE_RERANKER_PATH",
)