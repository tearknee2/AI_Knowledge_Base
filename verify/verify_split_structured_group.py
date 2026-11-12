
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from transformers import AutoTokenizer


# 1. 设置项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from app.rag.chunk_size_overlap import split_structured_group


# 2. 加载 BGE Tokenizer
model_path = os.getenv("BGE_MODEL_PATH")

if not model_path:
    raise ValueError("没有找到 BGE_MODEL_PATH，请检查 .env 配置")

tokenizer = AutoTokenizer.from_pretrained(
    model_path,
    local_files_only=True
)


# 3. 构造测试数据
short_text = "员工应当遵守公司的考勤管理制度。"

long_sentence = (
    "员工应当遵守公司的考勤管理制度，"
    "按时上下班，并按照规定完成每日考勤登记；"
)

long_text = (long_sentence * 100) + "员工应当认真履行考勤义务。"

# 模拟原始文档
source_text = short_text + long_text

short_start = 0
short_end = len(short_text)

long_start = short_end
long_end = long_start + len(long_text)

group = {
    "section_path": ["员工管理制度", "考勤管理"],
    "clause_title": "第三条 考勤要求",
    "blocks": [
        {
            "text": short_text,
            "source_start": short_start,
            "source_end": short_end,
        },
        {
            "text": long_text,
            "source_start": long_start,
            "source_end": long_end,
        },
    ],
}


# 4. 执行切分
max_tokens = 80
overlap_tokens = 20

chunks = split_structured_group(
    group,
    tokenizer,
    target_tokens=40,
    max_tokens=max_tokens,
    overlap_tokens=overlap_tokens,
)


# 5. 验证每个 Chunk 的正文都来自原文，且没有越界
# 注意：开启 Overlap 后，相邻 Chunk 会重复一部分正文，
# 因此不能再断言所有 Chunk 直接拼接等于原文。
for chunk in chunks:
    assert (
        source_text[chunk["source_start"]:chunk["source_end"]]
        == chunk["text"]
    ), "Chunk 正文与原文位置不一致"


# 6. 验证每个 Chunk 的原文位置
for chunk in chunks:
    start = chunk["source_start"]
    end = chunk["source_end"]

    assert source_text[start:end] == chunk["text"], (
        f"原文位置错误：{start} - {end}"
    )

    assert end - start == len(chunk["text"])


# 7. 验证每个 Chunk 的 Token 数
token_counts = [
    len(
        tokenizer.encode(
            (
                " > ".join(chunk["section_path"])
                + (
                    " > " + chunk["clause_title"]
                    if chunk["clause_title"] is not None
                    else ""
                )
                + "\n"
                + chunk["text"]
            ),
            add_special_tokens=True,
        )
    )
    for chunk in chunks
]

assert all(count <= max_tokens for count in token_counts), (
    "存在超过 Token 上限的 Chunk"
)


# 8. 验证短 block 没有被不必要地切分
short_chunks = [
    chunk for chunk in chunks
    if chunk["source_end"] <= short_end
]

assert len(short_chunks) == 1
assert short_chunks[0]["text"] == short_text


# 8.1 验证每个 block 的 Chunk 覆盖范围、无遗漏、无越界
for block in group["blocks"]:
    block_chunks = [
        chunk for chunk in chunks
        if (
            chunk["source_start"] >= block["source_start"]
            and chunk["source_end"] <= block["source_end"]
        )
    ]

    # 按原文位置排序
    block_chunks.sort(key=lambda chunk: chunk["source_start"])

    assert block_chunks, "某个 block 没有生成 Chunk"

    # 第一个 Chunk 应从 block 起点开始
    assert block_chunks[0]["source_start"] == block["source_start"]

    # 最后一个 Chunk 应到达 block 终点
    assert block_chunks[-1]["source_end"] == block["source_end"]

    # 同一个 block 内：不遗漏、不乱序，被拆分的 block 必须有 Overlap
    for previous, current in zip(block_chunks, block_chunks[1:]):
        assert previous["source_end"] >= current["source_start"], (
            "同一个 block 内出现正文遗漏"
        )
        assert current["source_start"] >= previous["source_start"], (
            "同一个 block 内出现 Chunk 乱序"
        )
        if len(block_chunks) > 1:
            assert previous["source_end"] > current["source_start"], (
                "同一个 block 拆分出的相邻 Chunk 没有 Overlap"
            )


# 8.2 验证 Overlap 部分的 Token 数不超过配置
for block in group["blocks"]:
    block_chunks = [
        chunk for chunk in chunks
        if (
            chunk["source_start"] >= block["source_start"]
            and chunk["source_end"] <= block["source_end"]
        )
    ]
    block_chunks.sort(key=lambda chunk: chunk["source_start"])

    for previous, current in zip(block_chunks, block_chunks[1:]):
        overlap_length = previous["source_end"] - current["source_start"]
        overlap_text = current["text"][:overlap_length]

        assert overlap_text == previous["text"][-overlap_length:]

        overlap_token_count = len(
            tokenizer.encode(overlap_text, add_special_tokens=False)
        )
        assert overlap_token_count <= overlap_tokens


# 8.3 验证结构信息继承
for chunk in chunks:
    assert chunk["section_path"] == group["section_path"]
    assert chunk["clause_title"] == group["clause_title"]


# 9. 输出结果
print("Chunk 总数：", len(chunks))
print("短文本 Chunk 数量：", len(short_chunks))
print("长文本 Chunk 数量：", len(chunks) - len(short_chunks))
print("最大 Token 数：", max(token_counts))
print("最小 Token 数：", min(token_counts))
print("原文位置检查：PASS")
print("正文不遗漏/不乱序检查：PASS")
print("Overlap 检查：PASS")
print("Token 上限检查：PASS")
