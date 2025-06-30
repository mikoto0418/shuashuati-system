# 刷刷题系统 (ShuaShuaTi System)

智能题库管理与练习系统 - 支持文档智能提取、题目管理、练习刷题等功能

## 📋 项目概述

刷刷题系统是一个基于前后端分离架构的智能题库管理与练习平台。系统利用大模型技术，实现对各类题库文档的自动化处理、高效管理和灵活的练习与刷题功能。通过自动化提取、智能分类和多样化的学习模式，帮助用户更好地巩固知识、找出薄弱环节。

## ✨ 核心功能

### 🤖 智能文档处理
- 支持 Word、PDF、图片格式的题库文档上传
- 基于大模型的智能内容提取和题型识别
- 自动结构化处理，支持单选、多选、判断、填空题型

### 📚 题库管理
- 灵活的分类管理系统
- 题目的增删改查操作
- 批量操作和高级筛选
- 手动添加题目功能

### 🎯 练习模式
- **练习模式**：计时练习、错题记录、成绩统计
- **刷题模式**：快速浏览、答案展示、知识点复习
- 收藏夹和错题本功能
- 多种题目排序方式（顺序/乱序）

### 👤 用户系统
- 用户注册、登录、权限管理
- 个人学习数据统计
- 安全的身份认证机制

## 🛠️ 技术栈

### 后端技术
- **语言**: Python 3.9+
- **框架**: Flask
- **数据库**: MySQL + Redis
- **ORM**: SQLAlchemy
- **认证**: JWT Token + bcrypt
- **文件处理**: python-docx, PyPDF2, Pillow
- **任务队列**: Celery + Redis

### 前端技术
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **状态管理**: Pinia
- **UI组件**: Element Plus
- **HTTP客户端**: Axios
- **样式**: SCSS + CSS Modules

## 🏗️ 项目结构

```
shuashuati-system/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   ├── controllers/    # 控制器
│   │   └── utils/          # 工具函数
│   ├── migrations/         # 数据库迁移
│   ├── tests/              # 测试代码
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # 通用组件
│   │   ├── views/          # 页面组件
│   │   ├── stores/         # 状态管理
│   │   ├── services/       # API服务
│   │   └── types/          # TypeScript类型
│   ├── public/             # 静态资源
│   └── package.json        # 前端依赖
├── docs/                   # 项目文档
└── README.md              # 项目说明
```

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+
- MySQL 8.0+
- Redis 6.0+

### 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息

# 初始化数据库
flask db upgrade

# 启动开发服务器
flask run
```

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 📖 API 文档

启动后端服务后，访问 `http://localhost:5000/docs` 查看完整的 API 文档。

### 主要接口

- **用户认证**: `/api/auth/*`
- **题目管理**: `/api/questions/*`
- **分类管理**: `/api/categories/*`
- **文件上传**: `/api/files/*`
- **练习功能**: `/api/practice/*`

## 🗄️ 数据库设计

### 核心表结构

- **users**: 用户信息
- **categories**: 题目分类
- **questions**: 题目内容
- **practice_records**: 练习记录
- **wrong_answers**: 错题本
- **favorites**: 收藏夹
- **upload_records**: 文件上传记录

详细的数据库设计请参考 [需求分析文档.md](./需求分析文档.md)。

## 🔧 配置说明

### 环境变量配置

```env
# 数据库配置
DATABASE_URL=mysql://username:password@localhost/shuashuati
REDIS_URL=redis://localhost:6379/0

# JWT配置
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600

# 大模型API配置
AI_MODEL_API_KEY=your-ai-api-key
AI_MODEL_BASE_URL=https://api.example.com

# 文件存储配置
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
```

## 🧪 测试

### 后端测试

```bash
cd backend
pytest tests/
```

### 前端测试

```bash
cd frontend
npm run test
```

## 📦 部署

### 生产环境部署

1. **后端部署**
   ```bash
   # 使用 Gunicorn 启动
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **前端构建**
   ```bash
   npm run build
   # 将 dist 目录部署到 Nginx
   ```

3. **Nginx 配置**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           root /path/to/frontend/dist;
           try_files $uri $uri/ /index.html;
       }
       
       location /api {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- **Python**: 遵循 PEP 8，使用 Black 格式化
- **Vue/TypeScript**: 使用 ESLint + Prettier
- **Git**: 使用 Conventional Commits 规范

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- 项目地址: [https://github.com/mikoto0418/shuashuati-system](https://github.com/mikoto0418/shuashuati-system)
- 问题反馈: [Issues](https://github.com/mikoto0418/shuashuati-system/issues)

## 🎯 开发路线图

- [x] 项目初始化和基础架构
- [x] 需求分析和技术方案设计
- [ ] 用户认证系统开发
- [ ] 题目和分类管理功能
- [ ] 文件上传和智能提取功能
- [ ] 练习和刷题模式开发
- [ ] 前端界面开发
- [ ] 系统测试和优化
- [ ] 部署和上线

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！