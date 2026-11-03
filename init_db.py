# 一次性建表脚本：项目没有 alembic 迁移历史，首次部署时在空库上创建全部表。
# 用法（在 compose 网络内执行，可重复运行，已存在的表会跳过）：
#   docker compose run --rm app python init_db.py
from app.core.database import Base, engine

# 导入所有模型模块，把表注册到 Base.metadata
import app.models.user  # noqa: F401
import app.models.knowledge_base  # noqa: F401
import app.models.document  # noqa: F401
import app.models.conversation  # noqa: F401
import app.models.message  # noqa: F401


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("数据库表已创建/确认存在：")
    for name in sorted(Base.metadata.tables):
        print(f"  - {name}")
