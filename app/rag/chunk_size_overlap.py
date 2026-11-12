# chunk_size_overlap
import re

from app.rag.embedding import get_model


def split_text(text, chunk_size:int, chunk_overlap:int):
    if not isinstance(text,str):
        raise TypeError("Text must be of type str")
    if type(chunk_size) is not int:
        raise TypeError("Chunk size must be of type int")
    if type(chunk_overlap) is not int:
        raise TypeError("Chunk overlap must be of type int")

    result = []
    if chunk_size <= chunk_overlap or chunk_size <=0 or chunk_overlap <0:
        raise ValueError("给出的参数不合法")
    if not text:
        return result
    if len(text) <= chunk_size:
        return [text] if text else []

    for i in range(0, len(text), chunk_size-chunk_overlap):
        result.append(text[i:i+chunk_size])
    return result

def parse_sections(text: str):
    """识别标题和段落"""
    heading_stack = []
    sections = []
    for line in text.split("\n"):
        if not line.strip():
            continue
        if line.startswith("#"):
            level = len(line.split(" ")[0])
            heading_text = line.lstrip("#").strip()
            while heading_stack and heading_stack[-1][0]>=level:
                heading_stack.pop()
            heading_stack.append((level, heading_text))
        else:
            sections.append(
                {
                    "section_path":[
                        heading_stack[i][1]
                        for i in range(len(heading_stack))
                    ],
                    "paragraph":line.strip()
                }
            )
    return sections

def merge_paragraphs(sections, chunk_size):
    """合并同一章节内较短的段落"""
    merged_chunks = []
    current_chunk = ""
    current_section_path = []

    for section in sections:
        new_paragraph = section["paragraph"]
        new_section_path = section["section_path"]
        if (
            current_chunk != ""
            and current_section_path == new_section_path
            and len(current_chunk) + 2 + len(new_paragraph) <= chunk_size
        ):
                current_chunk = current_chunk+"\n\n"+new_paragraph
                current_section_path = new_section_path
        else:
            if current_chunk != "":
                merged_chunks.append({
                    "section_path":current_section_path,
                    "text":current_chunk
                })
            current_chunk = new_paragraph
            current_section_path = new_section_path
    if current_chunk != "":
        merged_chunks.append({
            "section_path": current_section_path,
            "text": current_chunk
        })

    return merged_chunks

def split_long_paragraph(text: str, chunk_size, chunk_overlap):
    """拆分过长的单个段落"""
    if not isinstance(text, str):
        raise TypeError("Text must be of type str")
    if type(chunk_size) is not int:
        raise TypeError("Chunk size must be of type int")
    if type(chunk_overlap) is not int:
        raise TypeError("Chunk overlap must be of type int")
    result = []
    if chunk_size <= chunk_overlap or chunk_size <=0 or chunk_overlap <0:
        raise ValueError("给出的参数不合法")
    if not text:
        return result
    if len(text) <= chunk_size:
        return [text] if text else []
    for start in range(0, len(text),chunk_size-chunk_overlap):
        result.append(text[start:start+chunk_size])
        if start + chunk_size >= len(text):
            break
    return result

def build_chunks(text, chunk_size=500, chunk_overlap=50):
    sections = parse_sections(text)
    merged_chunks = merge_paragraphs(sections, chunk_size)
    new_chunks = []
    for item in merged_chunks:
        section_path = item["section_path"]
        chunk_text = item["text"]
        result = split_long_paragraph(chunk_text, chunk_size, chunk_overlap)
        for i in result:
            new_chunks.append({
                "section_path":section_path,
                "text":i
            })
    return new_chunks

def is_heading(line):
    pattern = r"^(#{1,6})\s+(.+?)\s*#*\s*$"
    match = re.match(pattern, line)

    if match and match.group(2).strip():
        hashes = match.group(1)
        level = len(hashes)
        return level
    return None

def is_clause(line):
    pattern = r"^\*\*(第[一二三四五六七八九十百千万零〇两]+条)\s+(.+?)\*\*$"
    match = re.match(pattern, line)
    if match and match.group(2).strip():
        clause_title = f"{match.group(1)} {match.group(2).strip()}"
        return clause_title
    return None

