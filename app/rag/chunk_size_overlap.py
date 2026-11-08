# chunk_size_overlap
import re


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

file = r"C:\Users\tear_knee\Desktop\01_员工管理制度.txt"

with open(file, encoding="utf-8") as f:

    text = f.read()

    parsed_blocks = parse_structured_document(text)

    merged_blocks = merge_paragraph_blocks(parsed_blocks)

    groups = group_structured_documents(merged_blocks)

    print("原始文本长度：", len(text))
    print("Parser 输出数量：", len(parsed_blocks))
    print("Merge 输出数量：", len(merged_blocks))
    print("Grouping 输出数量：", len(groups))

    for index, group in enumerate(groups):
        print(f"\n第 {index + 1} 组")
        print("章节路径：", group["section_path"])
        print("条款标题：", group["clause_title"])
        print("正文块数量：", len(group["blocks"]))

    for index, group in enumerate(groups):
        print(f"\n========== 第 {index + 1} 组正文 ==========")

        for block in group["blocks"]:
            print(block["text"], end="")

    # 检查正文块是否完整归组
    paragraph_blocks = [
        block for block in merged_blocks
        if block["type"] == "paragraph"
    ]

    grouped_blocks = [
        block
        for group in groups
        for block in group["blocks"]
    ]

    print("Merge 后正文块数量：", len(paragraph_blocks))
    print("Grouping 后正文块数量：", len(grouped_blocks))

    assert len(paragraph_blocks) == len(grouped_blocks)
    assert paragraph_blocks == grouped_blocks

    print("正文完整性检查通过！")







