# 回归测试：确认 txt_loader.load_txt 与 chunk_size_overlap.split_text 改动后原有行为不变
# 只覆盖「对外契约」：返回值、边界、异常类型，不测内部实现细节
import pytest

from app.rag.chunk_size_overlap import split_text
from app.rag.txt_loader import load_txt


# ---------- load_txt ----------

def test_load_txt_reads_and_cleans(tmp_path):
    """正常读取：返回清理后的正文（去首尾空白、逐行 strip、压缩连续空行）。"""
    f = tmp_path / "doc.txt"
    f.write_text("  hello  \n\n\n   world  \n", encoding="utf-8")
    assert load_txt(str(f)) == "hello\n\nworld"


def test_load_txt_rejects_non_txt(tmp_path):
    f = tmp_path / "doc.md"
    f.write_text("hello", encoding="utf-8")
    with pytest.raises(ValueError):
        load_txt(str(f))


def test_load_txt_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_txt(str(tmp_path / "nope.txt"))


def test_load_txt_directory_path(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_txt(str(tmp_path))


def test_load_txt_blank_content_raises(tmp_path):
    """全空白文件视为空内容（本次新增的校验）。"""
    f = tmp_path / "blank.txt"
    f.write_text("   \n\n  \n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_txt(str(f))


# ---------- split_text ----------

def test_split_text_short_text_single_chunk():
    assert split_text("ABC", 10, 2) == ["ABC"]


def test_split_text_length_equals_chunk_size():
    """边界改动点：len(text) == chunk_size 仍应返回单块原文。"""
    assert split_text("ABCDE", 5, 0) == ["ABCDE"]
    assert split_text("ABCDE", 5, 2) == ["ABCDE"]


def test_split_text_empty_returns_empty_list():
    assert split_text("", 9, 4) == []


def test_split_text_overlap_windows():
    chunks = split_text("ABCDEFGHIJKLMN", 4, 1)
    assert chunks[0] == "ABCD"
    assert all(len(c) <= 4 for c in chunks)
    for prev, nxt in zip(chunks, chunks[1:]):
        assert prev[-1:] == nxt[:1]
    # 去掉重叠部分后可无损还原原文（无丢字）
    restored = chunks[0] + "".join(c[1:] for c in chunks[1:])
    assert restored == "ABCDEFGHIJKLMN"


@pytest.mark.parametrize(
    "text,size,overlap,exc",
    [
        ("ABCDEFGHIJKLMN", 9, 9, ValueError),
        ("ABCDEFGHIJKLMN", 0, 0, ValueError),
        ("ABCDEFGHIJKLMN", 4, -1, ValueError),
        ("ABCDEFGHIJKLMN", 4.5, 1, TypeError),
        ("ABCDEFGHIJKLMN", "4", 1, TypeError),
        (None, 4, 1, TypeError),
        ("ABCDEFGHIJKLMN", True, 0, TypeError),
    ],
)
def test_split_text_invalid_inputs(text, size, overlap, exc):
    with pytest.raises(exc):
        split_text(text, size, overlap)


# ---------- 串联 ----------

def test_load_then_split_pipeline(tmp_path):
    """端到端：真实 txt 读入后可直接切分，块数符合预期。"""
    f = tmp_path / "pipeline.txt"
    f.write_text("x" * 25, encoding="utf-8")
    text = load_txt(str(f))
    chunks = split_text(text, 10, 0)
    assert chunks == ["x" * 10, "x" * 10, "x" * 5]
