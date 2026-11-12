from app.rag.chunk_size_overlap import (
    split_text_recursively,
    count_tokens,
)
from app.rag.embedding import get_model

model = get_model()
tokenizer = model.tokenizer
# text = (
#     "第一段：员工应当遵守公司的考勤管理制度，按时上下班。\n\n"
#     "第二段：员工因特殊情况需要请假的，应当提前提交请假申请。\n\n"
#     "第三段：未经批准擅自缺勤的，按照公司的相关规定处理。\n\n"
# ) * 30
#
# prefix = "员工管理制度 > 考勤管理\n"
# max_tokens = 80
#
# chunks = split_text_recursively(
#     text,
#     tokenizer,
#     max_tokens,
#     prefix=prefix,
# )
#
# # 1. 验证正文完整性
# assert "".join(chunks) == text
#
# # 2. 验证没有空块
# assert all(chunk for chunk in chunks)
#
# # 3. 验证每个 Chunk 的完整 embedding_text 不超限
# token_counts = [
#     count_tokens(prefix + chunk, tokenizer)
#     for chunk in chunks
# ]
#
# assert all(count <= max_tokens for count in token_counts)
#
# print("Chunk 数量：", len(chunks))
# print("最大 Token 数：", max(token_counts))
# print("最小 Token 数：", min(token_counts))
# print("正文完整还原：", "".join(chunks) == text)
# print("Token 上限检查：", all(count <= max_tokens for count in token_counts))


clause = "员工应当遵守公司的考勤管理制度，并按照规定完成每日考勤登记"

sentence = "；".join([clause] * 3) + "。"

paragraph = sentence * 2

text = "\n\n".join([paragraph] * 2)

prefix = "员工管理制度 > 考勤管理\n"
max_tokens = 80

chunks = split_text_recursively(
    text,
    tokenizer,
    max_tokens,
    prefix=prefix,
)

token_counts = [
    count_tokens(prefix + chunk, tokenizer)
    for chunk in chunks
]

assert "".join(chunks) == text
assert all(count <= max_tokens for count in token_counts)

print("Chunk 数量：", len(chunks))
print("最大 Token 数：", max(token_counts))
print("正文完整还原：", "".join(chunks) == text)
print("Token 上限检查：", all(count <= max_tokens for count in token_counts))






