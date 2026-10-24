from sentence_transformers import SentenceTransformer


model_path = r'C:\Users\tear_knee\.cache\huggingface\hub\models--BAAI--bge-small-zh-v1.5\snapshots\7999e1d3359715c523056ef9478215996d62a620'
# 指向你的本地模型路径

model = SentenceTransformer(model_path)

texts = [
    "Python是一种编程语言",
    "Python支持多种编程范式"
]

embeddings = model.encode(texts)

print("文本数量:",len(texts))
print("向量形状：",embeddings.shape)
print("第一条向量的前10个数值：",embeddings[0][:10])

from sentence_transformers import util

similarity = util.cos_sim(
    embeddings[0],
    embeddings[1]
)
print("两条文本的余弦相似度：",similarity.item())