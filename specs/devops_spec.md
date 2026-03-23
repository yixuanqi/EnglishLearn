# DevOps Specification

## 1. Overview

### 1.1 Infrastructure Strategy

- **Container-First**: All services run in Docker containers
- **Infrastructure as Code**: All infrastructure defined in code
- **GitOps**: Git as single source of truth
- **Automated Deployments**: Zero-touch deployments
- **Observability**: Comprehensive monitoring and logging

### 1.2 Environment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENVIRONMENT ARCHITECTURE                    │
└─────────────────────────────────────────────────────────────────┘

Development Environment
├── Local development (Docker Compose)
├── Feature branches (Preview deployments)
└── Shared dev environment

Staging Environment
├── Pre-production testing
├── Performance testing
├── Integration testing
└── UAT (User Acceptance Testing)

Production Environment
├── High availability setup
├── Auto-scaling
├── Multi-region deployment
└── Blue-green deployments
```

---

## 2. Docker Configuration

### 2.1 Backend Dockerfile

```dockerfile
# backend/Dockerfile

FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/production.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY alembic.ini ./
COPY pyproject.toml ./

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app ./app/
COPY --from=builder /app/alembic.ini ./
COPY --from=builder /app/pyproject.toml ./

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2.2 Mobile App Dockerfile (for CI/CD)

```dockerfile
# mobile/Dockerfile

FROM cirrusci/flutter:stable as build

WORKDIR /app

# Copy pubspec files
COPY pubspec.* ./

# Get dependencies
RUN flutter pub get

# Copy source code
COPY . .

# Build APK
RUN flutter build apk --release

# Production stage
FROM alpine:latest

WORKDIR /app

# Copy build artifacts
COPY --from=build /app/build/app/outputs/flutter-apk/app-release.apk ./app.apk

# Verify build
RUN ls -lh ./app.apk
```

### 2.3 Docker Compose (Development)

```yaml
# docker-compose.yml

version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: english_trainer_db
    environment:
      POSTGRES_USER: english_trainer
      POSTGRES_PASSWORD: english_trainer_password
      POSTGRES_DB: english_trainer_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U english_trainer"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: english_trainer_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: english_trainer_backend
    environment:
      DATABASE_URL: postgresql+asyncpg://english_trainer:english_trainer_password@postgres:5432/english_trainer_dev
      REDIS_URL: redis://redis:6379/0
      JWT_SECRET_KEY: dev_secret_key_change_in_production
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      AZURE_SPEECH_KEY: ${AZURE_SPEECH_KEY}
      AZURE_SPEECH_REGION: eastus
      STRIPE_SECRET_KEY: ${STRIPE_SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - audio_files:/app/audio
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  nginx:
    image: nginx:alpine
    container_name: english_trainer_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
  audio_files:
```

---

## 3. Kubernetes Configuration

### 3.1 Namespace Configuration

```yaml
# k8s/namespace.yaml

apiVersion: v1
kind: Namespace
metadata:
  name: english-trainer
  labels:
    name: english-trainer
    environment: production
```

### 3.2 Deployment Configuration

```yaml
# k8s/backend-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: english-trainer
  labels:
    app: backend
    version: v1
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
        version: v1
    spec:
      containers:
      - name: backend
        image: englishtrainer/backend:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: backend-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: backend-secrets
              key: redis-url
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: backend-secrets
              key: jwt-secret
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: backend-secrets
              key: openai-api-key
        - name: AZURE_SPEECH_KEY
          valueFrom:
            secretKeyRef:
              name: backend-secrets
              key: azure-speech-key
        - name: AZURE_SPEECH_REGION
          valueFrom:
            configMapKeyRef:
              name: backend-config
              key: azure-speech-region
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 1
```

### 3.3 Service Configuration

```yaml
# k8s/backend-service.yaml

apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: english-trainer
  labels:
    app: backend
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: backend
```

### 3.4 Ingress Configuration

```yaml
# k8s/ingress.yaml

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: english-trainer-ingress
  namespace: english-trainer
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.englishspeakingtrainer.com
    secretName: english-trainer-tls
  rules:
  - host: api.englishspeakingtrainer.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 80
```

### 3.5 Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: english-trainer
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
```

---

## 4. CI/CD Pipeline

### 4.1 GitHub Actions Workflow

```yaml
# .github/workflows/ci-cd.yml