def parse_structured_document(text):
    """逐行扫描，识别结构，记录原文位置"""
    lines = text.splitlines(keepends=True)
    blocks = []
    current_offset = 0

    # 逐行扫描
    for line in lines:
        # 记录每行的source_start和source_end
        source_start = current_offset
        source_end = source_start + len(line)

        level = is_heading(line)
        clause_title = is_clause(line)

        if not line.strip():
            blocks.append({
                "type": "blank",
                "text": line,
                "source_start": source_start,
                "source_end": source_end,
            })
        elif level is not None:
            heading_match = re.match(
                r"^#{1,6}\s+(.+?)\s*#*\s*$",
                line.strip()
            )
            heading_title = heading_match.group(1).strip()

            pattern = r"^(第[一二三四五六七八九十百千万零〇两]+条)\s+(.+?)$"

            if re.match(pattern, heading_title):
                blocks.append({
                    "type": "heading",
                    "text": line,
                    "source_start": source_start,
                    "source_end": source_end,
                    "level": level,
                    "clause_title": heading_title
                })
            else:
                blocks.append({
                    "type": "heading",
                    "text": line,
                    "source_start": source_start,
                    "source_end": source_end,
                    "level": level,
                })
        elif clause_title is not None:
            blocks.append({
                "type": "clause",
                "text": line,
                "source_start": source_start,
                "source_end": source_end,
                "clause_title": clause_title,
            })
        else:
            blocks.append(
                {
                    "type": "paragraph",
                    "text": line,
                    "source_start":source_start,
                    "source_end":source_end,
                }
            )
        current_offset += len(line)
    return blocks

def merge_paragraph_blocks(blocks):
    """把连续的 paragraph 合并成一个段落结构单元"""
    merged_blocks = []
    current_paragraph = None
    for block in blocks:
        if (
            block["type"] == "blank"
            or block["type"] == "heading"
            or block["type"] == "clause"
        ):
            if current_paragraph is not None:
                merged_blocks.append(current_paragraph)
            current_paragraph = None
            merged_blocks.append(block.copy())
        elif block["type"] == "paragraph":
            if current_paragraph is None:
                current_paragraph = block.copy()
            else:
                current_paragraph["text"] += block["text"]
                current_paragraph["source_end"] = block["source_end"]
    if current_paragraph is not None:
        merged_blocks.append(current_paragraph)
    return merged_blocks

def flush_current_group(current_group, groups):
    # 如果当前组存在，而且里面有正文
    # 就把他保存到groups
    if current_group is not None and current_group["blocks"]:
        groups.append(current_group)
    # 然后清空当前组
    current_group = None
    return groups, current_group


def group_structured_documents(blocks):
    groups = []
    section_path = []
    current_clause = None
    current_group = None

    for block in blocks:
        if block["type"] == "paragraph":
            if current_group is None:
                # 创建新组
                current_group ={
                    "section_path": section_path.copy(),
                    "clause_title": current_clause,
                    "blocks": []
                }
            # 把正文放入当前组
            current_group["blocks"].append(block)
        elif block["type"] == "heading":
            # # 提交旧组，更新章节路径，重置current_clause
            groups, current_group = flush_current_group(current_group, groups)

            if "clause_title" in block:
                current_clause = block["clause_title"]
            else:
                # 保留当前标题层级之前的路径
                section_path = section_path[:block["level"] - 1]
                # 添加当前heading
                match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", block["text"].strip())
                heading_title = match.group(1).strip()
                section_path.append(heading_title)

                # 重置当前条款标题
                current_clause = None
        elif block["type"] == "clause":
            # 先提交旧组
            # 再更新条款标题
            groups, current_group = flush_current_group(current_group, groups)
            current_clause = block["clause_title"]
    groups, current_group = flush_current_group(
        current_group, groups
    )
    return groups



def count_tokens(text, tokenizer):
    """对文本编码并统计总长度(含特殊token)"""
    token_ids = tokenizer.encode(text, add_special_tokens=True)
    return len(token_ids)

def build_embedding_text(group, text):
    """在不丢失正文、不跨越当前 Group 边界的前提下，把正文切成符合 Token 长度限制的 Chunk"""
    section_path = " > ".join(group["section_path"])

    if group["clause_title"] is not None:
        section_path += " > " + group["clause_title"]

    embedding_text = section_path + "\n" + text

    return embedding_text

