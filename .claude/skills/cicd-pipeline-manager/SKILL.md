---
name: cicd-pipeline-manager
description: Comprehensive CI/CD pipeline management with GitHub Actions, Docker, Digital Ocean CLI, and Odoo CLI integration
version: 1.0.0
tags: [ci-cd, github-actions, docker, digital-ocean, odoo-cli, deployment, automation]
requires:
  files:
    - superclaude/knowledge/ODOO_19_REFERENCE.md
    - docker-compose.yml
    - scripts/droplet-setup.sh
uses:
  skills:
    - odoo-sh-devops
    - connector-integration-expert
    - odoo-apps-manager
---

# CI/CD Pipeline Manager Skill

## Purpose

Manage complete CI/CD pipelines using GitHub Actions, Docker, Digital Ocean CLI, and Odoo CLI for automated testing, building, and deployment of Odoo applications.

## When to use

- Setting up automated GitHub Actions workflows
- Building and deploying Docker containers
- Managing Digital Ocean infrastructure via CLI
- Automating Odoo module installation and upgrades
- Implementing blue-green deployments
- Managing environment-specific configurations

## Actions

1. **GitHub Actions Setup**: Create and manage CI/CD workflows
2. **Docker Pipeline**: Build, test, and deploy Docker containers
3. **Digital Ocean Automation**: Provision and manage infrastructure
4. **Odoo CLI Integration**: Automate Odoo operations
5. **Environment Management**: Handle staging, production, and development environments
6. **Monitoring & Rollback**: Implement monitoring and automated rollback procedures

## Inputs

- `pipeline_type`: Type of pipeline (testing, deployment, full-ci-cd)
- `target_environment`: Environment to deploy to (staging, production)
- `docker_config`: Docker build and deployment configuration
- `infrastructure_provider`: Infrastructure provider (digital-ocean, aws, azure)
- `odoo_operations`: Odoo-specific operations (install, upgrade, migrate)

## Outputs

- GitHub Actions workflow files
- Docker build configurations
- Digital Ocean provisioning scripts
- Odoo CLI automation scripts
- Environment configuration files
- Monitoring and alerting setup

## Examples

### Example 1: Full CI/CD Pipeline Setup
```
User: "Set up complete CI/CD pipeline for Odoo with GitHub Actions and Digital Ocean"

Agent:
1. Creates GitHub Actions workflow for automated testing
2. Sets up Docker build and push to registry
3. Configures Digital Ocean deployment automation
4. Implements Odoo module installation and upgrade automation
5. Sets up monitoring and health checks
6. Provides rollback procedures
```

### Example 2: Automated Testing Pipeline
```
User: "Create automated testing pipeline for Odoo modules"

Agent:
1. Sets up GitHub Actions for unit and integration tests
2. Configures test database setup and teardown
3. Implements code quality checks (pylint, black, isort)
4. Sets up test coverage reporting
5. Creates automated test result notifications
```

### Example 3: Production Deployment Pipeline
```
User: "Set up production deployment pipeline with blue-green deployment"

Agent:
1. Creates blue-green deployment strategy
2. Sets up load balancer configuration
3. Implements database migration automation
4. Configures health checks and monitoring
5. Creates rollback automation procedures
```

## GitHub Actions Integration

### Complete CI/CD Workflow
```yaml
# .github/workflows/ci-cd.yml
name: Odoo CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: odoo
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Run tests
      run: |
        python -m pytest tests/ --cov=addons --cov-report=xml
        
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
        
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        
    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to Digital Ocean
      uses: appleboy/ssh-action@v1
      with:
        host: ${{ secrets.DIGITALOCEAN_HOST }}
        username: ${{ secrets.DIGITALOCEAN_USERNAME }}
        key: ${{ secrets.DIGITALOCEAN_SSH_KEY }}
        script: |
          cd /opt/odoo19
          docker-compose pull
          docker-compose up -d
          docker system prune -f
```

### Odoo-Specific Testing Workflow
```yaml
# .github/workflows/odoo-tests.yml
name: Odoo Module Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  odoo-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_DB: test
          POSTGRES_USER: odoo
          POSTGRES_PASSWORD: odoo
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:6
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v4
    
    - name: Start Odoo test container
      run: |
        docker run -d \
          --name odoo-test \
          --link postgres:db \
          --link redis:redis \
          -e HOST=db \
          -e USER=odoo \
          -e PASSWORD=odoo \
          -e DATABASE=test \
          odoo:19 \
          odoo -i base --test-enable --stop-after-init --without-demo=all
        
    - name: Check test results
      run: |
        docker logs odoo-test
        if docker logs odoo-test 2>&1 | grep -q "ERROR"; then
          echo "Tests failed"
          exit 1
        fi
```

## Docker Pipeline Automation

### Multi-stage Docker Build
```dockerfile
# Dockerfile for Odoo with OCA modules
FROM odoo:19.0 as builder

# Install build dependencies
USER root
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Clone OCA modules
RUN git clone https://github.com/OCA/web.git /mnt/oca-web
RUN git clone https://github.com/OCA/server-tools.git /mnt/oca-server-tools

FROM odoo:19.0

# Copy OCA modules
COPY --from=builder /mnt/oca-web /mnt/extra-addons/oca-web
COPY --from=builder /mnt/oca-server-tools /mnt/extra-addons/oca-server-tools

# Install Python dependencies
USER root
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

# Set proper permissions
RUN chown -R odoo:odoo /mnt/extra-addons

USER odoo

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=300s \
  CMD curl -f http://localhost:8069/web/health || exit 1
```

