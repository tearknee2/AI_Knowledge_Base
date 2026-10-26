# T1 冒烟测试：RAG 核心纯函数行为与参数校验
# 用例素材来自 verify_chunk_size.py 的历史验证（迁移自 verify/，此处为 pytest 版）
import pytest

from app.rag.chunk_size_overlap import split_text


def test_basic_windows_with_overlap():
    chunks = split_text("ABCDEFGHIJKLMN", 4, 1)
    assert chunks[0] == "ABCD"
    assert all(len(chunk) <= 4 for chunk in chunks)
    # overlap=1：相邻块首尾各 1 字符重叠
    for prev, nxt in zip(chunks, chunks[1:]):
        assert prev[-1:] == nxt[:1]


def test_text_shorter_than_chunk_returns_single_block():
    assert split_text("ABC", 10, 2) == ["ABC"]


def test_empty_text_returns_empty_list():
    assert split_text("", 9, 4) == []


@pytest.mark.parametrize(
    "text,size,overlap,exc",
    [
        ("ABCDEFGHIJKLMN", 9, 9, ValueError),      # size == overlap
        ("ABCDEFGHIJKLMN", -4, 1, ValueError),     # size 非正
        ("ABCDEFGHIJKLMN", 4, -1, ValueError),     # overlap 为负
        ("ABCDEFGHIJKLMN", 4.5, 1, TypeError),     # 浮点 size
        ("ABCDEFGHIJKLMN", "4", 1, TypeError),     # 字符串 size
        (None, 4, 1, TypeError),                   # None 文本
        ("ABCDEFGHIJKLMN", True, 0, TypeError),    # bool 冒充 int
    ],
)
def test_invalid_inputs_raise(text, size, overlap, exc):
    with pytest.raises(exc):
        split_text(text, size, overlap)
