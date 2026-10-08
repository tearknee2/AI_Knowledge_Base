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
