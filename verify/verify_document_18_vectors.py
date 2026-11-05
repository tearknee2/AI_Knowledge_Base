from collections import Counter
from pathlib import Path
import random

from app.rag.vector_store import init
from app.rag.txt_loader import load_txt
from app.rag.chunk_size_overlap import build_chunks


# 1. 计算本次文档理论上应该产生多少个 Chunk
# base_dir = Path(__file__).resolve().parent[4]
# file_path = (
#     base_dir
#     / "evaluation"
#     / "documents"
#     / "synthetic"
#     / "01_员工管理制度.txt"
# )

text = load_txt(r"D:\PythonProject\ai_agent\demo\large_test.txt")
expected_count = len(build_chunks(text))

print(f"理论 Chunk 数量：{expected_count}")


# 2. 查询 ChromaDB 中 document_id=18 的向量
client, collection = init()

result = collection.get(
    where={"document_id": 20},
    include=["metadatas"]
)

ids = result["ids"]
metadatas = result["metadatas"]

print(f"ChromaDB 实际向量数量：{len(ids)}")


# 3. 按 version 统计向量数量
version_counts = Counter(
    metadata["version"]
    for metadata in metadatas
    if metadata is not None
)

print("\n各版本向量数量：")
for version, count in version_counts.items():
    print(f"版本：{version}，数量：{count}")


# 4. 检查向量数量和版本情况
print("\n验证结果：")

if len(version_counts) == 1:
    current_count = next(iter(version_counts.values()))

    if current_count == expected_count:
        print("PASS：当前只有一个版本，且向量数量正确")
    else:
        print("FAIL：向量数量与理论 Chunk 数量不一致")
else:
    print("FAIL：存在多个版本，可能有旧版本向量残留")


# 5. 随机抽取一条 metadata
if metadatas:
    index = random.randrange(len(metadatas))

    print("\n随机抽取的向量：")
    print("向量 ID：", ids[index])
    print("Metadata：", metadatas[index])
    print("章节路径：", metadatas[index].get("section_path"))