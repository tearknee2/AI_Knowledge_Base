# verify_embedding
from app.rag.embedding import embed_texts, get_model

# result = embed_texts(
#     [
#         "出差期间因客户、项目或交通原因需变更行程或延期的，员工应提前1个工作日在OA提交变更申请",
#         "紧急情况下可先通过电话、企业微信或邮件请示部门负责人，并在返程后2个工作日内补办"
#     ]
# )
#
# print(result)


result1 = embed_texts(["第一条测试文本"])
model1 = get_model()

result2 = embed_texts(["第二条测试文本"])
model2 = get_model()

assert model1 is model2
assert len(result1) == 1
assert len(result2) == 1

print("模型复用验证通过")