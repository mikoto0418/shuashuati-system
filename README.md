# 刷刷题 - 智能刷题系统

一个基于Flask和AI技术的智能刷题系统，支持从文档中自动提取题目并生成练习。

## ✨ 主要功能

### 🎯 核心功能
- **用户管理**: 注册、登录、个人资料管理
- **题库管理**: 题目分类、增删改查、批量导入
- **智能练习**: 随机练习、分类练习、错题重练
- **收藏系统**: 收藏重要题目，便于复习

### 🤖 AI智能提取
- **多格式支持**: Word文档(.docx)、PDF文件(.pdf)、图片(.png/.jpg/.jpeg)、纯文本(.txt)
- **智能解析**: 自动识别题目类型（单选、多选、判断、填空、问答）
- **质量优化**: AI自动优化题目表述和选项
- **批量处理**: 一次上传，批量提取多个题目
- **历史管理**: 查看上传历史和处理结果
- **实时监控**: 实时显示AI处理进度和思考过程

## 🏗️ 技术栈

### 后端
- **框架**: Flask 2.3.3
- **数据库**: SQLite (开发) / MySQL (生产)
- **ORM**: SQLAlchemy
- **认证**: Flask-Login
- **API**: RESTful API
- **AI服务**: 硅基流动 DeepSeek API

### 前端
- **框架**: Vue 3 + TypeScript
- **UI库**: Element Plus
- **构建工具**: Vite
- **样式**: 响应式设计

## 📁 项目结构

```
刷刷题-shuashuati/
├── backend/                 # 后端代码
│   ├── app.py              # Flask应用主文件
│   ├── config.py           # 配置文件
│   ├── models.py           # 数据库模型
│   ├── services/           # 业务逻辑服务
│   │   ├── ai_service.py   # AI题目提取服务
│   │   ├── document_parser.py # 文档解析服务
│   │   └── file_processor.py  # 文件处理服务
│   ├── routes/             # API路由
│   ├── requirements.txt    # Python依赖
│   └── uploads/            # 文件上传目录
├── frontend-vue/           # Vue前端代码
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── components/     # 通用组件
│   │   ├── stores/         # 状态管理
│   │   └── utils/          # 工具函数
│   ├── package.json        # 前端依赖
│   └── vite.config.ts      # Vite配置
├── start_backend.py        # 后端启动脚本
├── 需求分析文档.md          # 项目需求文档
├── 项目进度分析.md          # 项目进度规划
└── README.md               # 项目说明文档
```

## 🚀 快速开始

### 环境要求

- Python 3.7+
- Node.js 16+
- 现代浏览器（Chrome、Firefox、Safari、Edge）

### AI服务配置

本系统使用硅基流动的DeepSeek模型进行题目提取，需要配置API密钥：

1. 访问 [硅基流动开放平台](https://siliconflow.cn/)
2. 注册账号并获取API密钥
3. 在 `backend/.env` 文件中配置:
```
SILICONFLOW_API_KEY=your-api-key-here
```

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/mikoto0418/shuashuati-system.git
   cd shuashuati-system
   ```

2. **后端设置**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **前端设置**
   ```bash
   cd frontend-vue
   npm install
   ```

4. **启动服务**
   ```bash
   # 启动后端（在backend目录）
   python app.py
   
   # 启动前端（在frontend-vue目录）
   npm run dev
   ```

5. **访问应用**
   - 前端：http://localhost:3000
   - 后端API：http://localhost:5000

## 📋 最新更新

### ✅ 2025年1月 - 实时处理监控优化

- [x] **修复文档处理卡顿问题**
  - 优化前端进度监控机制
  - 实现处理日志自动刷新
  - 用户可实时查看AI思考过程

- [x] **增强用户体验**
  - 自动刷新处理日志（每1.5秒）
  - 实时显示AI分析步骤
  - 透明的处理进度展示

### 🚧 开发中功能

- [ ] MySQL数据库支持
- [ ] 批量题目导入优化
- [ ] 题目质量评估系统
- [ ] 用户练习数据分析

## 🔧 开发指南

### 核心特性

1. **智能文档解析**：支持多种格式文档的智能解析
2. **AI题目提取**：使用先进AI模型自动提取和优化题目
3. **实时处理监控**：用户可实时查看文档处理进度和AI思考过程
4. **完整的日志系统**：详细记录每个处理步骤，便于调试和优化

### 技术亮点

- **前后端分离**：Vue3 + Flask架构，便于维护和扩展
- **实时通信**：前端轮询机制实现实时状态更新
- **模块化设计**：服务层清晰分离，便于功能扩展
- **错误处理**：完善的异常处理和用户提示机制

## 🐛 故障排除

### 常见问题

1. **后端启动失败**
   ```bash
   # 检查Python版本
   python --version
   
   # 重新安装依赖
   pip install -r requirements.txt
   ```

2. **前端无法连接后端**
   - 确认后端服务运行在 http://localhost:5000
   - 检查前端配置文件中的API地址

3. **AI服务调用失败**
   - 检查 `.env` 文件中的API密钥配置
   - 确认网络连接正常

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- GitHub Issues: [提交问题](https://github.com/mikoto0418/shuashuati-system/issues)
- 项目维护者: mikoto0418

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。