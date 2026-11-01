# AI Knowledge Base — 基于 RAG 的智能知识库应用后端

## 1. 项目介绍

AI Knowledge Base 是一个基于 FastAPI 构建的智能知识库应用后端，集成知识库管理、文档上传与处理、向量存储、检索增强生成（RAG）和大模型问答能力。

项目围绕知识库文档处理与问答两个核心流程展开：

- 支持用户创建和管理知识库。
- 支持上传 TXT 文档，并完成文本读取、清洗、切分和向量化。
- Embedding 模型采用本地 BGE 模型，通过 Sentence Transformers 加载，并使用模块级缓存实现懒加载，避免每次请求重复加载模型。
- 使用 ChromaDB 持久化存储文档向量。
- 基于向量检索召回相关文本片段，并结合文档处理状态进行结果过滤。
- 调用 DeepSeek 大模型生成基于知识库内容的回答。
- 返回答案及对应检索来源，并保存问答记录。

项目重点在于实现一个可运行、可验证的 RAG 应用后端，并通过测试和检索实验验证核心流程。

## 2. 核心功能

### 2.1 知识库管理

- 创建用户。
- 创建知识库。
- 查询用户关联的知识库列表。
- 根据知识库 ID 查询详情。
- 检查知识库是否存在及用户是否具有访问权限。

### 2.2 文档上传与处理

- 支持 TXT 文档上传。
- 保存原始文件并记录文档信息。
- 对文本进行清洗和固定窗口切分。
- 使用 Embedding 模型生成文本向量。
- 将向量及文档元数据写入 ChromaDB。
- 记录文档处理状态。

文档处理状态包括：

`PENDING` → `PARSING` → `CHUNKING` → `EMBEDDING` → `COMPLETED`

处理异常时尝试将文档状态更新为 `FAILED`。

当前读取与文本切分在同一处理流程中执行，PARSING 和 CHUNKING 状态用于表示处理阶段。

### 2.3 RAG 检索问答

- 将用户问题转换为向量。
- 从 ChromaDB 检索候选文本片段。
- 扩大候选召回数量，再过滤非 COMPLETED 文档的检索结果。
- 选取最终文本片段构建上下文。
- 调用大模型生成回答。
- 返回答案、来源文档信息及检索距离。
- 当没有符合条件的检索结果时，直接返回无相关结果提示，不再调用大模型。


### 2.4 对话记录

- 创建或复用会话。
- 保存用户问题。
- 保存助手回答。
- 返回会话 ID、问题、回答和检索来源。

## 3. 技术栈

| 技术 | 用途 |
|---|----|
| Python 3.11 | 项目开发语言 |
| FastAPI | Web API 框架 |
| Pydantic | 请求与响应数据校验 |
| SQLAlchemy | ORM 数据库操作 |
| MySQL | 用户、知识库、文档及会话数据持久化 |
| ChromaDB | 向量持久化与相似度检索 |
| BGE | 本地文本向量化模型 |
| Sentence Transformers | 模型加载与文本向量化 |
| PyTorch | Sentence Transformers 使用的底层深度学习框架 |
| DeepSeek API | RAG问答生成 |
| python-dotenv | 环境变量配置 |
| pytest | 自动化测试 |
| httpx | API 测试支持 |


## 4. 系统架构

项目采用分层组织方式：

```text
                    Client
                      |
                      v
                FastAPI API
                 app/main.py
                      |
                      v
                   Service
              业务逻辑与流程编排
                      |
           +----------+----------+
           |                     |
           v                     v
       Repository             RAG Service
           |                     |
           v              +------+------+
         MySQL             |             |
                           v             v
                       Embedding     ChromaDB
                           |             |
                           +------+------+
                                  |
                                  v
                              Context
                                  |
                                  v
                             DeepSeek API
                                  |
                                  v
                               Answer
```

主要代码层次：

- `core`：数据库连接及配置。
- `models`：数据库 ORM 模型。
- `schemas`：请求和响应数据模型。
- `repositories`：数据访问逻辑。
- `services`：业务逻辑与业务流程编排。
- `rag`：文本处理、向量化、向量存储及问答生成。

说明：目前 API 路由集中定义在 `app/main.py`，尚未拆分为独立 Router 模块。

## 5. 核心业务流程

### 5.1 文档上传与向量化

```text
用户上传 TXT 文档
       |
       v
检查知识库访问权限
       |
       v
保存原始文件
       |
       v
创建 Document 数据记录(PENDING)
       |
       v
进入文档处理流程
       |
       v
更新处理状态并读取 TXT 文件
       |
       v
文本清洗与切分
       |
       v
Embedding 向量化
       |
       v
生成文档版本标识
       |
       v
写入 ChromaDB
       |
       v
校验新版本向量数量
       |
       v
删除旧版本向量
       |
       v
更新文档状态为 COMPLETED
```

**文档版本管理**

向量写入采用版本化 ID：