name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: englishtrainer/backend

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements/development.txt
      
      - name: Run linter
        run: |
          black --check app/
          isort --check-only app/
          flake8 app/
      
      - name: Run type checker
        run: |
          mypy app/
      
      - name: Run tests
        run: |
          pytest --cov=app --cov-report=xml --cov-report=term
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
      image-digest: ${{ steps.build.outputs.digest }}
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix={{branch}}-
      
      - name: Build and push Docker image
        id: build
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Scan image for vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ steps.meta.outputs.tags }}
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload Trivy results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBE_CONFIG_STAGING }}
      
      - name: Update deployment
        run: |
          kubectl set image deployment/backend \
            backend=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ needs.build.outputs.image-tag }} \
            -n english-trainer
      
      - name: Wait for rollout
        run: |
          kubectl rollout status deployment/backend -n english-trainer --timeout=5m

  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBE_CONFIG_PRODUCTION }}
      
      - name: Update deployment
        run: |
          kubectl set image deployment/backend \
            backend=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ needs.build.outputs.image-tag }} \
            -n english-trainer
      
      - name: Wait for rollout
        run: |
          kubectl rollout status deployment/backend -n english-trainer --timeout=5m
      
      - name: Run database migrations
        run: |
          kubectl exec -n english-trainer deployment/backend -- \
            alembic upgrade head
      
      - name: Verify deployment
        run: |
          kubectl get pods -n english-trainer
          kubectl get services -n english-trainer
```

### 4.2 Mobile App CI/CD

```yaml
# .github/workflows/mobile-ci.yml

name: Mobile CI/CD

on:
  push:
    branches: [main, develop]
    paths:
      - 'mobile/**'

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.16.0'
          channel: 'stable'
          cache: true
      
      - name: Get dependencies
        run: flutter pub get
      
      - name: Analyze code
        run: flutter analyze
      
      - name: Run tests
        run: flutter test --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info

  build-android:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.16.0'
          channel: 'stable'
          cache: true
      
      - name: Get dependencies
        run: flutter pub get
      
      - name: Build APK
        run: |
          flutter build apk \
            --release \
            --build-number=${{ github.run_number }} \
            --build-name=english-trainer-${{ github.run_number }}
      
      - name: Sign APK
        run: |
          jarsigner -keystore ${{ secrets.KEYSTORE_PATH }} \
            -storepass ${{ secrets.KEYSTORE_PASSWORD }} \
            -keypass ${{ secrets.KEY_PASSWORD }} \
            build/app/outputs/flutter-apk/app-release.apk \
            ${{ secrets.KEY_ALIAS }}
      
      - name: Upload APK
        uses: actions/upload-artifact@v3
        with:
          name: android-apk
          path: build/app/outputs/flutter-apk/app-release.apk

  build-ios:
    needs: test
    runs-on: macos-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.16.0'
          channel: 'stable'
          cache: true
      
      - name: Get dependencies
        run: flutter pub get
      
      - name: Build iOS
        run: |
          flutter build ios \
            --release \
            --build-number=${{ github.run_number }} \
            --build-name=english-trainer-${{ github.run_number }}
      
      - name: Archive build
        run: |
          cd build/ios/Release-iphoneos
          zip -r ../../english-trainer-ios.zip *
      
      - name: Upload iOS build
        uses: actions/upload-artifact@v3
        with:
          name: ios-build
          path: english-trainer-ios.zip
```

---

## 5. Monitoring & Observability

### 5.1 Prometheus Configuration

```yaml
# k8s/prometheus-config.yaml

apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: english-trainer
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    
    scrape_configs:
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_label_app]
            target_label: app
          - source_labels: [__meta_kubernetes_namespace]
            target_label: namespace
          - source_labels: [__address__]
            target_label: __param_target
```

### 5.2 Grafana Dashboards

```json
{
  "dashboard": {
    "title": "English Trainer Backend",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[1m])",
            "legendFormat": "{{method}} {{status}}"
          }
        ]
      },
      {
        "title": "Response Time (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "{{endpoint}}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[1m])",
            "legendFormat": "{{status}}"
          }
        ]
      },
      {
        "title": "Database Connections",
        "targets": [
          {
            "expr": "pg_stat_database_numbackends",
            "legendFormat": "{{datname}}"
          }
        ]
      },
      {
        "title": "Redis Memory Usage",
        "targets": [
          {
            "expr": "redis_memory_used_bytes / 1024 / 1024",
            "legendFormat": "MB"
          }
        ]
      }
    ]
  }
}
```

### 5.3 Alerting Rules

```yaml
# k8s/alerting-rules.yaml

groups:
  - name: backend_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/sec"
      
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "p95 response time is {{ $value }} seconds"
      
      - alert: HighMemoryUsage
        expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is {{ $value | humanizePercentage }}"
      
      - alert: PodCrashLooping
        expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Pod is crash looping"
          description: "Pod {{ $labels.pod }} is restarting frequently"
```

---

## 6. Logging

### 6.1 Structured Logging

```python
# app/utils/logger.py

import structlog
from pythonjsonlogger import jsonlogger

def configure_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

logger = structlog.get_logger()
```

### 6.2 Log Aggregation

```yaml
# k8s/fluentd-config.yaml

apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
  namespace: english-trainer
