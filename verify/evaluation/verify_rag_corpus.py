# verify/evaluation/verify_rag_corpus.py
"""RAG 评测语料只读验收脚本

检查三部分：
1. MySQL documents 表中文档完整性（数量、id、file_name、status）
2. ChromaDB 中该知识库的向量完整性（按文档数量、多余向量、总数）
3. ChromaDB metadata 中 version 的一致性（每份文档恰好一个非空版本）

只读：仅执行 SELECT 与 collection.get，不写入/删除任何数据，
不执行 Embedding，不调用 LLM。

用法（项目根目录）：
    python verify/evaluation/verify_rag_corpus.py --knowledge-base-id <id>
"""
import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.database import SessionLocal
from app.models.document import Document
from app.rag.vector_store import init

# file_name 以数据库实际记录为准（上传时保留了 evaluation/documents 的 01_/02_ 等来源前缀），
# 与 document_registry.md 中的裸文件名不同。
EXPECTED_DOCUMENTS = {
    23: {"file_name": "01_员工管理制度.txt", "chunks": 9},
    24: {"file_name": "02_项目管理制度.txt", "chunks": 27},
    25: {"file_name": "03_星河计划项目说明.txt", "chunks": 22},
    26: {"file_name": "04_星河科技有限公司费用报销管理办法.txt", "chunks": 13},
    27: {"file_name": "05_星河科技有限公司IT设备管理办法.txt", "chunks": 12},
    29: {"file_name": "06_星河科技有限公司员工培训与考核管理办法.txt", "chunks": 14},
}
EXPECTED_TOTAL_VECTORS = 97


def header(index: int, title: str):
    print()
    print("=" * 62)
    print(f"[{index}/3] {title}")
    print("=" * 62)


def check_documents(db, kb_id: int) -> bool:
    """模块1：数据库文档完整性，全部通过返回 True"""
    header(1, "文档完整性检查（MySQL documents 表）")
    failed = False

    documents = db.query(Document).filter(
        Document.knowledge_base_id == kb_id
    ).all()

    if len(documents) == len(EXPECTED_DOCUMENTS):
        print(f"PASS 文档数量：预期 {len(EXPECTED_DOCUMENTS)}，实际 {len(documents)}")
    else:
        print(f"FAIL 文档数量：预期 {len(EXPECTED_DOCUMENTS)}，实际 {len(documents)}")
        failed = True

    actual_ids = {d.id for d in documents}
    missing_ids = sorted(set(EXPECTED_DOCUMENTS) - actual_ids)
    extra_ids = sorted(actual_ids - set(EXPECTED_DOCUMENTS))
    if not missing_ids and not extra_ids:
        print(f"PASS document_id 集合：{sorted(actual_ids)}，与预期完全一致")
    else:
        print("FAIL document_id 集合与预期不一致")
        if missing_ids:
            print(f"  缺少 document_id：{missing_ids}")
        if extra_ids:
            print(f"  多出 document_id：{extra_ids}")
        failed = True

    for doc_id in sorted(EXPECTED_DOCUMENTS):
        doc = next((d for d in documents if d.id == doc_id), None)
        if doc is None:
            continue  # 缺失已在集合检查中报告
        expected_name = EXPECTED_DOCUMENTS[doc_id]["file_name"]
        if doc.file_name == expected_name:
            print(f"PASS file_name[{doc_id}]：{doc.file_name}")
        else:
            print(f"FAIL file_name[{doc_id}]：预期 {expected_name}，实际 {doc.file_name}")
            failed = True

    bad_status = {d.id: d.status for d in documents if d.status != "COMPLETED"}
    if bad_status:
        print(f"FAIL status：以下文档状态不是 COMPLETED：{bad_status}")
        failed = True
    elif documents:
        print(f"PASS status：{len(documents)} 份文档全部为 COMPLETED")

    return not failed


