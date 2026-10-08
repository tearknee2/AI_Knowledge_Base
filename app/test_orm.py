# test_orm.py
from app.core.database import SessionLocal
from app.models.user import User
from app.core.config import TEST_PASSWORD_HASH

db = SessionLocal()

# 查询全部
print("=====查询全部=====")
users = db.query(User).all()
for user in users:
    print(
        user.id,
        user.username
    )

# 查询单个
print("=====查询单个=====")
user = db.query(User).filter(User.id==1).first()
print(
    user.id,
    user.username
)
# 创建
print("=======创建用户========")
user = User(
    username="张三",
    password_hash=TEST_PASSWORD_HASH
)
db.add(user)
db.commit()
print("创建完成")


# 更新
print("=======更新用户========")
user.username="李四"
db.commit()
print("===更新完成===")


# 删除
print("====删除用户====")
db.delete(user)
db.commit()
print("删除完成")


db.close()