# Django Finance App - Deployment Guide

This guide covers deploying the Django Finance App to production environments.

## 🌐 Production Deployment Options

### 1. Cloud Platforms (Recommended)

#### AWS Deployment
```bash
# Using AWS ECS with Docker
# 1. Push images to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# 2. Tag and push images
docker tag djangoproject_web:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/finance-app:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/finance-app:latest

# 3. Use provided ECS task definition
```

#### Google Cloud Run
```bash
# Build and deploy to Cloud Run
gcloud builds submit --tag gcr.io/PROJECT-ID/finance-app
gcloud run deploy --image gcr.io/PROJECT-ID/finance-app --platform managed --region us-central1
```

#### Heroku Deployment
```bash
# Install Heroku CLI and login
heroku login

# Create Heroku app
heroku create finance-app-prod

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Add Redis addon
heroku addons:create heroku-redis:hobby-dev

# Set environment variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-production-secret-key
heroku config:set STRIPE_SECRET_KEY=sk_live_your_live_key
heroku config:set STRIPE_PUBLIC_KEY=pk_live_your_live_key

# Deploy
git push heroku main
```

### 2. VPS/Server Deployment

#### Using Docker Compose (Production)

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  web:
    build: .
    command: gunicorn financeapp.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - db
      - redis
    environment:
      - DEBUG=False
      - DATABASE_URL=postgres://django:${DB_PASSWORD}@db:5432/financeapp
      - REDIS_URL=redis://redis:6379/1
      - SECRET_KEY=${SECRET_KEY}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - STRIPE_PUBLIC_KEY=${STRIPE_PUBLIC_KEY}
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=financeapp
      - POSTGRES_USER=django
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  celery:
    build: .
    command: celery -A financeapp worker --loglevel=info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgres://django:${DB_PASSWORD}@db:5432/financeapp
      - REDIS_URL=redis://redis:6379/1
    restart: unless-stopped

  celery-beat:
    build: .
    command: celery -A financeapp beat --loglevel=info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgres://django:${DB_PASSWORD}@db:5432/financeapp
      - REDIS_URL=redis://redis:6379/1
    restart: unless-stopped

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

#### Nginx Configuration

Create `nginx.conf`:
```nginx
upstream web {
    server web:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://web;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
    
    location /static/ {
        alias /app/staticfiles/;
    }
    
    location /media/ {
        alias /app/media/;
    }
}
```

## 🔐 Security Configuration

### 1. Environment Variables

Create `.env.prod`:
```env
DEBUG=False
SECRET_KEY=your-very-secure-secret-key-here
DATABASE_URL=postgres://django:secure_password@db:5432/financeapp
REDIS_URL=redis://redis:6379/1
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
STRIPE_SECRET_KEY=sk_live_your_live_secret_key
STRIPE_PUBLIC_KEY=pk_live_your_live_public_key
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 2. SSL Certificate Setup

Using Let's Encrypt:
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. Database Security

```sql
-- Create production database user
CREATE USER django_prod WITH PASSWORD 'very_secure_password';
CREATE DATABASE financeapp_prod;
GRANT ALL PRIVILEGES ON DATABASE financeapp_prod TO django_prod;

-- Restrict permissions
REVOKE ALL ON SCHEMA public FROM public;
GRANT USAGE ON SCHEMA public TO django_prod;
GRANT CREATE ON SCHEMA public TO django_prod;
```

## 📊 Monitoring and Logging

### 1. Application Monitoring

Add to `settings.py`:
```python
# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/error.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'transactions': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

### 2. Database Monitoring

```bash
# PostgreSQL monitoring script
#!/bin/bash
# monitor_db.sh

DB_NAME="financeapp_prod"
DB_USER="django_prod"

echo "=== Database Health Check ==="
echo "Active connections:"
psql -U $DB_USER -d $DB_NAME -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"

echo "Database size:"
psql -U $DB_USER -d $DB_NAME -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));"

echo "Slow queries:"
psql -U $DB_USER -d $DB_NAME -c "SELECT query, state, query_start FROM pg_stat_activity WHERE state != 'idle' AND query_start < now() - interval '5 minutes';"
```

### 3. Performance Monitoring

Create `monitoring/docker-compose.yml`:
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123

volumes:
  prometheus_data:
  grafana_data:
```

## 🚀 Deployment Steps

### 1. Server Preparation

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create app directory
sudo mkdir -p /opt/financeapp
sudo chown $USER:$USER /opt/financeapp
cd /opt/financeapp
```

### 2. Deploy Application

```bash
# Clone repository
git clone <your-repo-url> .

# Create production environment file
cp .env.example .env.prod
# Edit .env.prod with production values

# Build and start services
docker-compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### 3. Setup Monitoring

```bash
# Create monitoring directory
mkdir monitoring
cd monitoring

