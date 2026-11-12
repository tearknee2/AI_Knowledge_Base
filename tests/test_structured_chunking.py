# 结构化普通正文 Chunking：Structural Overlap 回归测试
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from transformers import AutoTokenizer

from app.rag.chunk_size_overlap import (
    count_tokens,
    group_structured_documents,
    merge_paragraph_blocks,
    parse_structured_document,
    split_structured_group,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


@pytest.fixture(scope="module")
def tokenizer():
    model_path = os.getenv("BGE_MODEL_PATH")
    if not model_path:
        pytest.skip("BGE_MODEL_PATH 未配置")
    return AutoTokenizer.from_pretrained(model_path, local_files_only=True)


def build_embedding_text(chunk):
    section_path = " > ".join(chunk["section_path"])
    if chunk["clause_title"] is not None:
        section_path += " > " + chunk["clause_title"]
    return section_path + "\n" + chunk["text"]


def make_block(text, start):
    return {
        "text": text,
        "source_start": start,
        "source_end": start + len(text),
    }


def make_group(blocks, section_path=None, clause_title=None):
    return {
        "section_path": section_path or ["员工管理制度"],
        "clause_title": clause_title,
        "blocks": blocks,
    }


def assert_structural_contract(chunks, source_text, blocks, max_tokens, tokenizer):
    assert chunks

    for chunk in chunks:
        start = chunk["source_start"]
        end = chunk["source_end"]
        assert chunk["text"]
        assert 0 <= start < end <= len(source_text)
        assert source_text[start:end] == chunk["text"]
        assert count_tokens(build_embedding_text(chunk), tokenizer) <= max_tokens

        owners = [
            block
            for block in blocks
            if block["source_start"] <= start and end <= block["source_end"]
        ]
        assert len(owners) == 1, "Chunk 越出了原始 block"

    assert [chunk["source_start"] for chunk in chunks] == sorted(
        chunk["source_start"] for chunk in chunks
    )

    for block in blocks:
        block_chunks = [
            chunk
            for chunk in chunks
            if block["source_start"] <= chunk["source_start"]
            and chunk["source_end"] <= block["source_end"]
        ]
        block_chunks.sort(key=lambda chunk: chunk["source_start"])
        assert block_chunks

        assert block_chunks[0]["source_start"] == block["source_start"]
        assert block_chunks[-1]["source_end"] == block["source_end"]

        for previous, current in zip(block_chunks, block_chunks[1:]):
            assert previous["source_end"] >= current["source_start"], "正文出现遗漏"
            assert current["source_start"] >= previous["source_start"], "Chunk 乱序"


def test_adjacent_chunks_from_same_block_have_semantic_overlap(tokenizer):
    sentence = "员工应当遵守公司的考勤管理制度，按时上下班，并完成每日考勤登记。"
    text = "".join(f"第{i}项：{sentence}" for i in range(1, 41))
    block = make_block(text, 0)
    group = make_group([block])

    max_tokens = 140
    overlap_tokens = 40
    chunks = split_structured_group(
        group,
        tokenizer,
        max_tokens=max_tokens,
        overlap_tokens=overlap_tokens,
    )

    assert len(chunks) >= 3
    assert_structural_contract(chunks, text, [block], max_tokens, tokenizer)

    for previous, current in zip(chunks, chunks[1:]):
        overlap_length = previous["source_end"] - current["source_start"]
        assert overlap_length > 0, "同一 block 的相邻 Chunk 没有重叠"
        assert current["text"][:overlap_length] == previous["text"][-overlap_length:]
        assert len(
            tokenizer.encode(
                previous["text"][-overlap_length:],
                add_special_tokens=False,
            )
        ) <= overlap_tokens
        assert current["source_start"] == 0 or (
            text[current["source_start"] - 1] in "。！？；\n，、："
        )


def test_no_overlap_between_different_blocks(tokenizer):
    text_a = "".join(
        f"甲项{i}：员工应当遵守考勤制度，按时上下班。" for i in range(1, 41)
    )
    text_b = "".join(
        f"乙项{i}：员工应当提前提交请假申请，并完成审批。" for i in range(1, 41)
    )
    source_text = text_a + text_b
    blocks = [
        make_block(text_a, 0),
        make_block(text_b, len(text_a)),
    ]
    group = make_group(blocks)

    max_tokens = 140
    chunks = split_structured_group(
        group,
        tokenizer,
        max_tokens=max_tokens,
        overlap_tokens=40,
    )

    assert_structural_contract(chunks, source_text, blocks, max_tokens, tokenizer)

    boundary_index = next(
        index
        for index, chunk in enumerate(chunks)
        if chunk["source_start"] >= len(text_a)
    )
    assert boundary_index > 0
    assert chunks[boundary_index - 1]["source_end"] == len(text_a)
    assert chunks[boundary_index]["source_start"] == len(text_a)
    assert chunks[boundary_index]["text"] == text_b[: len(chunks[boundary_index]["text"])]


def test_no_overlap_between_sections(tokenizer):
    body_a = "".join(
        f"总则第{i}项：员工应当遵守公司的各项规章制度。" for i in range(1, 41)
    )
    body_b = "".join(
        f"考勤第{i}项：员工应当按时上下班并完成每日考勤登记。" for i in range(1, 41)
    )
    document = (
        "# 总则\n"
        f"{body_a}\n"
        "\n"
        "# 考勤\n"
        f"{body_b}\n"
    )

    blocks = merge_paragraph_blocks(parse_structured_document(document))
    groups = group_structured_documents(blocks)

    max_tokens = 140
    chunks = [
        chunk
        for group in groups
        for chunk in split_structured_group(
            group,
            tokenizer,
            max_tokens=max_tokens,
            overlap_tokens=40,
        )
    ]

    paragraph_blocks = [block for block in blocks if block["type"] == "paragraph"]
    assert_structural_contract(
        chunks,
        document,
        paragraph_blocks,
        max_tokens,
        tokenizer,
    )
    assert {tuple(chunk["section_path"]) for chunk in chunks} == {
        ("总则",),
        ("考勤",),
    }

    for previous, current in zip(chunks, chunks[1:]):
        if previous["section_path"] != current["section_path"]:
            assert previous["source_end"] <= current["source_start"]


def test_no_overlap_between_clauses(tokenizer):
    body_a = "".join(
        f"总则第{i}项：员工应当遵守公司的各项规章制度。" for i in range(1, 41)
    )
    body_b = "".join(
        f"考勤第{i}项：员工应当按时上下班并完成每日考勤登记。" for i in range(1, 41)
    )
    document = (
        "**第一条 总则**\n"
        f"{body_a}\n"
        "\n"
        "**第二条 考勤**\n"
        f"{body_b}\n"
    )

    blocks = merge_paragraph_blocks(parse_structured_document(document))
    groups = group_structured_documents(blocks)

    max_tokens = 140
    chunks = [
        chunk
        for group in groups
        for chunk in split_structured_group(
            group,
            tokenizer,
            max_tokens=max_tokens,
            overlap_tokens=40,
        )
    ]

    paragraph_blocks = [block for block in blocks if block["type"] == "paragraph"]
    assert_structural_contract(
        chunks,
        document,
        paragraph_blocks,
        max_tokens,
        tokenizer,
    )
    assert {chunk["clause_title"] for chunk in chunks} == {
        "第一条 总则",
        "第二条 考勤",
    }

    for previous, current in zip(chunks, chunks[1:]):
        if previous["clause_title"] != current["clause_title"]:
            assert previous["source_end"] <= current["source_start"]


def test_whitespace_only_parts_are_merged_into_content(tokenizer):
    sentence = "员工应当遵守考勤制度。"
    text = sentence * 20 + "\n"
    block = make_block(text, 0)
    group = make_group([block])

    max_tokens = 80
    chunks = split_structured_group(
        group,
        tokenizer,
        max_tokens=max_tokens,
        overlap_tokens=20,
    )

    assert_structural_contract(chunks, text, [block], max_tokens, tokenizer)
    assert len(chunks) >= 2
    assert all(chunk["text"].strip() for chunk in chunks)
    assert chunks[-1]["text"].endswith("\n")

    for previous, current in zip(chunks, chunks[1:]):
        overlap_length = previous["source_end"] - current["source_start"]
        assert overlap_length == len(sentence)
        assert current["text"][:overlap_length] == previous["text"][-overlap_length:]


def test_unsplit_short_block_has_no_overlap(tokenizer):
    short_text = "员工应当遵守公司的考勤管理制度。"
    long_text = "".join(
        f"第{i}项：员工应当按时上下班并完成每日考勤登记。" for i in range(1, 41)
    )
    source_text = short_text + long_text
    blocks = [
        make_block(short_text, 0),
        make_block(long_text, len(short_text)),
    ]
    group = make_group(blocks)

    max_tokens = 120
    chunks = split_structured_group(
        group,
        tokenizer,
        max_tokens=max_tokens,
        overlap_tokens=30,
    )

    assert_structural_contract(chunks, source_text, blocks, max_tokens, tokenizer)

    short_chunks = [
        chunk for chunk in chunks if chunk["source_end"] <= len(short_text)
    ]
    assert len(short_chunks) == 1
    assert short_chunks[0]["text"] == short_text
    assert short_chunks[0]["source_start"] == 0
    assert short_chunks[0]["source_end"] == len(short_text)

    next_chunk = chunks[chunks.index(short_chunks[0]) + 1]
    assert next_chunk["source_start"] == len(short_text)
