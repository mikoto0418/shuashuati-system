# Shuashuati 刷刷题 ✨

<p align="center">
  <a href="#-简体中文">🇨🇳 简体中文</a> |
  <a href="#-english">🇺🇸 English</a>
</p>

## 🇨🇳 简体中文

### 项目简介 🧠
刷刷题是一个帮助个人与团队构建题库、开展针对性刷题训练的全栈平台。前端提供练习中心、仪表盘、错题本等交互体验，后端提供稳定的 API、账号体系与题目解析能力。

### 核心特性 🌟
- **智能练习中心**：多模式练习（智能、巩固、错题回顾等），实时展示进度、正确率与练习统计。
- **题库管理**：支持题目增删改查、分类管理、批量导入与列表分页检索。
- **文件与 AI 解析**：上传 Word/PDF/图片自动切题，内置基础与 AI 混合解析流程。
- **错题本与收藏夹**：一键归档错题、收藏题目，辅助复习回顾。
- **权限与审计**：JWT 鉴权、管理员视图、解析任务日志，保障账户与数据安全。

### 技术架构 🏗️
- `frontend/`：Vue 3 · TypeScript · Vite · Naive UI · Pinia · Axios。
- `backend/`：FastAPI · SQLAlchemy · Alembic · JWT · SQLite（默认）/ PostgreSQL（推荐生产）。
- `parsing/AI`：pdfplumber、python-docx、Pillow/pytesseract、OpenAI API（可配置）。

### 快速开始 🚀
#### 后端（FastAPI）
依赖：Python 3.11+、SQLite（内置）或 PostgreSQL。

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows 使用 .\.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Windows 使用 copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端（Vite + Vue 3）
依赖：Node.js 18+、npm 9+。

```bash
cd frontend
npm install
# 若需调整接口地址，请创建/编辑 `.env.local` 并设置 VITE_API_BASE_URL
npm run dev
```

> 默认前端通过 `VITE_API_BASE_URL` 访问 `http://localhost:8000/api/v1`，请根据后端实际地址调整。

### 系统运行指南 🧭
1. 启动后端：在 `backend/` 目录执行 `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`。
2. 启动前端：在 `frontend/` 目录执行 `npm run dev`，访问终端输出的本地地址（默认 `http://localhost:5173`）。
3. 如需生产部署，可使用 `npm run build` 生成静态资源并配置 Nginx/反向代理指向 FastAPI 服务。

### 常用脚本 🛠️
- `npm run build`：生成前端生产构建产物（位于 `frontend/dist`）。
- `npm run preview`：本地预览已构建站点。
- `pytest`：执行后端测试（需在虚拟环境中运行）。
- `alembic revision --autogenerate` / `alembic upgrade head`：维护数据库迁移。

### 目录结构 🗂️
```text
.
├── backend/
│   ├── app/                # FastAPI 应用与业务逻辑
│   ├── alembic/            # 数据库迁移脚本
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/                # Vue 3 应用源码
│   ├── package.json
│   └── vite.config.ts
└── README.md               # 本文档
```

### 开源许可 📝
本项目依据 [MIT License](./LICENSE) 开源，欢迎遵循许可条款进行使用与分发。

---

## 🇺🇸 English

### Overview 🧠
Shuashuati is a full-stack practice platform that helps individuals and teams build question banks and run focused study sessions. The web client ships dashboards, practice center, and review tools, while the FastAPI backend delivers secure APIs, authentication, and document-to-question parsing.

### Highlights
- **Adaptive Practice Center**: Multiple drill modes (smart, consolidation, wrong-book review) with live progress and accuracy indicators.
- **Question Bank Management**: CRUD operations, category management, bulk import, and paginated search.
- **Document & AI Parsing**: Upload Word/PDF/images, auto-split questions via basic or AI-assisted workflows.
- **Wrong-Book & Favorites**: Capture mistakes, bookmark important questions, and revisit them anytime.
- **Security & Auditing**: JWT authentication, admin views, and task logging to keep data safe.

### Tech Stack 🧰
- `frontend/`: Vue 3 · TypeScript · Vite · Naive UI · Pinia · Axios.
- `backend/`: FastAPI · SQLAlchemy · Alembic · JWT · SQLite (default) / PostgreSQL (recommended for production).
- `parsing/AI`: pdfplumber, python-docx, Pillow/pytesseract, OpenAI API (configurable provider).

### Quick Start ⚡
#### Backend (FastAPI)
Prerequisites: Python 3.11+, SQLite (bundled) or PostgreSQL.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows use .\.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # On Windows run copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend (Vite + Vue 3)
Prerequisites: Node.js 18+, npm 9+.

```bash
cd frontend
npm install
# Create or edit `.env.local` and set VITE_API_BASE_URL when overriding the API endpoint
npm run dev
```

> The frontend consumes the backend at `VITE_API_BASE_URL` (defaults to `http://localhost:8000/api/v1`). Update it to match your environment.

### Run the Stack 🧭
1. Start the backend with `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.
2. Start the frontend with `npm run dev` inside `frontend/` and open the printed URL (default `http://localhost:5173`).
3. For production, run `npm run build` and serve `frontend/dist` behind your preferred web server and proxy traffic to FastAPI.

### Useful Scripts 🔧
- `npm run build`: produce the production bundle under `frontend/dist`.
- `npm run preview`: locally preview the built site.
- `pytest`: run backend test suites (activate the virtualenv first).
- `alembic revision --autogenerate` / `alembic upgrade head`: maintain database migrations.

### Project Layout 🗂️
```text
.
├── backend/
│   ├── app/                # FastAPI application & domain logic
│   ├── alembic/            # Database migrations
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/                # Vue 3 source code
│   ├── package.json
│   └── vite.config.ts
└── README.md               # This document
```

### License 📝
Released under the [MIT License](./LICENSE). Feel free to use and distribute in compliance with the terms.
