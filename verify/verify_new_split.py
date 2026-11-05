from app.rag.chunk_size_overlap import build_chunks
from pathlib import Path

base_dir = Path(__file__).parent.parent
work_dir = base_dir / "evaluation" / "documents" / "synthetic" / "01_员工管理制度.txt"
print(work_dir)
with open(work_dir, "r", encoding="utf-8") as f:
    chunks=build_chunks(f.read())
    # print(len(chunks))
    assert (isinstance(chunks, list))
    for i in range(len(chunks)):
        print(f"chunk{i}:{len(chunks[i]['text'])}字")
        print(f"chunk{i}\n章节路径：{chunks[i]['section_path']}\n正文：{chunks[i]['text']}")
        assert(isinstance(chunks[i], dict))
        assert(isinstance(chunks[i]['text'], str))
        assert(chunks[i]['text'] != "")
        assert(isinstance(chunks[i]['section_path'], list))
        assert(len(chunks[i]['text']) <= 500)
        assert all(isinstance(path, str) for path in chunks[i]["section_path"])
    assert len(chunks) == 9