def build_chunk_embedding_text(chunk):
    """使用 Chunk 自带的结构信息生成 embedding_text"""
    return build_embedding_text(chunk, chunk["text"])


def create_chunk(group, paragraph):
    return {
        "section_path": group["section_path"].copy(),
        "clause_title": group["clause_title"],
        "text": paragraph["text"],
        "source_start": paragraph["source_start"],
        "source_end": paragraph["source_end"],
    }


_SENTENCE_SEPARATORS = ("\n\n", "\n", "。", "！", "？", "；")
_CLAUSE_SEPARATORS = ("，", "、", "：")


def _separator_cuts(text, separators):
    """返回分隔符之后的字符位置，按位置升序排列（越靠前重叠越长）"""
    cuts = set()
    for separator in separators:
        start = 0
        while True:
            position = text.find(separator, start)
            if position == -1:
                break
            end = position + len(separator)
            if end < len(text):
                cuts.add(end)
            start = end
    return sorted(cuts)


def _select_separator_overlap(
    previous_text,
    current_text,
    tokenizer,
    prefix,
    overlap_tokens,
    max_tokens,
    separators,
):
    for cut in _separator_cuts(previous_text, separators):
        overlap = previous_text[cut:]
        if not overlap.strip():
            continue
        if len(tokenizer.encode(overlap, add_special_tokens=False)) > overlap_tokens:
            continue
        if count_tokens(prefix + overlap + current_text, tokenizer) <= max_tokens:
            return overlap
    return ""


def _select_token_overlap(
    previous_text,
    current_text,
    tokenizer,
    prefix,
    overlap_tokens,
    max_tokens,
):
    """没有语义分隔符可用时，退回到 Token 边界，避免按固定字符数截断"""
    offsets = tokenizer(
        previous_text,
        add_special_tokens=False,
        return_offsets_mapping=True,
    )["offset_mapping"]

    for window in range(min(overlap_tokens, len(offsets)), 0, -1):
        start = offsets[-window][0]
        if start <= 0:
            continue
        overlap = previous_text[start:]
        if not overlap.strip():
            continue
        if count_tokens(prefix + overlap + current_text, tokenizer) <= max_tokens:
            return overlap
    return ""


def _merge_whitespace_parts(parts):
    """把纯空白片段并入相邻正文，避免生成只含换行的 Chunk"""
    merged = []
    pending = ""

    for part in parts:
        if part.strip():
            merged.append(pending + part)
            pending = ""
        elif merged:
            merged[-1] += part
        else:
            pending += part

    if pending:
        merged.append(pending)

    return merged


def _select_overlap(
    previous_text,
    current_text,
    tokenizer,
    prefix,
    overlap_tokens,
    max_tokens,
):
    if overlap_tokens <= 0 or not previous_text:
        return ""

    for separators in (_SENTENCE_SEPARATORS, _CLAUSE_SEPARATORS):
        overlap = _select_separator_overlap(
            previous_text,
            current_text,
            tokenizer,
            prefix,
            overlap_tokens,
            max_tokens,
            separators,
        )
        if overlap:
            return overlap

    # 上一块本身就是一句完整正文时，优先整句重叠，避免从句子中间开始
    previous_token_count = len(
        tokenizer.encode(previous_text, add_special_tokens=False)
    )
    if (
        previous_token_count <= overlap_tokens
        and count_tokens(prefix + previous_text + current_text, tokenizer)
        <= max_tokens
    ):
        return previous_text

    return _select_token_overlap(
        previous_text,
        current_text,
        tokenizer,
        prefix,
        overlap_tokens,
        max_tokens,
    )


