# English Trainer - Backend Setup Guide

## 🚀 快速启动后端

由于Python环境配置问题，请按照以下步骤手动启动后端：

### 方法1：手动安装Python（推荐）

#### 步骤1：安装Python
1. 访问 https://www.python.org/downloads/
2. 下载 Python 3.12.x Windows installer
3. 运行安装程序，**务必勾选 "Add Python to PATH"**
4. 完成安装后重启命令行

#### 步骤2：验证安装
```bash
python --version
```

#### 步骤3：启动后端
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements/development.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 方法2：使用现有Python路径

如果你的Python已安装但不在PATH中，找到Python.exe的完整路径：

常见安装位置：
- `C:\Python312\python.exe`
- `C:\Program Files\Python312\python.exe`
- `C:\Users\你的用户名\AppData\Local\Programs\Python\Python312\python.exe`

然后运行：
```bash
cd backend
C:\Python312\python.exe -m venv venv
venv\Scripts\activate
pip install -r requirements/development.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🔧 配置说明

我已经为你做了以下配置优化：

### 1. 数据库配置
已将数据库从PostgreSQL改为SQLite，无需安装数据库：
- 配置文件：`backend/app/core/config.py`
- 数据库文件：`backend/english_trainer.db`（自动创建）

### 2. 依赖更新
已更新依赖文件，使用aiosqlite替代asyncpg：
- 文件：`backend/requirements/base.txt`

### 3. 防火墙配置
已配置防火墙规则允许访问：
- 端口8000（后端API）
- 端口3000（前端）

## 📱 访问地址

后端启动成功后，可以通过以下地址访问：

- **本地访问**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **手机访问**: http://10.6.6.102:8000
- **健康检查**: http://localhost:8000/health

## 🎯 启动成功标志

当看到以下输出时，表示后端启动成功：

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## 🐛 常见问题

### 问题1：找不到Python
**解决方案**：
1. 确保Python已正确安装
2. 检查是否勾选了"Add Python to PATH"
3. 重启命令行或重启电脑

### 问题2：虚拟环境创建失败
**解决方案**：
```bash
# 使用完整路径
C:\Python312\python.exe -m venv backend\venv
```

### 问题3：依赖安装失败
**解决方案**：
```bash
# 升级pip
python -m pip install --upgrade pip

# 重新安装依赖
pip install -r requirements/development.txt --force-reinstall
```

### 问题4：端口被占用
**解决方案**：
```bash
# 使用其他端口
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## 📝 启动脚本说明

我为你创建了以下启动脚本：

1. **start-backend.bat** - 后端启动脚本（需要Python在PATH中）
2. **install-python.bat** - Python安装脚本
3. **setup-backend.bat** - 后端设置脚本

## 🎉 启动后端后

后端启动成功后，你可以：

1. **访问API文档**: http://localhost:8000/docs
2. **测试API端点**: 使用Swagger UI进行测试
3. **连接前端**: 前端会自动连接到后端
4. **手机访问**: 在手机浏览器访问 http://10.6.6.102:8000

---

**现在请按照上面的步骤手动安装Python并启动后端！** 🚀