# Production Deployment Guide

This guide provides step-by-step instructions for deploying the English Learning application to production.

## Prerequisites

- Docker and Docker Compose installed
- Domain name configured (e.g., api.englishspeakingtrainer.com)
- SSL certificates (Let's Encrypt or commercial)
- Server with minimum specifications:
  - 2 CPU cores
  - 4GB RAM
  - 50GB storage

## 1. SSL Certificate Setup

### Option A: Let's Encrypt (Free)

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d api.englishspeakingtrainer.com

# Copy certificates to nginx directory
sudo cp /etc/letsencrypt/live/api.englishspeakingtrainer.com/fullchain.pem ./nginx/ssl/
sudo cp /etc/letsencrypt/live/api.englishspeakingtrainer.com/privkey.pem ./nginx/ssl/

# Set permissions
sudo chmod 644 ./nginx/ssl/*.pem
```

### Option B: Commercial Certificates

```bash
# Place your certificates in nginx/ssl directory
cp your-fullchain.pem ./nginx/ssl/fullchain.pem
cp your-privkey.pem ./nginx/ssl/privkey.pem

# Set permissions
chmod 644 ./nginx/ssl/*.pem
```

## 2. Environment Configuration

### 2.1 Create Production Environment File

```bash
# Copy example environment file
cp .env.production .env

# Edit with production values
nano .env
```

### 2.2 Required Environment Variables

```bash
# Database
POSTGRES_USER=english_trainer
POSTGRES_PASSWORD=<strong_password>
POSTGRES_DB=english_trainer_prod

# JWT
JWT_SECRET_KEY=<very_long_random_string>

# AI Services
OPENAI_API_KEY=<your_openai_key>
AZURE_SPEECH_KEY=<your_azure_key>

# Payment
STRIPE_SECRET_KEY=<your_stripe_key>
APPLE_SHARED_SECRET=<your_apple_secret>
GOOGLE_SERVICE_ACCOUNT_JSON=<json_string>

# CORS
CORS_ORIGINS=["https://englishspeakingtrainer.com"]
```

### 2.3 Generate Secure Secrets

```bash
# Generate JWT secret
openssl rand -hex 32

# Generate database password
openssl rand -base64 32
```

## 3. Deployment Steps

### 3.1 Clone Repository

```bash
git clone <your-repo-url>
cd EnglishLearn
```

### 3.2 Configure Environment

```bash
# Create environment file
cp .env.production .env

# Edit with your values
nano .env
```

### 3.3 Set Up SSL Certificates

```bash
# Create SSL directory
mkdir -p nginx/ssl

# Copy your SSL certificates
cp /path/to/fullchain.pem nginx/ssl/
cp /path/to/privkey.pem nginx/ssl/
```

### 3.4 Build and Start Services

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps
```

### 3.5 Run Database Migrations

```bash
# Enter backend container
docker-compose -f docker-compose.prod.yml exec backend bash

# Run migrations
alembic upgrade head

# Exit container
exit
```

### 3.6 Verify Deployment

```bash
# Check health endpoint
curl https://api.englishspeakingtrainer.com/health

# Check API documentation
curl https://api.englishspeakingtrainer.com/docs

# View logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

## 4. Database Backup Strategy

### 4.1 Automatic Backups

The system includes automatic daily backups configured in docker-compose.prod.yml:

- Daily backups at midnight
- Keep backups for 7 days
- Keep weekly backups for 4 weeks
- Keep monthly backups for 6 months

### 4.2 Manual Backup

```bash
# Run backup script
docker-compose -f docker-compose.prod.yml exec backup backup.sh

# Or use the backup script directly
./scripts/backup-db.sh
```

### 4.3 Restore from Backup

```bash
# List available backups
ls -lh ./backups/

# Restore from specific backup
docker-compose -f docker-compose.prod.yml exec backup restore.sh /backups/backup_20240101_000000.sql.gz

# Or use the restore script directly
./scripts/restore-db.sh ./backups/backup_20240101_000000.sql.gz
```

## 5. Monitoring and Maintenance

### 5.1 View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f nginx
docker-compose -f docker-compose.prod.yml logs -f postgres

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 backend
```

### 5.2 Check Service Health

```bash
# Check all services
docker-compose -f docker-compose.prod.yml ps

# Check specific service health
curl https://api.englishspeakingtrainer.com/health
```

### 5.3 Restart Services

```bash
# Restart all services
docker-compose -f docker-compose.prod.yml restart

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend
docker-compose -f docker-compose.prod.yml restart nginx
```

### 5.4 Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

## 6. Security Best Practices

### 6.1 Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 6.2 Regular Updates

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Update Docker
sudo apt-get install docker-ce docker-ce-cli containerd.io

# Update Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 6.3 SSL Certificate Renewal

```bash
# For Let's Encrypt certificates
sudo certbot renew --quiet

# Reload nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

## 7. Troubleshooting

### 7.1 Service Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Check resource usage
docker stats

# Check disk space
df -h
```

### 7.2 Database Connection Issues

```bash
# Check postgres logs
docker-compose -f docker-compose.prod.yml logs postgres

# Test database connection
docker-compose -f docker-compose.prod.yml exec postgres psql -U english_trainer -d english_trainer_prod -c "SELECT 1;"
```

### 7.3 SSL Certificate Issues

```bash
# Check certificate validity
openssl x509 -in nginx/ssl/fullchain.pem -text -noout

# Test SSL configuration
openssl s_client -connect api.englishspeakingtrainer.com:443
```

### 7.4 Nginx Configuration Errors

```bash
# Test nginx configuration
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Check nginx logs
docker-compose -f docker-compose.prod.yml logs nginx
```

## 8. Performance Optimization

### 8.1 Database Optimization

```bash
# Connect to database
docker-compose -f docker-compose.prod.yml exec postgres psql -U english_trainer -d english_trainer_prod

# Run vacuum and analyze
VACUUM ANALYZE;

# Check database size
SELECT pg_size_pretty(pg_database_size('english_trainer_prod'));
```

### 8.2 Redis Optimization

```bash
# Check Redis memory usage
docker-compose -f docker-compose.prod.yml exec redis redis-cli INFO memory

# Clear cache if needed
docker-compose -f docker-compose.prod.yml exec redis redis-cli FLUSHALL
```

### 8.3 Application Scaling

```bash
# Scale backend service
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# Update docker-compose.prod.yml to set default replicas
# Add: deploy: replicas: 3 to backend service
```

## 9. Disaster Recovery

### 9.1 Full System Backup

```bash
# Backup all volumes
docker run --rm -v english_trainer_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
docker run --rm -v english_trainer_redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis_backup.tar.gz /data
```

### 9.2 Full System Restore

```bash
# Restore volumes
docker run --rm -v english_trainer_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /
docker run --rm -v english_trainer_redis_data:/data -v $(pwd):/backup alpine tar xzf /backup/redis_backup.tar.gz -C /

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

## 10. Support and Monitoring

### 10.1 Health Checks

```bash
# API health
curl https://api.englishspeakingtrainer.com/health

# Database health
docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U english_trainer

# Redis health
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
```

### 10.2 Resource Monitoring

```bash
# Docker stats
docker stats --no-stream

# System resources
htop
df -h
free -h
```

### 10.3 Log Monitoring

```bash
# Follow all logs
docker-compose -f docker-compose.prod.yml logs -f

# Export logs
docker-compose -f docker-compose.prod.yml logs > app.log
```

## Quick Reference

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Stop all services
docker-compose -f docker-compose.prod.yml down

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart service
docker-compose -f docker-compose.prod.yml restart backend

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Backup database
./scripts/backup-db.sh

# Restore database
./scripts/restore-db.sh <backup_file>
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
