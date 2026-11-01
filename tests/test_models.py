# ORM 层测试：用 SQLite 内存库验证模型建表、字段约束与关系导航。
# 由 verify/ 下 test_orm.py、test_relationship.py、test_document_relationship.py
# 三个 print 式检查脚本重写而来（原脚本无断言、依赖真实 MySQL）。
#
# 已知方言差异：SQLAlchemy 2.x 的 Enum 默认 create_constraint=False，
# SQLite 上不生成 CHECK 约束，非法状态值不会被数据库拒绝（合法值由
# Schema 层 Literal 把守）；MySQL 原生 ENUM 的拒绝行为属于真实库行为，
# 不在本套件覆盖范围。
import pytest
from sqlalchemy.exc import IntegrityError

from app.models.document import Document
from app.models.knowledge_base import KnowledgeBase
from app.models.user import User


def test_user_crud_lifecycle(db_session):
    """对应 verify/test_orm.py：创建 -> 查询 -> 更新 -> 删除。"""
    user = User(username="张三", password_hash="test-hash")
    db_session.add(user)
    db_session.commit()

    fetched = db_session.query(User).filter(User.username == "张三").one()
    assert fetched.id is not None

    fetched.username = "李四"
    db_session.commit()

    renamed = db_session.query(User).filter(User.id == fetched.id).one()
    assert renamed.username == "李四"

    db_session.delete(renamed)
    db_session.commit()
    assert db_session.query(User).filter(User.id == fetched.id).first() is None


def test_user_username_is_unique(db_session):
    db_session.add(User(username="alice", password_hash="hash-1"))
    db_session.commit()

    db_session.add(User(username="alice", password_hash="hash-2"))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_timestamps_filled_by_server_default(db_session):
    """created_at / updated_at 不手动赋值，由数据库默认值填充。"""
    user = User(username="bob", password_hash="hash")
    db_session.add(user)
    db_session.commit()

    assert user.created_at is not None
    assert user.updated_at is not None


def _create_kb(db_session, user_id=1, name="技术文档"):
    kb = KnowledgeBase(user_id=user_id, name=name, description=None, status="ACTIVE")
    db_session.add(kb)
    db_session.commit()
    return kb


def _create_document(db_session, knowledge_base_id, file_name="test.txt"):
    document = Document(
        knowledge_base_id=knowledge_base_id,
        file_name=file_name,
        file_path=f"uploads/{knowledge_base_id}/{file_name}",
        file_type="txt",
        file_size=100,
        status="PENDING",
    )
    db_session.add(document)
    db_session.commit()
    return document


def test_user_knowledge_base_relationship_both_directions(db_session):
    """对应 verify/test_relationship.py：User <-> KnowledgeBase 双向导航。"""
    user = User(username="carol", password_hash="hash")
    db_session.add(user)
    db_session.commit()

    kb1 = KnowledgeBase(user_id=user.id, name="数学", status="ACTIVE")
    kb2 = KnowledgeBase(user_id=user.id, name="物理", status="ACTIVE")
    db_session.add_all([kb1, kb2])
    db_session.commit()

    assert {kb.name for kb in user.knowledge_bases} == {"数学", "物理"}
    assert kb1.user.id == user.id
    assert kb1.user.username == "carol"


def test_knowledge_base_document_relationship_both_directions(db_session):
    """对应 verify/test_document_relationship.py：KnowledgeBase <-> Document 双向导航。"""
    kb = _create_kb(db_session)
    document = _create_document(db_session, kb.id)

    assert document.knowledge_base.id == kb.id
    assert [doc.id for doc in kb.documents] == [document.id]


def test_documents_do_not_leak_across_knowledge_bases(db_session):
    kb_math = _create_kb(db_session, name="数学")
    kb_physics = _create_kb(db_session, name="物理")
    _create_document(db_session, kb_math.id, file_name="math.txt")

    assert [doc.file_name for doc in kb_math.documents] == ["math.txt"]
    assert kb_physics.documents == []


def test_document_required_fields_cannot_be_null(db_session):
    kb = _create_kb(db_session)
    document = Document(
        knowledge_base_id=kb.id,
        file_name=None,  # nullable=False
        file_path="uploads/1/none.txt",
        file_type="txt",
        file_size=1,
        status="PENDING",
    )
    db_session.add(document)
    with pytest.raises(IntegrityError):
        db_session.commit()
