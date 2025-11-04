# 刷刷题系统 - 后端

基于 FastAPI 的后端 API 服务。

## 技术栈

- **框架**: FastAPI 0.109+
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **ORM**: SQLAlchemy 2.0+
- **认证**: JWT (PyJWT)
- **密码加密**: bcrypt

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

### 3. 运行服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问：http://localhost:8000

API 文档：http://localhost:8000/docs

## 项目结构

```
backend/
├── app/
│   ├── api/              # API 路由
│   │   ├── v1/           # API v1 版本
│   │   └── deps.py       # 依赖注入
│   ├── core/             # 核心配置
│   │   ├── config.py     # 配置文件
│   │   ├── database.py   # 数据库连接
│   │   └── security.py   # 安全模块
│   ├── models/           # 数据模型
│   ├── schemas/          # Pydantic 模式
│   ├── services/         # 业务逻辑
│   ├── utils/            # 工具函数
│   └── main.py           # 主应用
├── alembic/              # 数据库迁移
├── static/               # 静态文件
├── tests/                # 测试
├── requirements.txt      # 依赖
└── README.md             # 说明文档
```

## 开发进度

- [x] 项目初始化
- [x] 数据库配置
- [x] 数据模型创建
- [x] Pydantic Schemas
- [x] 安全模块（JWT、密码加密）
- [ ] API 路由实现
- [ ] 业务逻辑实现
- [ ] 测试

## 下一步

请按照 `.claude/task-plan.md` 继续开发 API 路由和业务逻辑。
