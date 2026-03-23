# English Trainer - 完整操作流程指南

## 🎯 当前状态

✅ **前端界面**：已打开在浏览器中
⚠️ **后端服务**：需要手动启动（Python环境配置问题）

## 🚀 完整启动步骤

### 步骤1：启动后端服务

由于Python环境配置问题，请手动启动后端：

#### 方法A：使用Python Launcher（推荐）

1. 打开新的命令行窗口
2. 进入后端目录：
```bash
cd C:\Users\0qyx\dev\0python\EnglishLearn\backend
```

3. 创建虚拟环境（首次运行）：
```bash
py -m venv venv
```

4. 激活虚拟环境：
```bash
venv\Scripts\activate
```

5. 安装依赖（首次运行）：
```bash
pip install -r requirements/development.txt
```

6. 启动后端服务：
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 方法B：使用完整Python路径

如果上面的方法不行，使用完整路径：

```bash
cd C:\Users\0qyx\dev\0python\EnglishLearn\backend
C:\Users\0qyx\AppData\Local\Programs\Python\Python312\python.exe -m venv venv
venv\Scripts\activate
pip install -r requirements/development.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 步骤2：验证后端运行

后端启动成功后，在浏览器中访问：

- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

### 步骤3：前端界面

前端界面已经在浏览器中打开，包含：
- 登录页面
- 仪表板
- 场景列表
- 练习界面

## 🔄 完整操作流程

### 1. 用户注册流程

1. **打开注册页面**
   - 在前端界面点击 "Create Account"
   - 或访问：http://localhost:3000/register

2. **填写注册信息**
   - Full Name: 测试用户
   - Email: test@example.com
   - Password: password123
   - Confirm Password: password123

3. **提交注册**
   - 点击 "Create Account" 按钮
   - 系统会创建用户并返回认证信息

4. **自动登录**
   - 注册成功后自动登录到系统
   - 跳转到仪表板页面

### 2. 用户登录流程

1. **打开登录页面**
   - 访问：http://localhost:3000/login

2. **输入登录信息**
   - Email: test@example.com
   - Password: password123

3. **提交登录**
   - 点击 "Sign In" 按钮
   - 系统验证凭据并返回访问令牌

4. **进入仪表板**
   - 登录成功后跳转到仪表板
   - 显示学习统计和进度

### 3. 浏览学习场景

1. **查看场景列表**
   - 点击导航栏的 "Scenarios"
   - 或访问：http://localhost:3000/scenarios

2. **筛选场景**
   - 使用搜索框搜索特定场景
   - 点击难度按钮筛选：All / Beginner / Intermediate / Advanced

3. **查看场景详情**
   - 每个场景卡片显示：
     - 场景标题和描述
     - 难度级别（颜色编码）
     - 预计时长
     - 分类标签
     - Premium标识（如适用）

### 4. 开始练习会话

1. **选择场景**
   - 点击任意场景卡片
   - 或点击 "Start Practice" 按钮

2. **启动练习**
   - 系统创建新的练习会话
   - 加载对话内容和AI角色

3. **练习界面功能**
   - **对话显示**：显示AI和用户的对话历史
   - **录音控制**：开始/停止录音按钮
   - **语音识别**：实时显示识别的文本
   - **提交答案**：将语音识别结果提交给后端

4. **接收反馈**
   - 系统分析发音、流利度、准确性
   - 提供改进建议和技巧
   - 显示综合评分

5. **继续练习**
   - 点击 "Next Turn" 继续下一轮对话
   - 完成所有轮次后显示最终成绩

### 5. 查看学习进度

1. **仪表板统计**
   - Total Sessions: 总练习次数
   - Practice Hours: 累计练习时长
   - Current Streak: 当前连续学习天数
   - Accuracy Rate: 平均准确率

2. **最近练习**
   - 显示最近完成的练习场景
   - 显示每个场景的完成进度
   - 提供快速重新练习的链接

3. **学习建议**
   - 显示个性化的学习建议
   - 提供提升技巧和方法

## 🎨 界面特点

### 奢华精致设计
- **深色主题**：专业的深色背景
- **金色点缀**：优雅的金色强调元素
- **流畅动画**：精致的过渡和微交互
- **响应式布局**：完美适配各种屏幕尺寸

### 用户体验优化
- **简单导航**：直观的菜单和页面切换
- **清晰反馈**：即时的操作反馈和状态提示
- **快速加载**：优化的性能和加载状态
- **错误处理**：友好的错误提示和恢复建议

## 🔧 故障排除

### 后端无法启动

**问题**：端口8000被占用
```bash
# 使用其他端口
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**问题**：依赖安装失败
```bash
# 升级pip
python -m pip install --upgrade pip

# 重新安装依赖
pip install -r requirements/development.txt --force-reinstall
```

### 前端无法连接后端

**问题**：CORS错误
- 确保后端CORS配置包含前端URL
- 检查 `backend/app/core/config.py` 中的 `cors_origins`

**问题**：API请求失败
- 打开浏览器开发者工具 (F12)
- 查看Console和Network标签
- 检查请求状态和错误信息

### 数据库连接问题

**问题**：PostgreSQL未运行
```bash
# 启动PostgreSQL服务
net start postgresql-x64-15

# 或使用Docker
docker-compose up -d postgres
```

**问题**：数据库不存在
```sql
-- 连接到PostgreSQL
psql -U postgres

-- 创建数据库
CREATE DATABASE english_trainer_dev;

-- 创建用户
CREATE USER english_trainer WITH PASSWORD 'english_trainer_password';

-- 授权
GRANT ALL PRIVILEGES ON DATABASE english_trainer_dev TO english_trainer;
```

## 📱 移动端体验

前端界面完全响应式，支持：
- 📱 手机竖屏
- 📱 手机横屏
- 💻 平板设备
- 🖥️ 桌面显示器

## 🎯 学习建议

1. **每日练习**：保持每天至少15分钟的练习
2. **多样化场景**：尝试不同类型的对话场景
3. **关注反馈**：仔细阅读AI提供的发音和流利度反馈
4. **重复练习**：对困难场景进行多次练习
5. **记录进度**：定期查看仪表板了解学习进展

## 📞 技术支持

遇到问题时：
1. 检查后端服务是否正常运行
2. 查看浏览器控制台的错误信息
3. 验证网络连接和端口访问
4. 参考本指南的故障排除部分

---

**开始你的英语学习之旅吧！** 🌟