def split_structured_group(
    group,
    tokenizer,
    target_tokens=350,
    max_tokens=480,
    overlap_tokens=64,
):
    chunks = []

    if type(overlap_tokens) is not int:
        raise TypeError("Overlap tokens must be of type int")
    if overlap_tokens < 0:
        raise ValueError("Overlap tokens must not be negative")
    if overlap_tokens >= max_tokens:
        raise ValueError("Overlap tokens must be smaller than max_tokens")

    for block in group["blocks"]:
        embedding_text = build_embedding_text(group, block["text"])
        count_token = count_tokens(embedding_text, tokenizer)

        if count_token <= max_tokens:
            chunks.append(create_chunk(group, block))
            continue

        cursor = 0
        previous_text = None
        prefix = build_embedding_text(group, "")
        split_budget = max_tokens - overlap_tokens
        parts = _merge_whitespace_parts(
            split_text_recursively(
                block["text"],
                tokenizer,
                split_budget,
                prefix=prefix,
            )
        )

        for part in parts:
            overlap = ""
            if previous_text is not None:
                overlap = _select_overlap(
                    previous_text,
                    part,
                    tokenizer,
                    prefix,
                    overlap_tokens,
                    max_tokens,
                )

            source_start = block["source_start"] + cursor - len(overlap)
            source_end = block["source_start"] + cursor + len(part)
            paragraph = {
                "text": overlap + part,
                "source_start": source_start,
                "source_end": source_end,
            }
            chunks.append(create_chunk(group, paragraph))
            cursor += len(part)
            previous_text = part
        assert cursor == len(block["text"])

    return chunks

def split_by_separator(text, separator):
    """按照指定分隔符切分文本，同时保留分隔符"""
    parts = []
    while text:
        position = text.find(separator)
        if position == -1:
            parts.append(text)
            break
        end_position = position + len(separator)
        part1 = text[:end_position]
        part2 = text[end_position:]
        parts.append(part1)
        text = part2

    return parts

def hard_split(text, tokenizer, max_tokens, prefix=""):
    special_token_count = tokenizer.num_special_tokens_to_add(pair=False)
    available_tokens = max_tokens - special_token_count

    if available_tokens <= 0:
        raise ValueError("max_tokens is too small")

    parts = []
    remaining = text

    while remaining:
        result = tokenizer(
            prefix + remaining,
            add_special_tokens=False,
            return_offsets_mapping=True
        )
        input_ids = result["input_ids"]
        offset_mapping = result["offset_mapping"]
        token_count = len(input_ids)

        if token_count <= available_tokens:
            parts.append(remaining)
            break

        body_cut_position = None

        for start, end in offset_mapping[:available_tokens]:
            if start >= len(prefix) and end > start:
                body_cut_position = end - len(prefix)

        if body_cut_position is None or body_cut_position <= 0:
            raise ValueError("无法在当前 Token 预算内找到合法的正文切分位置")

        parts.append(remaining[:body_cut_position])
        remaining = remaining[body_cut_position:]

    return parts

def split_text_recursively(
    text,
    tokenizer,
    max_tokens,
    prefix="",
    separators=None,
):
    """
    :param text:当前需要处理的正文
    :param tokenizer: BGE分词器
    :param max_tokens: 完整embedding_text上限
    :param prefix: 结构路径
    :param separators: 递归切分的分隔符优先级
    :return: list[str]只返回正文，不含prefix，包含原始分隔符和空白字符
    """
    # 1.判断完整embedding_text是否超限
    input_ids = tokenizer(
        prefix + text,
        add_special_tokens=False,
        return_offsets_mapping=True
    )["input_ids"]
    token_count = len(input_ids)

    special_tokens_count = tokenizer.num_special_tokens_to_add(pair=False)
    available_tokens = max_tokens - special_tokens_count
    if available_tokens <= 0:
        raise ValueError("max_tokens is too small")
    # 2.如果没有超限，直接返回[text]
    if token_count <= available_tokens:
        return [text]
    # 3.如果超限，进入分隔符切分逻辑
    if separators is None:
        separators = ["\n\n", "\n", "。", "！", "？", "；"]

    chunks = []

    for index, separator in enumerate(separators):
        parts = split_by_separator(text, separator)

        if len(parts) <= 1:
            continue

        for part in parts:
            part_ids = tokenizer(
                prefix + part,
                add_special_tokens=False,
                return_offsets_mapping=True
            )["input_ids"]

            part_count = len(part_ids)

            if part_count <= available_tokens:
                chunks.append(part)
            else:
                results = split_text_recursively(
                    part,
                    tokenizer,
                    max_tokens,
                    prefix=prefix,
                    separators=separators[index+1:],
                )
                for result in results:
                    chunks.append(result)
        return chunks
    return hard_split(text, tokenizer, max_tokens, prefix=prefix)

