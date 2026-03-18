# 万象智文Omni Intelligent Documents（OmniAI）: AI驱动的文档智能平台

**状态**：✅ MVP已完成 - 文档上传与处理流水线  
**版本**：0.8.0  
**许可证**：专有

> 🌐 **文档站点**：[https://williamjxj.github.io/AgenticOmni](https://williamjxj.github.io/AgenticOmni)  
> 🚀 **快速开始**：见 [docs/quickstart.md](docs/quickstart.md)  
> 📖 **下一步指南**：[docs/next-steps.md](docs/next-steps.md) - 上传 → RAG → 检索

## 📄 概述

万象智文Omni Intelligent Documents（OmniAI）是基于ETL到RAG流水线架构的企业级AI文档智能平台。系统可将复杂多格式文档（PDF、DOCX、TXT）转化为可检索、智能的知识库。

### 🎯 主要特性（v0.8.0）
- 多格式支持：PDF、DOCX、TXT
- 批量上传与异步处理
- 智能分块，优化RAG检索
- 多租户隔离与安全
- 支持本地与S3存储
- 恶意软件扫描与内容去重

### 技术架构
- 后端：FastAPI + PostgreSQL + pgvector
- 前端：Next.js 14 + React + TypeScript + Tailwind CSS
- RAG框架：LangChain, LlamaIndex
- 任务队列：Dramatiq
- 安全：多租户、RBAC、审计日志

## 🚀 快速开始

### 先决条件
- Python 3.12+
- Node.js 18+
- Docker 20+（含Compose）
- Git 2.30+

### 安装步骤
```bash
# 1. 克隆仓库
git clone <repository-url> omniai
cd omniai

# 2. 配置环境变量
cp .env.example .env
# 编辑.env文件

# 3. 启动服务（PostgreSQL + Redis）
docker-compose up -d

# 4. 设置Python环境
python3.12 -m venv venv
source venv/bin/activate
pip install -e .

# 5. 数据库迁移
alembic upgrade head

# 6. 启动后端API
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 7. 启动前端（可选）
cd frontend
npm install
npm run dev
```

### 验证安装
```bash
curl http://localhost:8000/api/v1/health
```

## 📚 文档
- [核心文档](./docs/readme.md)
- [实现说明](./docs/implementation.md)
- [变更日志](./docs/changelog.md)
- [环境配置](./docs/environment.md)
- [前端集成](./docs/frontend.md)
- [生产部署](./docs/production.md)

## 🤝 贡献
- 遵循代码风格（Ruff, mypy）
- 新功能需配套测试（80%覆盖率）
- 文档需同步更新
- 所有更改请通过PR提交

---

**为企业文档智能而生 ❤️**
