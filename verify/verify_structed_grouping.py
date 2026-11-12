from app.rag.chunk_size_overlap import parse_structured_document, merge_paragraph_blocks, group_structured_documents

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
