# chunk_size_overlap
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