`doc_{document_id}_{version}_chunk_{i}`

处理新版本时，先写入新版本向量，再查询并校验新版本向量数量，随后清理旧版本向量。

这种方式可以降低文档重新处理时直接覆盖旧数据所带来的风险。

需要注意：MySQL 和 ChromaDB 属于两个独立的数据存储系统，当前没有跨存储原子事务，因此异常情况下仍可能出现状态与向量数据不一致。

### 5.2 RAG 问答

```text
用户提出问题
       |
       v
问题 Embedding
       |
       v
ChromaDB 向量检索
       |
       v
召回候选文本片段
       |
       v
过滤非 COMPLETED 文档
       |
       v
选取 Top-K 结果
       |
       v
构建上下文 Context
       |
       v
调用 DeepSeek API
       |
       v
生成回答
       |
       v
保存问答记录
       |
       v
返回回答及来源
```

当前默认最终检索数量为 `K=4`，候选召回数量为：

`max(n_results * 5, 20)`

即先扩大候选召回范围，再根据文档处理状态过滤，最后选取前 K 条结果。

## 6. 项目目录结构

```text
AI_Knowledge_Base/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   │   ├── user.py
│   │   ├── knowledge_base.py
│   │   ├── document.py
│   │   ├── conversation.py
│   │   └── message.py
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   └── rag/
│       ├── embedding.py
│       ├── vector_store.py
│       ├── txt_loader.py
│       ├── text_cleaner.py
│       ├── chunk_size_overlap.py
│       ├── generation.py
│       └── ...
├── tests/
│   ├── test_load_txt_split_text.py
│   ├── test_smoke.py
│   └── test_split_text.py
├── verify/
│   ├── rag_retrieval_evaluation.md
│   └── ...
├── uploads/                 # 本地上传文件，运行时生成
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

说明：

- `tests/`：自动化测试。
- `verify/`：开发过程中的功能验证脚本及实验记录。
- `uploads/`：本地上传文件目录，不属于正式源码。
- ChromaDB 本地持久化目录属于运行时数据，不纳入源码架构。

## 7. 环境配置与启动

### 7.1 环境要求

- Python 3.11
- MySQL
- DeepSeek API Key
- 本地持久化存储空间

项目当前开发环境：

- Conda 环境：`ai-agent`
- Python：`3.11.16`
- 依赖版本：以 `requirements.txt` 为准

### 7.2 安装依赖

```bash
pip install -r requirements.txt
```

### 7.3 配置环境变量

复制 `.env.example`，创建项目根目录下的 `.env` 文件，并填写实际配置：

```env
APP_NAME=your_app_name

MYSQL_HOST=your_mysql_host
MYSQL_PORT=3306
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=your_database_name

TEST_PASSWORD_HASH=your_test_password_hash

DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
CHROMA_PATH=your_chroma_path
BGE_MODEL_PATH=your_bge_model_path
```

请勿将真实 API Key、数据库密码或其他敏感配置提交到 Git。

其中，`BGE_MODEL_PATH` 用于指定本地 BGE 模型目录，`CHROMA_PATH` 用于指定 ChromaDB 持久化目录。请确保相关路径有效且具有读写权限。

### 7.4 数据库初始化

项目启动前，需要手动完成 MySQL 数据库及数据表的初始化：

1. **创建数据库**：在 MySQL 中手动创建项目所需的数据库（例如 `ai_knowledge_base`）。
2. **创建数据表**：使用 DBeaver 连接 MySQL，逐张执行 MySQL 建表 SQL 脚本，创建项目所需的数据表。
3. **连接数据库**：完成初始化后，配置 `.env` 中的数据库连接信息。项目运行时由 SQLAlchemy 连接已有数据库及数据表，当前项目不使用 Alembic 自动迁移，也不通过 ORM 自动创建数据表。

### 7.5 启动服务

在项目根目录执行：

```bash
uvicorn app.main:app --reload
```

启动后访问：

- 服务入口：`http://127.0.0.1:8000/`
- Swagger API 文档：`http://127.0.0.1:8000/docs`
- ReDoc API 文档：`http://127.0.0.1:8000/redoc`

## 8. API 接口说明

| 方法 | 接口路径 | 功能 |
|---|---|---|
| GET | `/` | 服务入口检查 |
| POST | `/users` | 创建用户 |
| POST | `/knowledge-bases` | 创建知识库 |
| GET | `/knowledge-bases` | 获取知识库列表 |
| GET | `/knowledge-bases/{knowledge_base_id}` | 获取知识库详情 |
| POST | `/knowledge-bases/{knowledge_base_id}/documents` | 上传文档 |
| GET | `/knowledge-bases/{knowledge_base_id}/documents` | 获取文档列表 |
| POST | `/knowledge-bases/{knowledge_base_id}/chat` | 知识库问答 |

详细请求参数、响应结构及状态码以 Swagger 文档为准。

**文档上传**

