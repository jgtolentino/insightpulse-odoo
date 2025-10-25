# Docker Setup for InsightPulse Odoo

This repository includes a complete Docker setup for building and deploying Odoo 19.0 with custom addons, following DigitalOcean best practices.

## 🚀 Quick Start

### Option 1: Simple Setup (Official Image)

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd insightpulse-odoo
   cp .env.example .env
   ```

2. **Start the services:**
   ```bash
   docker compose up -d
   ```

3. **Initialize Odoo database:**
   - Visit: http://localhost:8069
   - Create a new database
   - Master password: `admin` (or set your own)

### Option 2: Custom Build (Full Control)

1. **Build custom image:**
   ```bash
   docker compose -f docker-compose.custom.yml up -d --build
   ```

2. **Multi-architecture build:**
   ```bash
   ./build-multiarch.sh
   ```

### CI/CD Pipeline

The repository includes GitHub Actions for automated Docker builds:

- **Triggers:** Push to `main` branch, tags `v*`, `release-*`
- **Platforms:** Multi-architecture (AMD64 + ARM64)
- **Registry:** Docker Hub (`jgtolentino/insightpulse-odoo`)

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `docker-compose.yml` | **Simple setup** - Official Odoo image |
| `docker-compose.custom.yml` | **Custom build** - Build from source with addons |
| `Dockerfile` | Custom Odoo build (follows DO best practices) |
| `build-multiarch.sh` | Multi-architecture build script |
| `.github/workflows/docker-build.yml` | CI/CD pipeline |
| `.env.example` | Configuration template |
| `test-docker-setup.sh` | Setup validation script |

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REGISTRY_USER` | jgtolentino | Docker Hub username |
| `ODOO_REF` | 19.0 | Odoo version to build |
| `POSTGRES_DB` | odoo | Database name |
| `POSTGRES_USER` | odoo | Database user |
| `POSTGRES_PASSWORD` | odoo | Database password |
| `PLATFORM_DB` | - | Platform override for database |
| `PLATFORM_ODOO` | - | Platform override for Odoo |

### GitHub Secrets Required

Set these in your repository settings:

- `REGISTRY_TOKEN`: Docker Hub personal access token
- `REGISTRY_USER`: Docker Hub username (set as variable)

## 🏗️ Build Process

### Local Build

```bash
# Build the image
docker compose build

# Build with no cache
docker compose build --no-cache

# View build logs
docker compose logs odoo
```

### CI/CD Build

The GitHub Actions workflow:

1. Checks out code
2. Logs into Docker Hub
3. Sets up Docker Buildx with cloud builder
4. Builds multi-architecture image
5. Pushes to Docker Hub with tags:
   - `latest`
   - `{commit-sha}`

## 🧪 Testing

Run the validation script:

```bash
./test-docker-setup.sh
```

This checks:
- Docker daemon status
- Image pull capability
- Configuration files
- Docker Compose syntax

## 📦 Image Details

- **Base:** Python 3.11-slim
- **Odoo:** 19.0 (from source)
- **Addons:** Custom addons from `addons/` directory
- **Architecture:** Multi-platform (linux/amd64, linux/arm64/v8)
- **Size:** ~1.2GB (optimized)

## 🔍 Troubleshooting

### Common Issues

1. **Build fails with network errors:**
   - Check internet connectivity
   - Retry the build (temporary network issues)

2. **Docker login fails:**
   - Verify Docker Hub credentials
   - Check if token has expired

3. **Platform-specific issues:**
   - Use `PLATFORM_DB` and `PLATFORM_ODOO` variables
   - Example: `PLATFORM_DB=linux/arm64/v8`

### Debug Commands

```bash
# Check Docker status
docker info

# View container logs
docker compose logs odoo

# Access container shell
docker compose exec odoo bash

# Check image details
docker buildx imagetools inspect jgtolentino/insightpulse-odoo:latest
```

## 🚀 Deployment

### Production Deployment

1. **Pull the image:**
   ```bash
   docker pull jgtolentino/insightpulse-odoo:latest
   ```

2. **Run with production settings:**
   ```bash
   docker run -d \
     --name odoo \
     -p 8069:8069 \
     -e DB_HOST=your-db-host \
     -e DB_USER=your-db-user \
     -e DB_PASSWORD=your-db-password \
     jgtolentino/insightpulse-odoo:latest
   ```

### Docker Compose Production

```yaml
version: "3.8"
services:
  odoo:
    image: jgtolentino/insightpulse-odoo:latest
    environment:
      DB_HOST: your-db-host
      DB_USER: your-db-user
      DB_PASSWORD: your-db-password
    ports:
      - "8069:8069"
```

## 📚 Additional Resources

- [Odoo Documentation](https://www.odoo.com/documentation/19.0/)
- [Docker Multi-arch Builds](https://docs.docker.com/build/building/multi-platform/)
- [GitHub Actions](https://docs.github.com/en/actions)
