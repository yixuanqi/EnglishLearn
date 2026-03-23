# 阿里云部署指南

## 推荐配置

| 配置项 | 推荐选择 | 费用估算 |
|--------|----------|----------|
| **地域** | 华东1（杭州）或华南1（广州） | - |
| **实例规格** | 2核2G / 2核4G | ¥60-150/月 |
| **系统盘** | 40GB SSD | ¥10-20/月 |
| **带宽** | 3-5Mbps | ¥30-50/月 |
| **操作系统** | Ubuntu 22.04 LTS | 免费 |

## 部署方式

### 方式一：Docker 部署（推荐）

#### 1. 安装 Docker
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu
```

#### 2. 安装 Docker Compose
```bash
sudo apt update
sudo apt install docker-compose -y
```

#### 3. 上传项目文件
```bash
# 在本地项目目录执行
scp -r EnglishLearn ubuntu@your-server-ip:/home/ubuntu/
```

#### 4. 配置环境变量
```bash
cd /home/ubuntu/EnglishLearn
cp .env.example .env
nano .env  # 编辑配置
```

#### 5. 启动服务
```bash
docker-compose up -d
docker-compose ps  # 查看状态
```

### 方式二：手动部署

#### 1. 安装 Python 3.11+
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip -y
```

#### 2. 安装 Redis
```bash
sudo apt install redis-server -y
sudo systemctl start redis
```

#### 3. 安装 PostgreSQL（可选，生产环境推荐）
```bash
sudo apt install postgresql postgresql-contrib -y
sudo systemctl start postgresql
```

#### 4. 配置 Python 虚拟环境
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements/production.txt
```

#### 5. 启动后端服务
```bash
gunicorn app.main:app --bind 0.0.0.0:8000 --workers 4
```

---

## Nginx 反向代理配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## SSL 证书配置

使用 Let's Encrypt 免费证书：
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## 快速部署脚本

对于新的阿里云服务器，运行以下命令一键部署：

```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/EnglishLearn/main/scripts/deploy-aliyun.sh | bash
```

---

## 验证部署

```bash
# 检查容器状态
docker-compose ps

# 查看日志
docker-compose logs -f backend

# 测试API
curl http://localhost:8000/health
```

---

## 防火墙配置

在阿里云控制台开放以下端口：

| 端口 | 用途 |
|------|------|
| 22 | SSH |
| 80 | HTTP |
| 443 | HTTPS |
| 8000 | 后端API（如不使用nginx） |

---

## 备份策略

数据库备份脚本：
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
docker-compose exec -T db pg_dump -U postgres > backup_$DATE.sql
```

---

## 监控

推荐使用阿里云监控服务或开源方案：
- [阿里云监控](https://cloudmonitor.console.aliyun.com/)
- [Prometheus + Grafana](https://prometheus.io/)
