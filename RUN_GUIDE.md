# English Trainer - 项目运行指南

## 🚀 快速开始

### 方式1：直接打开前端界面（最简单）

直接在文件资源管理器中双击以下文件：

```
frontend\index.html
```

或者在命令行中运行：

```bash
start frontend\index.html
```

### 方式2：使用启动脚本

双击运行项目根目录下的启动脚本：

```
start-project.bat
```

这个脚本会自动：
1. 检查Python和Node.js环境
2. 启动后端服务（端口8000）
3. 启动前端开发服务器（端口3000）

### 方式3：手动启动

#### 启动后端服务

```bash
cd backend

# 创建虚拟环境（首次运行）
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖（首次运行）
pip install -r requirements/development.txt

# 启动后端服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 启动前端服务

```bash
cd frontend

# 安装依赖（首次运行）
npm install

# 启动前端开发服务器
npm run dev
```

## 📋 环境要求

### 必需
- **Python 3.11+** - 后端服务
- **Node.js 18+** - 前端开发服务器（可选）

### 可选
- **Docker** - 容器化部署
- **Git** - 版本控制

## 🔧 环境配置

### 后端环境变量

创建 `backend\.env` 文件：

```env
APP_NAME=English Trainer API
APP_VERSION=1.0.0
DEBUG=true

DATABASE_URL=postgresql+asyncpg://english_trainer:english_trainer_password@localhost:5432/english_trainer_dev
REDIS_URL=redis://localhost:6379/0

JWT_SECRET_KEY=dev_secret_key_change_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

OPENAI_API_KEY=your_openai_api_key_here
AZURE_SPEECH_KEY=your_azure_speech_key_here
AZURE_SPEECH_REGION=eastus
STRIPE_SECRET_KEY=your_stripe_secret_key_here

CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
```

### 数据库设置

#### 使用Docker（推荐）

```bash
docker-compose up -d
```

#### 使用本地PostgreSQL

确保PostgreSQL运行并创建数据库：

```sql
CREATE DATABASE english_trainer_dev;
CREATE USER english_trainer WITH PASSWORD 'english_trainer_password';
GRANT ALL PRIVILEGES ON DATABASE english_trainer_dev TO english_trainer;
```

## 🌐 访问地址

启动成功后，可以通过以下地址访问：

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **数据库**: localhost:5432
- **Redis**: localhost:6379

## 📱 界面功能

### 登录页面
- 用户登录
- 创建账户

### 仪表板
- 学习统计
- 进度追踪
- 最近练习

### 场景列表
- 浏览练习场景
- 按难度筛选
- 搜索功能

### 练习界面
- AI对话练习
- 语音识别
- 实时反馈

## 🐛 常见问题

### 端口被占用

如果端口被占用，修改端口配置：

**后端端口** (backend/app/main.py):
```python
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**前端端口** (frontend/vite.config.js):
```javascript
server: {
  port: 3001,
  // ...
}
```

### 依赖安装失败

**Python依赖**:
```bash
pip install --upgrade pip
pip install -r requirements/development.txt
```

**Node.js依赖**:
```bash
npm cache clean --force
npm install
```

### 数据库连接失败

检查PostgreSQL服务状态：
```bash
# Windows
net start postgresql-x64-15

# 检查连接
psql -U english_trainer -d english_trainer_dev
```

## 📊 监控和日志

### 后端日志
后端服务会在终端显示实时日志，包括：
- API请求
- 数据库查询
- 错误信息

### 前端日志
浏览器开发者工具 (F12) 可以查看：
- 控制台日志
- 网络请求
- 性能指标

## 🔄 数据库迁移

如果需要更新数据库结构：

```bash
cd backend

# 激活虚拟环境
venv\Scripts\activate

# 创建迁移
alembic revision --autogenerate -m "description"

# 应用迁移
alembic upgrade head
```

## 🧪 测试

### 后端测试
```bash
cd backend
pytest
```

### 前端测试
```bash
cd frontend
npm test
```

## 📦 生产部署

### 使用Docker
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 手动部署
1. 设置环境变量
2. 运行数据库迁移
3. 启动后端服务
4. 构建前端：`npm run build`
5. 使用nginx等Web服务器托管前端

## 📞 技术支持

遇到问题？
1. 检查环境要求
2. 查看日志输出
3. 参考常见问题
4. 联系开发团队

---

**祝学习愉快！** 🎉