def check_vectors(metadatas: list) -> bool:
    """模块2：ChromaDB 向量完整性，全部通过返回 True"""
    header(2, "向量完整性检查（ChromaDB）")
    failed = False

    counts = Counter()
    unexpected_docs = Counter()
    for metadata in metadatas:
        if metadata is None:
            unexpected_docs["<metadata为None>"] += 1
            continue
        doc_id = metadata.get("document_id")
        if doc_id in EXPECTED_DOCUMENTS:
            counts[doc_id] += 1
        else:
            unexpected_docs[doc_id] += 1

    for doc_id in sorted(EXPECTED_DOCUMENTS):
        expected = EXPECTED_DOCUMENTS[doc_id]["chunks"]
        actual = counts.get(doc_id, 0)
        if actual == expected:
            print(f"PASS 向量数量[{doc_id}]：预期 {expected}，实际 {actual}")
        else:
            print(f"FAIL 向量数量[{doc_id}]：预期 {expected}，实际 {actual}")
            failed = True

    if unexpected_docs:
        print(f"FAIL 存在不属于六份预期文档的向量：{dict(unexpected_docs)}")
        failed = True
    else:
        print("PASS 多余向量：所有向量均属于六份预期文档")

    total = len(metadatas)
    if total == EXPECTED_TOTAL_VECTORS:
        print(f"PASS 向量总数：预期 {EXPECTED_TOTAL_VECTORS}，实际 {total}")
    else:
        print(f"FAIL 向量总数：预期 {EXPECTED_TOTAL_VECTORS}，实际 {total}")
        failed = True

    return not failed


def check_versions(metadatas: list) -> bool:
    """模块3：版本一致性，全部通过返回 True"""
    header(3, "版本一致性检查（ChromaDB metadata.version）")
    failed = False

    versions_by_doc = defaultdict(set)
    docs_with_missing_version = set()
    for metadata in metadatas:
        if metadata is None:
            continue  # 已在模块2报告
        doc_id = metadata.get("document_id")
        if doc_id not in EXPECTED_DOCUMENTS:
            continue  # 非预期文档已在模块2报告
        version = metadata.get("version")
        if not version or not str(version).strip():
            docs_with_missing_version.add(doc_id)
            continue
        versions_by_doc[doc_id].add(version)

    for doc_id in sorted(EXPECTED_DOCUMENTS):
        versions = versions_by_doc[doc_id]
        if doc_id in docs_with_missing_version:
            print(f"FAIL version[{doc_id}]：存在缺失或为空的 version")
            failed = True
        elif len(versions) == 1:
            print(f"PASS version[{doc_id}]：恰好一个版本 {next(iter(versions))}")
        elif len(versions) == 0:
            print(f"FAIL version[{doc_id}]：该文档没有任何向量，version 集合为空")
            failed = True
        else:
            print(
                f"FAIL version[{doc_id}]：出现 {len(versions)} 个版本"
                f"（旧版本残留）：{sorted(versions)}"
            )
            failed = True

    return not failed


def main():
    parser = argparse.ArgumentParser(description="RAG 评测语料只读验收脚本")
    parser.add_argument(
        "--knowledge-base-id",
        type=int,
        required=True,
        help="评测知识库 ID（必填，从命令行传入，不在脚本中硬编码）",
    )
    args = parser.parse_args()
    kb_id = args.knowledge_base_id

    print(f"评测知识库 ID：{kb_id}")
    print("执行模式：只读（MySQL 仅 SELECT，Chroma 仅 collection.get），"
          "不写入/删除数据，不执行 Embedding，不调用 LLM")

    _, collection = init()
    metadatas = collection.get(
        where={"knowledge_base_id": kb_id},
        include=["metadatas"],
    )["metadatas"]

    db = SessionLocal()
    try:
        results = [
            check_documents(db, kb_id),
            check_vectors(metadatas),
            check_versions(metadatas),
        ]
    finally:
        db.close()

    print()
    print("=" * 62)
    if all(results):
        print("整体结果：ALL PASS")
        sys.exit(0)

    print("整体结果：ALL FAIL")
    sys.exit(1)


if __name__ == "__main__":
    main()