使用 `multipart/form-data` 提交文件，字段名为 `file`。

**知识库问答**

提交问题及可选的会话 ID，接口返回：

- `conversation_id`：会话 ID。
- `question`：用户问题。
- `answer`：大模型生成的回答。
- `sources`：检索来源信息。

## 9. 测试与实验结果

### 9.1 自动化测试

项目使用 pytest 进行自动化测试，测试代码位于 `tests/` 目录，运行环境为 conda 环境 `ai-agent`（Python 3.11）。测试覆盖五个层次：纯函数（文本切分/加载）、Schema 字段校验、服务层与 RAG 问答链路（mock 隔离向量库与大模型）、ORM 模型与关系（SQLite 内存库）、API 全链路（TestClient + 依赖覆盖，真实服务层与仓储跑在内存库上）。

当前完整测试结果：

```text
100 passed in 14.35s
```

其中 RAG 问答链路测试覆盖：

- 仅使用处理完成的文档。
- 不存在已完成文档时不调用大模型。
- 处理空检索结果。
- 扩大候选召回数量后再进行过滤。

运行测试：

```bash
pytest tests -q
```

### 9.2 检索实验

针对两个项目文档构建测试知识库，验证单事实查询、无答案查询及多事实查询。

**实验一：单事实查询**

问题：云帆计划负责人是谁？

结果：正确检索到包含负责人信息的文档片段，回答为陈思远。

**实验二：无答案查询**

问题：云帆计划后端编程语言是什么？

结果：原始文档没有提供后端编程语言信息。模型明确说明知识库没有相关信息，并指出来源文档未提及该信息，没有直接推测答案。

**实验三：多事实查询**

问题：星河计划和云帆计划的风险上报时限分别是什么？

实验发现：

- K=1、K=2 时，检索结果不能同时覆盖两个项目的答案证据。
- K=3 时，检索结果覆盖两个项目的相关证据，模型正确回答。
- K=4 时，该次实验仍然正确回答。

该实验说明：对于这个具体的多事实问题，检索数量会影响证据覆盖情况；不能据此推断所有问题的最佳 K 值。

**实验四：问题改写对检索结果的影响**

使用三种不同表达方式询问同一事实：

- 云帆计划负责人是谁？
- 谁负责云帆计划？
- 云帆项目的负责人姓名是什么？

实验结果：

三种表达方式均将包含“项目负责人：陈思远”的文档片段召回至 Top-1，模型均正确回答。

实验结论：

在本次测试的三种表达方式下，向量检索均能稳定召回包含正确答案的证据，说明当前检索流程能够处理这几种常见的自然语言表达变化。

需要注意，本次实验仅覆盖同一事实的三种问法，不代表所有问题改写都能获得相同效果。

### 9.3 向量检索配置

当前 ChromaDB 配置：

- ChromaDB：1.5.9
- Collection：`knowledge_chunks_bge_test`
- HNSW 空间度量：`l2`（L2 欧氏距离）
- `ef_construction`：100
- `ef_search`：100
- `max_neighbors`：16

检索结果中的 distance 表示向量距离，不是回答置信度或百分比。当前没有设置统一的距离阈值。

## 10. 当前限制与后续规划

### 当前限制

1. **身份认证尚未完成**：当前使用临时 `user_id=1` 关联用户及检查访问权限，尚未接入完整 JWT 身份认证。
2. **文档格式支持有限**：当前已验证 TXT 文档处理流程，尚未形成完整的 PDF、DOCX 等多格式解析能力。
3. **文本切分方式较基础**：目前采用字符级固定窗口切分，尚未实现完整的结构化或语义切分。
4. **无独立无答案检测机制**：目前主要依赖 Prompt 约束模型回答，不能保证所有情况下都准确拒答。
5. **尚未集成实际 Reranker**：当前检索流程没有接入独立重排序模型。
6. **未设置统一距离阈值**：目前没有基于距离的统一拒答规则。
7. **跨存储一致性有限**：MySQL 与 ChromaDB 之间尚未实现跨存储事务。
8. **部署工程尚待完善**：尚未完成 Docker 容器化及 Linux 环境部署。

### 后续规划

- 完善 JWT 身份认证与用户权限控制。
- 增强文档解析和结构化切分能力。
- 根据实际检索评估结果优化召回与重排序。
- 完善异常处理和跨存储数据一致性。
- 增加 Docker 部署及运行环境配置。

---

## 11. 项目总结

本项目完成了从文档上传、文本处理、向量化、向量存储，到检索增强生成及问答记录保存的核心业务流程。

在 RAG 部分，重点实现了文档处理状态管理、向量版本化写入、新版本数量校验、旧版本清理、候选扩召回及已完成文档过滤，并通过自动化测试和实际检索实验验证了核心行为。

项目目前具备基础知识库管理与 RAG 问答能力，后续将围绕身份认证、检索质量、工程部署和系统可靠性继续完善。