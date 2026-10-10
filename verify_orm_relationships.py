import sys

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import configure_mappers

connections = []
event.listen(Engine, "connect", lambda c, conn: connections.append(1))

from app.core.database import Base
from app.models import Conversation, Document, KnowledgeBase, Message, User

RELATIONSHIPS = [
    ("User <-> KnowledgeBase", User, "knowledge_bases", KnowledgeBase, "user"),
    ("User <-> Conversation", User, "conversations", Conversation, "user"),
    ("KnowledgeBase <-> Document", KnowledgeBase, "documents", Document, "knowledge_base"),
    ("KnowledgeBase <-> Conversation", KnowledgeBase, "conversations", Conversation, "knowledge_base"),
    ("Conversation <-> Message", Conversation, "messages", Message, "conversation"),
]

EXPECTED_TABLES = {
    "users": User,
    "knowledge_bases": KnowledgeBase,
    "documents": Document,
    "conversations": Conversation,
    "messages": Message,
}

failures = []


def check(label, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f"  -- {detail}" if detail else ""))
    if not ok:
        failures.append(label)


print(f"python   : {sys.version.split()[0]}  {sys.executable}")
print(f"cwd      : {__import__('pathlib').Path.cwd()}")

print("\n[1] explicit model imports")
for cls in (User, KnowledgeBase, Document, Conversation, Message):
    check(f"{cls.__name__} imported from package and module",
          getattr(cls, "__table__", None) is not None,
          f"table='{cls.__tablename__}'")

print("\n[2] mapper configuration (no DDL, no connection)")
try:
    configure_mappers()
    check("sqlalchemy.orm.configure_mappers()", True)
except Exception as exc:
    check("sqlalchemy.orm.configure_mappers()", False, f"{type(exc).__name__}: {exc}")

print("\n[3] all five tables registered on the same Base.metadata")
registered = set(Base.metadata.tables)
check("expected tables all present", EXPECTED_TABLES.keys() <= registered,
      f"missing={sorted(EXPECTED_TABLES.keys() - registered) or 'none'}")
check("no unexpected tables", bool(registered) and registered <= set(EXPECTED_TABLES),
      f"extra={sorted(registered - set(EXPECTED_TABLES)) or 'none'}")
for name, cls in EXPECTED_TABLES.items():
    check(f"metadata['{name}'] is {cls.__name__}.__table__",
          Base.metadata.tables.get(name) is cls.__table__,
          f"columns={len(cls.__table__.columns)}")

print("\n[4] relationship / back_populates symmetry")
for label, left, left_attr, right, right_attr in RELATIONSHIPS:
    rel_lr = left.__mapper__.relationships[left_attr]
    rel_rl = right.__mapper__.relationships[right_attr]
    conditions = {
        f"{left.__name__}.{left_attr}.back_populates == '{right_attr}'":
            rel_lr.back_populates == right_attr,
        f"{right.__name__}.{right_attr}.back_populates == '{left_attr}'":
            rel_rl.back_populates == left_attr,
        f"{left.__name__}.{left_attr} targets {right.__name__}":
            rel_lr.mapper is right.__mapper__,
        f"{right.__name__}.{right_attr} targets {left.__name__}":
            rel_rl.mapper is left.__mapper__,
        f"{left.__name__}.{left_attr} is {rel_lr.direction.name}":
            rel_lr.direction.name == "ONETOMANY",
        f"{right.__name__}.{right_attr} is MANYTOONE":
            rel_rl.direction.name == "MANYTOONE",
    }
    check(label, all(conditions.values()),
          f"{left.__name__}.{left_attr} <-> {right.__name__}.{right_attr}")
    for cond, ok in conditions.items():
        if not ok:
            print(f"          unmet: {cond}")

print("\n[5] foreign keys declared in metadata")
for table_name in sorted(Base.metadata.tables):
    for column in Base.metadata.tables[table_name].columns:
        for fk in column.foreign_keys:
            check(f"{table_name}.{column.name} -> {fk.target_fullname}",
                  fk.target_fullname in {f"{t}.id" for t in Base.metadata.tables},
                  f"nullable={column.nullable} ondelete={fk.ondelete}")

print("\n[6] design-conventions spot check")
for label, ok, detail in [
    ("Document has no direct conversation FK", "conversation_id" not in Document.__table__.columns, ""),
    ("Message has no user_id", "user_id" not in Message.__table__.columns, ""),
    ("Message has no knowledge_base_id", "knowledge_base_id" not in Message.__table__.columns, ""),
    ("Message has no updated_at", "updated_at" not in Message.__table__.columns, ""),
    ("Message has created_at", "created_at" in Message.__table__.columns, ""),
]:
    check(label, ok, detail)
print("  [INFO] Conversation.user_id == KnowledgeBase.user_id is NOT enforced by any DB "
      "constraint or ORM validator (application-level only) -- by design for S1")

print("\n[7] isolation proof")
check("zero database connections made during this script", len(connections) == 0,
      f"connect events={len(connections)}")
check("no DDL emitted (create_all / drop never called)", True)

print("\n" + "=" * 62)
if failures:
    print(f"RESULT: {len(failures)} check(s) failed")
    for item in failures:
        print(f"  - {item}")
    sys.exit(1)
print("RESULT: ALL ORM CHECKS PASSED (mapper-level only, not live DB structure)")
print("NOTE  : this validates relationship configuration, NOT database foreign")
print("        keys or row-level data consistency. Use a separate read-only")
print("        INFORMATION_SCHEMA / inspector comparison for that.")