# Start monitoring services
docker-compose -f monitoring/docker-compose.yml up -d

# Access Grafana at http://your-server:3000
# Default login: admin/admin123
```

## 🔄 Backup and Recovery

### 1. Database Backup

```bash
#!/bin/bash
# backup_db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
DB_NAME="financeapp_prod"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create database backup
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U django $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/db_backup_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/db_backup_$DATE.sql.gz"
```

### 2. Media Files Backup

```bash
#!/bin/bash
# backup_media.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
MEDIA_DIR="/opt/financeapp/media"

# Create backup
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz -C $MEDIA_DIR .

# Keep only last 7 days
find $BACKUP_DIR -name "media_backup_*.tar.gz" -mtime +7 -delete

echo "Media backup completed: $BACKUP_DIR/media_backup_$DATE.tar.gz"
```

### 3. Automated Backups

```bash
# Add to crontab
crontab -e

# Add these lines:
0 2 * * * /opt/financeapp/backup_db.sh
0 3 * * * /opt/financeapp/backup_media.sh
```

## 🔍 Health Checks

### 1. Application Health Check

Create `health_check.py`:
```python
#!/usr/bin/env python
import requests
import sys
import os

def check_health():
    try:
        # Check web application
        response = requests.get('http://localhost:8000/admin/', timeout=10)
        if response.status_code != 200:
            print(f"Web app health check failed: {response.status_code}")
            return False
        
        # Check database
        response = requests.get('http://localhost:8000/api/accounts/', timeout=10)
        if response.status_code != 401:  # Should return 401 (unauthorized) if DB is working
            print(f"Database health check failed: {response.status_code}")
            return False
        
        print("Health check passed")
        return True
    
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

if __name__ == "__main__":
    if not check_health():
        sys.exit(1)
```

### 2. Monitoring Script

Create `monitor.sh`:
```bash
#!/bin/bash

# Check if all containers are running
echo "=== Container Status ==="
docker-compose -f docker-compose.prod.yml ps

# Check disk usage
echo "=== Disk Usage ==="
df -h

# Check memory usage
echo "=== Memory Usage ==="
free -h

# Check application health
echo "=== Application Health ==="
python3 health_check.py

# Check logs for errors
echo "=== Recent Errors ==="
docker-compose -f docker-compose.prod.yml logs --tail=50 web | grep -i error
```

## 🚨 Troubleshooting Production Issues

### Common Production Problems

1. **High Memory Usage**
   ```bash
   # Check memory usage
   docker stats
   
   # Increase memory limits in docker-compose.yml
   services:
     web:
       mem_limit: 1g
   ```

2. **Database Connection Issues**
   ```bash
   # Check database logs
   docker-compose -f docker-compose.prod.yml logs db
   
   # Check connection pool
   docker-compose -f docker-compose.prod.yml exec web python manage.py dbshell
   ```

3. **SSL Certificate Issues**
   ```bash
   # Check certificate expiry
   openssl x509 -in /etc/nginx/ssl/cert.pem -text -noout
   
   # Renew certificate
   sudo certbot renew
   ```

4. **Performance Issues**
   ```bash
   # Check slow queries
   docker-compose -f docker-compose.prod.yml exec db psql -U django -d financeapp -c "SELECT query, state, query_start FROM pg_stat_activity WHERE state != 'idle' AND query_start < now() - interval '5 minutes';"
   ```

### Emergency Recovery

```bash
# Stop all services
docker-compose -f docker-compose.prod.yml down

# Restore database from backup
docker-compose -f docker-compose.prod.yml up -d db
docker-compose -f docker-compose.prod.yml exec -T db psql -U django -d financeapp < /opt/backups/db_backup_YYYYMMDD_HHMMSS.sql

# Restore media files
tar -xzf /opt/backups/media_backup_YYYYMMDD_HHMMSS.tar.gz -C /opt/financeapp/media/

# Start all services
docker-compose -f docker-compose.prod.yml up -d
```

## 📈 Performance Optimization

### 1. Database Optimization

```sql
-- Add indexes for better performance
CREATE INDEX idx_transactions_date ON transactions_transaction(transaction_date);
CREATE INDEX idx_transactions_account_status ON transactions_transaction(account_id, status);
CREATE INDEX idx_transactions_type_date ON transactions_transaction(transaction_type, transaction_date);
```

### 2. Caching Configuration

Add to `settings.py`:
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache sessions in Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

### 3. Static File Optimization

```bash
# Use WhiteNoise for static files
pip install whitenoise

# Add to MIDDLEWARE in settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... other middleware
]

# Configure static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

This deployment guide provides a comprehensive approach to deploying your Django Finance App in production environments with proper security, monitoring, and maintenance procedures.
