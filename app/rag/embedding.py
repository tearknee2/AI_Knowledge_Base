# embedding
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from pathlib import Path
import os

# 读取项目根目录下的.env
dot_env = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(str(dot_env))

model_path = os.getenv("BGE_MODEL_PATH")

# 模块级变量：一开始还没有加载模型
_model = None

def get_model():
    """获取模型：首次调用时加载，后续调用复用。"""
    global _model

    if _model is None:
        if not model_path:
            raise ValueError("请在.env中配置 BGE_MODEL_PATH")

        _model = SentenceTransformer(model_path)
    return _model

def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    :param texts:接收文本列表
    :return: 返回对应的向量列表
    """
    model = get_model()
    vectors = model.encode(texts)
    return vectors.tolist()