data:
  fluent.conf: |
    <source>
      @type tail
      @id in_tail_container_logs
      path /var/log/containers/*.log
      pos_file /var/log/fluentd-containers.log.pos
      tag kubernetes.*
      read_from_head true
      <parse>
        @type json
        time_format %iso8601
      </parse>
    </source>

    <filter kubernetes.**>
      @type kubernetes_metadata
    </filter>

    <match kubernetes.**>
      @type elasticsearch
      host elasticsearch
      port 9200
      logstash_format true
      logstash_prefix fluentd
      <buffer>
        @type file
        path /var/log/fluentd-buffers/kubernetes.system.buffer
        flush_mode interval
        flush_interval 5s
      </buffer>
    </match>
```

---

## 7. Backup & Disaster Recovery

### 7.1 Database Backup Strategy

```yaml
# k8s/backup-cronjob.yaml

apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: english-trainer
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM UTC
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: prodrigestivill/postgres-backup-local
            env:
            - name: POSTGRES_HOST
              value: postgres
            - name: POSTGRES_DB
              value: english_trainer
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: postgres-secrets
                  key: username
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secrets
                  key: password
            - name: S3_BUCKET
              value: english-trainer-backups
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: aws-secrets
                  key: access-key-id
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: aws-secrets
                  key: secret-access-key
            volumeMounts:
            - name: backup-storage
              mountPath: /backups
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

### 7.2 Disaster Recovery Plan

| Scenario | Recovery Time | Recovery Point | Strategy |
|----------|----------------|-----------------|----------|
| Pod Failure | < 5 min | Minimal | Kubernetes auto-restart |
| Node Failure | < 10 min | Minimal | Pod rescheduling |
| Zone Failure | < 30 min | < 5 min | Multi-zone deployment |
| Database Failure | < 1 hour | < 15 min | Read replicas + failover |
| Complete Outage | < 4 hours | < 1 hour | DR site activation |

---

## 8. Environment Configuration

### 8.1 Environment Variables

```bash
# .env.example

# Application
APP_NAME=English Speaking Trainer
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/english_trainer
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Services
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
AZURE_SPEECH_KEY=your-azure-speech-key
AZURE_SPEECH_REGION=eastus

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Storage
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET=english-trainer-audio
S3_CDN_URL=https://cdn.englishspeakingtrainer.com

# Monitoring
SENTRY_DSN=https://...
PROMETHEUS_RETENTION=15d
```

### 8.2 Configuration Management

```python
# app/core/config.py

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Environment
    APP_ENV: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str
    REDIS_MAX_CONNECTIONS: int = 50
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # AI Services
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    AZURE_SPEECH_KEY: Optional[str] = None
    AZURE_SPEECH_REGION: str = "eastus"
    
    # Stripe
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    
    # Storage
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str
    S3_CDN_URL: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_RETENTION: str = "15d"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

---

## 9. Performance Optimization

### 9.1 Resource Limits

| Component | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|-------------|------------|----------------|--------------|
| Backend API | 250m | 500m | 256Mi | 512Mi |
| PostgreSQL | 500m | 1000m | 512Mi | 2Gi |
| Redis | 100m | 200m | 128Mi | 256Mi |
| Nginx | 100m | 200m | 64Mi | 128Mi |

### 9.2 Auto-scaling Policies

```yaml
# k8s/vpa.yaml

apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: backend-vpa
  namespace: english-trainer
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: backend
      maxAllowed:
        cpu: "2"
        memory: "2Gi"
      minAllowed:
        cpu: "100m"
        memory: "128Mi"
      controlledResources: ["cpu", "memory"]
```

---

## 10. Security in DevOps

### 10.1 Secrets Management

```bash
# Create Kubernetes secret
kubectl create secret generic backend-secrets \
  --from-literal=database-url="postgresql+asyncpg://..." \
  --from-literal=jwt-secret="..." \
  --from-literal=openai-api-key="sk-..." \
  --namespace=english-trainer

# Seal secret for Git storage
kubeseal -f backend-secrets.yaml \
  -w sealed-backend-secrets.yaml \
  --scope namespace-wide
```

### 10.2 Image Security

```yaml
# .github/workflows/security-scan.yml

name: Security Scan

on:
  push:
    branches: [main, develop]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

---

## 11. Maintenance & Operations

### 11.1 Routine Tasks

| Task | Frequency | Owner | Tool |
|------|------------|--------|-------|
| Database backups | Daily | Automated | CronJob |
| Log rotation | Weekly | Automated | Logrotate |
| Security patches | Weekly | DevOps | Kubernetes |
| Performance review | Monthly | DevOps | Grafana |
| Capacity planning | Quarterly | DevOps | Prometheus |
| Disaster recovery drill | Semi-annually | All | Manual |

### 11.2 On-Call Rotation

| Week | Primary | Secondary |
|------|----------|-----------|
| Week 1 | DevOps Lead | DevOps Engineer 1 |
| Week 2 | DevOps Engineer 1 | DevOps Engineer 2 |
| Week 3 | DevOps Engineer 2 | DevOps Lead |
| Week 4 | DevOps Lead | DevOps Engineer 1 |

### 11.3 Incident Response

1. **Detection**: Automated alerts from Prometheus
2. **Triage**: On-call engineer assesses severity
3. **Response**: Execute runbook procedures
4. **Communication**: Update status page
5. **Resolution**: Fix and verify
6. **Post-mortem**: Document and improve