### Docker Compose for Production
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - odoo_network

  redis:
    image: redis:6-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - odoo_network

  odoo:
    image: ${DOCKER_REGISTRY}/odoo:${ODOO_VERSION}
    depends_on:
      - postgres
      - redis
    environment:
      HOST: postgres
      USER: ${POSTGRES_USER}
      PASSWORD: ${POSTGRES_PASSWORD}
      REDIS_HOST: redis
    volumes:
      - odoo_data:/var/lib/odoo
      - ./addons:/mnt/extra-addons
    networks:
      - odoo_network
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - odoo
    networks:
      - odoo_network

volumes:
  postgres_data:
  redis_data:
  odoo_data:

networks:
  odoo_network:
    driver: bridge
```

## Digital Ocean CLI Automation

### Infrastructure Provisioning Script
```bash
#!/bin/bash
# digitalocean-provision.sh

set -e

# Digital Ocean CLI commands for infrastructure provisioning
echo "Provisioning Digital Ocean infrastructure..."

# Create droplet
doctl compute droplet create odoo-production \
  --image ubuntu-22-04-x64 \
  --size s-2vcpu-4gb \
  --region nyc3 \
  --ssh-keys $(doctl compute ssh-key list --format ID --no-header | tr '\n' ',') \
  --tag-name odoo \
  --wait

# Create load balancer
doctl compute load-balancer create \
  --name odoo-lb \
  --region nyc3 \
  --forwarding-rules "protocol:http,entry_port:80,target_port:8069" \
  --health-check "protocol:http,port:8069,path:/web/health" \
  --tag-name odoo

# Create database cluster
doctl databases create odoo-db \
  --engine pg \
  --version 14 \
  --region nyc3 \
  --size db-s-1vcpu-1gb \
  --num-nodes 1

# Create firewall rules
doctl compute firewall create \
  --name odoo-firewall \
  --inbound-rules "protocol:tcp,ports:22,address:0.0.0.0/0 protocol:tcp,ports:80,address:0.0.0.0/0 protocol:tcp,ports:443,address:0.0.0.0/0" \
  --tag-names odoo

echo "Infrastructure provisioning complete!"
```

### Deployment Automation Script
```bash
#!/bin/bash
# digitalocean-deploy.sh

set -e

DROPLET_IP=$(doctl compute droplet list --tag-name odoo --format PublicIPv4 --no-header | head -1)

if [ -z "$DROPLET_IP" ]; then
  echo "No Odoo droplet found"
  exit 1
fi

echo "Deploying to droplet: $DROPLET_IP"

# Copy deployment files
scp -o StrictHostKeyChecking=no \
  docker-compose.prod.yml \
  .env.production \
  root@$DROPLET_IP:/opt/odoo19/

# Execute deployment
ssh -o StrictHostKeyChecking=no root@$DROPLET_IP << 'EOF'
  cd /opt/odoo19
  docker-compose -f docker-compose.prod.yml pull
  docker-compose -f docker-compose.prod.yml down
  docker-compose -f docker-compose.prod.yml up -d
  docker system prune -f
EOF

echo "Deployment completed successfully!"
```

## Odoo CLI Integration

### Automated Module Management
```python
#!/usr/bin/env python3
# odoo-cli-automation.py

import subprocess
import sys
import time

class OdooCLIAutomation:
    """Automate Odoo CLI operations"""
    
    def __init__(self, host, port, database, username, password):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        
    def install_modules(self, modules):
        """Install Odoo modules"""
        cmd = [
            'docker', 'exec', 'odoo',
            'odoo', '-d', self.database,
            '-i', ','.join(modules),
            '--stop-after-init',
            '--without-demo=all'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Module installation failed: {result.stderr}")
            return False
        return True
        
    def upgrade_modules(self, modules):
        """Upgrade Odoo modules"""
        cmd = [
            'docker', 'exec', 'odoo',
            'odoo', '-d', self.database,
            '-u', ','.join(modules),
            '--stop-after-init'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Module upgrade failed: {result.stderr}")
            return False
        return True
        
    def backup_database(self, backup_path):
        """Backup Odoo database"""
        cmd = [
            'docker', 'exec', 'postgres',
            'pg_dump', '-U', self.username,
            '-d', self.database,
            '-f', backup_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
```

### Database Migration Script
```bash
#!/bin/bash
# odoo-database-migration.sh

set -e

echo "Starting Odoo database migration..."

# Backup current database
docker exec postgres pg_dump -U odoo -d odoo_prod -f /tmp/backup.sql

# Install new modules
docker exec odoo odoo -d odoo_prod -i new_module1,new_module2 --stop-after-init

# Upgrade existing modules
docker exec odoo odoo -d odoo_prod -u base,web,sale --stop-after-init

# Run data migration scripts
docker exec odoo python3 -c "
import xmlrpc.client
url = 'http://localhost:8069'
db = 'odoo_prod'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
# Perform data migration operations
print('Data migration completed')
"

echo "Database migration completed successfully!"
```

## Environment Management

### Environment Configuration
```bash
#!/bin/bash
# setup-environments.sh

# Production environment
cat > .env.production << EOF
POSTGRES_DB=odoo_prod
POSTGRES_USER=odoo
POSTGRES_PASSWORD=$(openssl rand -base64 32)
ODOO_VERSION=19.0
DOCKER_REGISTRY=ghcr.io/your-org
EOF

# Staging environment
cat > .env.staging << EOF
POSTGRES_DB=odoo_staging
POSTGRES_USER=odoo
POSTGRES_PASSWORD=$(openssl rand -base64 32)
ODOO_VERSION=19.0
DOCKER_REGISTRY=ghcr.io/your-org
EOF
```

## Success Metrics

### Pipeline Performance
- **Build Time**: < 10 minutes for complete pipeline
- **Test Coverage**: ≥ 80% automated test coverage
- **Deployment Success**: ≥ 95% successful deployments
- **Rollback Time**: < 5 minutes for automated rollback

### Infrastructure
