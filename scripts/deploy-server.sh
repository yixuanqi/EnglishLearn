#!/bin/bash

set -e

echo "============================================"
echo "English Trainer - Server Deployment Script"
echo "============================================"
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root or with sudo"
    exit 1
fi

# Variables
APP_DIR="/app/englishlearn"
DOMAIN="${DOMAIN:-englishspeakingtrainer.com}"
EMAIL="${EMAIL:-admin@${DOMAIN}}"

echo "Configuration:"
echo "  App Directory: $APP_DIR"
echo "  Domain: $DOMAIN"
echo "  Email: $EMAIL"
echo ""

# Update system
echo "[1/10] Updating system packages..."
apt update && apt upgrade -y

# Install dependencies
echo "[2/10] Installing dependencies..."
apt install -y \
    curl \
    wget \
    git \
    nginx \
    certbot \
    python3-certbot-nginx \
    docker.io \
    docker-compose \
    postgresql \
    postgresql-contrib \
    redis-server

# Start services
echo "[3/10] Starting services..."
systemctl start docker
systemctl enable docker
systemctl start postgresql
systemctl enable postgresql
systemctl start redis-server
systemctl enable redis-server

# Create app directory
echo "[4/10] Creating application directory..."
mkdir -p $APP_DIR
cd $APP_DIR

# Clone repository (if not already present)
if [ ! -d ".git" ]; then
    echo "Please clone your repository to $APP_DIR first:"
    echo "  git clone <your-repo-url> $APP_DIR"
    exit 1
fi

# Create .env file
echo "[5/10] Setting up environment..."
if [ ! -f ".env" ]; then
    if [ -f ".env.production" ]; then
        cp .env.production .env
        echo "Created .env from .env.production"
        echo "Please edit .env and add your API keys"
    else
        cat > .env << 'EOF'
APP_NAME=English Trainer API
APP_VERSION=1.0.0
DEBUG=false

DATABASE_URL=postgresql+asyncpg://english_trainer:password@localhost:5432/english_trainer_prod
REDIS_URL=redis://localhost:6379/0

JWT_SECRET_KEY=CHANGE_THIS_TO_A_SECURE_SECRET
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

OPENAI_API_KEY=your_openai_key
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=eastus

CORS_ORIGINS=["https://yourdomain.com"]
LOG_LEVEL=INFO
ENVIRONMENT=production
EOF
        echo "Created .env file - please edit with your actual values"
    fi
fi

# Setup PostgreSQL
echo "[6/10] Setting up PostgreSQL..."
sudo -u postgres psql << 'EOF'
CREATE DATABASE english_trainer_prod;
CREATE USER english_trainer WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE english_trainer_prod TO english_trainer;
EOF

# Build and start containers
echo "[7/10] Building and starting containers..."
docker-compose -f docker-compose.prod.yml down || true
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Wait for backend to be ready
echo "[8/10] Waiting for backend to start..."
sleep 10

# Run migrations
echo "[9/10] Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head || true

# Configure Nginx
echo "[10/10] Configuring Nginx..."
cat > /etc/nginx/sites-available/english-trainer << 'EOF'
server {
    listen 80;
    server_name DOMAIN_PLACEHOLDER;

    client_max_body_size 100M;

    location / {
        root /app/englishlearn/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /docs {
        proxy_pass http://localhost:8000;
    }

    location /health {
        proxy_pass http://localhost:8000;
    }
}
EOF

sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" /etc/nginx/sites-available/english-trainer
ln -sf /etc/nginx/sites-available/english-trainer /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-default/default

nginx -t && systemctl reload nginx

echo ""
echo "============================================"
echo "Deployment completed!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your actual API keys"
echo "2. Run: docker-compose -f docker-compose.prod.yml restart backend"
echo "3. Setup SSL: sudo certbot --nginx -d $DOMAIN"
echo "4. Check status: docker-compose -f docker-compose.prod.yml ps"
echo ""
echo "Useful commands:"
echo "  View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  Restart:   docker-compose -f docker-compose.prod.yml restart"
echo "  Stop:     docker-compose -f docker-compose.prod.yml down"
echo ""
