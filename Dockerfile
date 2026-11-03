# 后端镜像：FastAPI + RAG
# 构建顺序遵循依赖缓存原则：先 COPY requirements.txt 装依赖，最后才 COPY app/
# 国内服务器构建可加速：
#   docker compose build --build-arg APT_MIRROR=https://mirrors.tuna.tsinghua.edu.cn \
#     --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
#     --build-arg TORCH_WHEELS_URL=https://mirror.nju.edu.cn/pytorch/whl/cpu/torch/
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

ARG APT_MIRROR=https://deb.debian.org

# torch 在 slim 镜像里运行需要 libgomp1（缺它 import torch 直接报错）
RUN sed -i "s|https\?://deb.debian.org|${APT_MIRROR}|g" /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

ARG PIP_INDEX_URL=https://pypi.org/simple
ARG TORCH_WHEELS_URL=https://download.pytorch.org/whl/cpu/

# 先从 PyTorch 源装 CPU 轮子（体积约为 CUDA 版的十分之一），
# 再装 requirements.txt 时 torch==2.14.0 已满足，不会重新拉 CUDA 版
# find-links 而不是 index-url：torch 自带的依赖仍从 PIP_INDEX_URL 解析
COPY requirements.txt .
RUN pip install torch==2.14.0 --find-links ${TORCH_WHEELS_URL} -i ${PIP_INDEX_URL} \
    && pip install -r requirements.txt -i ${PIP_INDEX_URL}

COPY app ./app
COPY init_db.py .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
