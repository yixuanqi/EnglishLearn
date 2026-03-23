# 云服务器部署指南

## 推荐云服务器提供商

| 提供商 | 推荐配置 | 月费用 | 特点 |
|--------|----------|--------|------|
| **阿里云 ECS** | 2核4G/50GB SSD | ¥100-200 | 国内速度快 |
| **腾讯云 CVM** | 2核4G/50GB SSD | ¥100-200 | 国内速度快 |
| **Vultr** | 2核4G/55GB SSD | $20/月 | 全球节点 |
| **DigitalOcean** | 2核4G/80GB SSD | $20/月 | 简单易用 |
| **AWS EC2** | t3.medium | $30/月 | 功能强大 |

## 部署方式选择

### 方式一：Docker 部署（推荐）

适用于所有云服务器，需要服务器已安装 Docker

```bash
# 1. 安装 Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu

# 2. 克隆项目
git clone <your-repo-url>
cd EnglishLearn

# 3. 配置环境变量
cp .env.production .env
nano .env  # 编辑配置

# 4. 启动服务
docker-compose -f docker-compose.prod.yml up -d
```

### 方式二：手动部署

适用于没有 Docker 的服务器

```bash
# 1. 安装 Python 3.11
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# 2. 安装 PostgreSQL
sudo apt install postgresql postgresql-contrib

# 3. 安装 Redis
sudo apt install redis-server

# 4. 配置数据库
sudo -u postgres psql
CREATE DATABASE english_trainer_prod;
CREATE USER english_trainer WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE english_trainer_prod TO english_trainer;
```

## 阿里云 ECS 部署详细步骤

### 1. 创建 ECS 实例

1. 登录阿里云控制台 https://ecs.console.aliyun.com
2. 点击 "创建实例"
3. 选择配置：
   - 地域：华北2（北京）或华东1（杭州）
   - 实例规格：ecs.t5-lc2m1.large (2核2G) 或更高
   - 镜像：Ubuntu 22.04 LTS
   - 存储：40GB SSD
4. 设置安全组规则：
   - 端口 22 (SSH)
   - 端口 80 (HTTP)
   - 端口 443 (HTTPS)
   - 端口 8000 (后端API)
5. 创建并保存密钥对

### 2. 连接服务器

```bash
ssh -i your-key.pem ubuntu@your-server-ip
```

### 3. 安装 Docker

```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu
```

### 4. 部署应用

```bash
# 克隆代码
git clone https://github.com/yourusername/EnglishLearn.git
cd EnglishLearn

# 配置环境变量
cp .env.production .env
nano .env  # 填入真实的 API Keys

# 启动服务
docker-compose -f docker-compose.prod.yml up -d --build
```

### 5. 配置 SSL 证书

使用 Let's Encrypt 免费证书：

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书（需要域名已解析到服务器）
sudo certbot --nginx -d your-domain.com
```

## 域名和 DNS 配置

1. 购买域名（阿里云/腾讯云）
2. 添加 DNS 记录：
   - A记录：`@` -> 服务器IP
   - A记录：`www` -> 服务器IP
   - A记录：`api` -> 服务器IP

## Nginx 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /app/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /docs {
        proxy_pass http://localhost:8000;
    }
}
```

## 防火墙配置

```bash
# Ubuntu ufw
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# 阿里云安全组（在控制台配置）
# 入方向规则：
# - 22 (SSH)
# - 80 (HTTP)
# - 443 (HTTPS)
# - 8000 (API)
```

## 监控和日志

```bash
# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看资源使用
docker stats
```

## 自动化部署（CI/CD）

使用我们创建的 GitHub Actions：

1. 在 GitHub 仓库设置中添加 secrets：
   - `PRODUCTION_HOST`: 服务器IP
   - `PRODUCTION_USER`: ubuntu
   - `PRODUCTION_SSH_KEY`: SSH私钥
   - `SLACK_WEBHOOK_URL`: (可选) Slack通知

2. 推送代码到 main 分支自动部署

## 快速部署脚本

对于新服务器，运行以下脚本一键部署：

```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/EnglishLearn/main/scripts/deploy-server.sh | bash
```
