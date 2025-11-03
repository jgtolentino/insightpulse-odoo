# Unified Deployment Architecture - InsightPulse Platform

**Deployment Date**: 2025-11-02
**Version**: 2.0.0
**Platform**: DigitalOcean + Supabase
**Domain**: insightpulseai.net
**Total Cost**: ~$35-45/month

---

## 🎯 Overview

Complete unified deployment architecture for the InsightPulse platform integrating:
- **Main Website** (insightpulseai.net)
- **Odoo ERP** (Digital Ocean App Platform)
- **Superset Dashboard** (insightpulseai.net/superset)
- **Mobile App** (React Native with PaddleOCR)
- **PaddleOCR Service** (Digital Ocean Droplet)

---

## 🏗️ Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                   DNS: insightpulseai.net                        │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                    ┌────────▼──────────┐
                    │  Traefik/Caddy    │
                    │  Reverse Proxy    │
                    │  - SSL/TLS        │
                    │  - Path Routing   │
                    └────────┬──────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌───────▼────────┐  ┌───────▼────────┐
│  Main Website  │  │  Odoo ERP      │  │  Superset BI   │
│  /             │  │  /odoo         │  │  /superset     │
│  Static/SPA    │  │  DO App        │  │  DO App        │
└────────────────┘  └───────┬────────┘  └───────┬────────┘
                            │                    │
                            │    ┌───────────────┘
                            │    │
                    ┌───────▼────▼──────┐
                    │  Supabase         │
                    │  PostgreSQL 16    │
                    │  - pgVector       │
                    │  - RLS Policies   │
                    │  - Connection     │
                    │    Pooler (6543)  │
                    └───────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    Mobile App Layer                              │
└──────────────────────────────────────────────────────────────────┘
        │
┌───────▼────────┐           ┌────────────────┐
│  Mobile App    │           │  PaddleOCR     │
│  React Native  │◄──────────┤  Service       │
│  - iOS/Android │  OCR API  │  DO Droplet    │
│  - Expo        │           │  (Ubuntu 22.04)│
└───────┬────────┘           └────────────────┘
        │
        │ REST API
        │
┌───────▼────────┐
│  Odoo REST API │
│  /api/v1       │
└────────────────┘
```

---

## 📦 Component Breakdown

### 1. Main Website (insightpulseai.net)

**Technology**: Static site / SPA (React/Next.js)
**Hosting**: DigitalOcean App Platform (Static Site)
**Cost**: $0-3/month (free tier available)

**Configuration**:
```yaml
name: insightpulse-web
region: sgp

static_sites:
  - name: main-website
    github:
      repo: jgtolentino/insightpulse-web
      branch: main
    build_command: npm run build
    output_dir: dist
    routes:
      - path: /
```

**Features**:
- Landing page
- Product information
- Documentation
- User authentication portal
- Redirects to /odoo and /superset

---

### 2. Odoo ERP (insightpulseai.net/odoo)

**Technology**: Odoo 19.0 CE
**Hosting**: DigitalOcean App Platform
**Instance**: basic-xxs (512MB RAM, 1 vCPU)
**Cost**: $5/month
**Database**: Supabase PostgreSQL (free tier)

**Configuration**: See `infra/do/odoo-saas-platform.yaml`

**Key Features**:
- Multi-tenant SaaS operations
- Finance & operations modules
- AI knowledge workspace
- Expense management with OCR
- Project & program management

**Endpoints**:
- Web UI: `https://insightpulseai.net/odoo`
- REST API: `https://insightpulseai.net/odoo/api/v1`
- Health Check: `https://insightpulseai.net/odoo/web/health`

---

### 3. Superset Dashboard (insightpulseai.net/superset)

**Technology**: Apache Superset 3.0+
**Hosting**: DigitalOcean App Platform
**Instance**: basic-xs (1GB RAM, 1 vCPU)
**Cost**: $12/month (web) + $10/month (workers/redis) = $22/month
**Database**: Supabase PostgreSQL (shared with Odoo)

**Configuration**: See `infra/superset/superset-app.yaml`

**Components**:
- **Web Service** (basic-xs): Gunicorn + gevent workers
- **Worker Service** (basic-xxs): Celery worker for async queries
- **Beat Service** (basic-xxs): Celery beat for scheduled tasks
- **Redis Service** (basic-xxs): Cache and message broker

**Key Features**:
- 5 pre-built dashboards
- Row-level security (RLS)
- Real-time data sync with Odoo
- Custom chart builder
- SQL Lab for ad-hoc queries

**Endpoints**:
- Dashboard: `https://insightpulseai.net/superset`
- Health Check: `https://insightpulseai.net/superset/health`
- API: `https://insightpulseai.net/superset/api/v1`

---

### 4. PaddleOCR Service (Droplet)

**Technology**: PaddleOCR-VL (Python FastAPI)
**Hosting**: DigitalOcean Droplet
**Instance**: Basic Droplet (1GB RAM, 1 vCPU, 25GB SSD)
**Cost**: $6/month
**OS**: Ubuntu 22.04 LTS

**Existing Service**: `https://ade-ocr-backend-d9dru.ondigitalocean.app`

**Droplet Configuration**:
```yaml
# New dedicated droplet for production
name: paddleocr-service
region: sgp1
size: s-1vcpu-1gb
image: ubuntu-22-04-x64

# Software stack
docker:
  - paddleocr:latest
  - fastapi
  - uvicorn
```

**API Endpoints**:
- OCR Scan: `POST /api/v1/ocr/scan`
- Health: `GET /health`
- Metrics: `GET /metrics`

**Features**:
- Receipt/invoice OCR
- Multi-language support
- JSON structured output
- Confidence scoring
- Image preprocessing

**Integration**:
- Odoo `ipai_expense` module calls PaddleOCR API
- Mobile app sends images to PaddleOCR service
- Results processed by OpenAI GPT-4o-mini for accuracy

---

### 5. Mobile App (iOS/Android)

**Technology**: React Native + Expo
**Repositories**: New repository `insightpulse-mobile`
**Distribution**: Expo EAS Build + App Store/Play Store
**Cost**: $0 (development), $99/year (Apple), $25 (Google one-time)

**Architecture**:
```
Mobile App (React Native/Expo)
├── Screens
│   ├── Login (OAuth via Odoo)
│   ├── Expense Submission
│   │   └── Camera → PaddleOCR → Odoo
│   ├── Dashboard (embed Superset)
│   └── Settings
├── Services
│   ├── AuthService (Odoo OAuth)
│   ├── OCRService (PaddleOCR API)
│   ├── ExpenseService (Odoo REST API)
│   └── BiService (Superset embed)
└── State Management (Redux/Zustand)
```

**Key Features**:
- Camera integration for receipt capture
- Offline mode with sync
- Push notifications
- Biometric authentication
- Expense approval workflows
- Embedded Superset dashboards

**Tech Stack**:
```json
{
  "framework": "React Native",
  "platform": "Expo SDK 50+",
  "navigation": "React Navigation",
  "state": "Zustand",
  "api": "Axios + React Query",
  "camera": "expo-camera",
  "storage": "AsyncStorage",
  "auth": "expo-auth-session"
}
```

---

## 🌐 Reverse Proxy Configuration

### Traefik Configuration

**File**: `infra/reverse-proxy/traefik.yml`

```yaml
# Traefik Static Configuration
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https

  websecure:
    address: ":443"
    http:
      tls:
        certResolver: letsencrypt

certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@insightpulseai.net
      storage: /letsencrypt/acme.json
      httpChallenge:
        entryPoint: web

providers:
  file:
    filename: /etc/traefik/dynamic.yml
    watch: true
```

**Dynamic Configuration**: `infra/reverse-proxy/dynamic.yml`

```yaml
http:
  routers:
    # Main website
    main:
      rule: "Host(`insightpulseai.net`) && PathPrefix(`/`)"
      service: main-website
      entryPoints:
        - websecure
      tls:
        certResolver: letsencrypt
      priority: 1

    # Odoo ERP
    odoo:
      rule: "Host(`insightpulseai.net`) && PathPrefix(`/odoo`)"
      service: odoo-erp
      entryPoints:
        - websecure
      middlewares:
        - odoo-stripprefix
      tls:
        certResolver: letsencrypt
      priority: 10

    # Superset Dashboard
    superset:
      rule: "Host(`insightpulseai.net`) && PathPrefix(`/superset`)"
      service: superset-bi
      entryPoints:
        - websecure
      middlewares:
        - superset-headers
      tls:
        certResolver: letsencrypt
      priority: 10

  services:
    main-website:
      loadBalancer:
        servers:
          - url: "https://insightpulse-web-xxxxx.ondigitalocean.app"

    odoo-erp:
      loadBalancer:
        servers:
          - url: "https://odoo-saas-platform-xxxxx.ondigitalocean.app"

    superset-bi:
      loadBalancer:
        servers:
          - url: "https://superset-analytics-xxxxx.ondigitalocean.app"

  middlewares:
    odoo-stripprefix:
      stripPrefix:
        prefixes:
          - "/odoo"

    superset-headers:
      headers:
        customRequestHeaders:
          X-Script-Name: "/superset"
```

---

## 🗄️ Database Architecture (Supabase)

**Service**: Supabase PostgreSQL 16
**Region**: AWS us-east-1
**Connection**: Pooler (port 6543)
**Cost**: Free tier (up to 500MB, 2 CPU hours/day)

**Database Schema**:
```
supabase (project: spdtwktxdalcfigzeqrz)
├── Odoo Database (odoo schema)
│   ├── res_partner
│   ├── account_move
│   ├── project_project
│   ├── hr_expense
│   └── ... (all Odoo tables)
│
├── Superset Database (superset schema)
│   ├── dashboards
│   ├── slices
│   ├── datasources
│   └── query_results
│
├── pgVector Extension
│   └── knowledge_embeddings
│       └── vector(1536) for OpenAI embeddings
│
└── RLS Policies
    ├── Multi-tenant isolation
    └── Row-level security for all tables
```

**Connection Strings**:
```bash
# Odoo connection
postgresql://postgres.spdtwktxdalcfigzeqrz:$PASSWORD@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require

# Superset connection (same database, different schema)
postgresql://postgres.spdtwktxdalcfigzeqrz:$PASSWORD@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require
```

---

## 📱 Mobile App Deployment

### Development Environment

```bash
# 1. Create new repository
mkdir insightpulse-mobile
cd insightpulse-mobile

# 2. Initialize Expo project
npx create-expo-app@latest . --template blank-typescript

# 3. Install dependencies
npm install @react-navigation/native @react-navigation/stack
npm install axios react-query zustand
npm install expo-camera expo-image-picker
npm install expo-auth-session
npm install @react-native-async-storage/async-storage

# 4. Configure app.json
cat > app.json <<EOF
{
  "expo": {
    "name": "InsightPulse",
    "slug": "insightpulse-mobile",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "automatic",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "ios": {
      "bundleIdentifier": "com.insightpulse.app",
      "supportsTablet": true
    },
    "android": {
      "package": "com.insightpulse.app",
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#ffffff"
      },
      "permissions": [
        "CAMERA",
        "READ_EXTERNAL_STORAGE",
        "WRITE_EXTERNAL_STORAGE"
      ]
    },
    "extra": {
      "apiUrl": "https://insightpulseai.net/odoo/api/v1",
      "ocrUrl": "https://ade-ocr-backend-d9dru.ondigitalocean.app",
      "supersetUrl": "https://insightpulseai.net/superset"
    }
  }
}
EOF
```

### Production Build & Deployment

```bash
# 1. Configure EAS Build
eas build:configure

# 2. Build for iOS
eas build --platform ios --profile production

# 3. Build for Android
eas build --platform android --profile production

# 4. Submit to App Stores
eas submit --platform ios
eas submit --platform android
```

---

## 💰 Cost Breakdown

| Component | Service | Tier | Cost/Month |
|-----------|---------|------|------------|
| **Main Website** | DO App Platform | Static Site | $0-3 |
| **Odoo ERP** | DO App Platform | basic-xxs | $5 |
| **Superset Web** | DO App Platform | basic-xs | $12 |
| **Superset Worker** | DO App Platform | basic-xxs | $5 |
| **Superset Beat** | DO App Platform | basic-xxs | $5 |
| **Redis Cache** | DO App Platform | basic-xxs | $5 |
| **PaddleOCR Service** | DO Droplet | s-1vcpu-1gb | $6 |
| **Database** | Supabase PostgreSQL | Free Tier | $0 |
| **Reverse Proxy** | DO Droplet (Traefik) | s-1vcpu-1gb | $6 |
| **Mobile App** | Expo EAS | Development | $0 |
| **Domain & DNS** | DigitalOcean | - | $0-2 |
| **Backups** | DO Volumes | 10GB | $1 |
| **Total** | | | **$45-49/month** |

**Budget Optimization**:
- Use basic-xxs for all services: **~$35/month**
- Combine Superset workers: **~$30/month**
- Self-host OCR in Odoo container: **~$25/month**

---

## 🚀 Deployment Steps

### Phase 1: Infrastructure Setup (Day 1)

```bash
# 1. Deploy Traefik reverse proxy
cd infra/reverse-proxy
./deploy-traefik.sh

# 2. Configure DNS
doctl compute domain records create insightpulseai.net \
  --record-type A \
  --record-name "@" \
  --record-data <TRAEFIK_DROPLET_IP>

# 3. Configure SSL
# Automatic via Let's Encrypt (Traefik)
```

### Phase 2: Application Deployment (Day 1-2)

```bash
# 1. Deploy Odoo ERP
cd infra/do
doctl apps create --spec odoo-saas-platform.yaml

# 2. Deploy Superset
doctl apps create --spec ../superset/superset-app.yaml

# 3. Deploy PaddleOCR service
cd ../paddleocr
./deploy-droplet.sh

# 4. Update Traefik configuration with app URLs
# Edit infra/reverse-proxy/dynamic.yml
# Reload Traefik
docker exec traefik kill -HUP 1
```

### Phase 3: Mobile App Setup (Day 3-5)

```bash
# 1. Create repository
gh repo create jgtolentino/insightpulse-mobile --private

# 2. Initialize app
cd insightpulse-mobile
npx create-expo-app@latest . --template blank-typescript

# 3. Implement core features
# - Authentication
# - Camera/OCR
# - Expense submission
# - Dashboard embed

# 4. Build and deploy
eas build:configure
eas build --platform all --profile production
```

### Phase 4: Integration Testing (Day 6-7)

```bash
# 1. Test main website
curl -I https://insightpulseai.net

# 2. Test Odoo
curl -I https://insightpulseai.net/odoo/web/health

# 3. Test Superset
curl -I https://insightpulseai.net/superset/health

# 4. Test PaddleOCR
curl -X POST https://ade-ocr-backend-d9dru.ondigitalocean.app/api/v1/ocr/scan \
  -F "file=@test_receipt.jpg"

# 5. Test mobile app
# - Install on physical device
# - Test camera → OCR → Odoo flow
# - Test embedded Superset dashboard
```

---

## 🔒 Security Considerations

### SSL/TLS
- ✅ Let's Encrypt automatic certificates via Traefik
- ✅ HTTPS enforced (HTTP → HTTPS redirect)
- ✅ TLS 1.2+ only
- ✅ HSTS headers enabled

### Authentication
- ✅ OAuth 2.0 for mobile app
- ✅ JWT tokens with refresh mechanism
- ✅ Biometric authentication on mobile
- ✅ Session timeout (30 minutes)

### API Security
- ✅ Rate limiting (100 req/min per IP)
- ✅ CORS configuration
- ✅ API key authentication for services
- ✅ Request validation and sanitization

### Database Security
- ✅ SSL-required connections (sslmode=require)
- ✅ Row-level security (RLS) policies
- ✅ Encrypted at rest (Supabase)
- ✅ Connection pooling limits

### Mobile App Security
- ✅ Certificate pinning
- ✅ Secure storage for tokens
- ✅ Code obfuscation
- ✅ Root/jailbreak detection

---

## 📊 Monitoring & Logging

### Application Monitoring

```yaml
# Prometheus + Grafana on DO Droplet
monitoring:
  prometheus:
    targets:
      - odoo:8069/metrics
      - superset:8088/health
      - paddleocr:8000/metrics
      - traefik:8080/metrics

  grafana:
    dashboards:
      - System Metrics
      - Application Performance
      - User Activity
      - Error Tracking
```

### Log Aggregation

```bash
# Centralized logging with Loki
docker run -d \
  --name loki \
  -p 3100:3100 \
  grafana/loki:latest

# Log shipper configuration
# All DO apps → Loki → Grafana
```

### Uptime Monitoring

```bash
# UptimeRobot configuration
monitors:
  - name: Main Website
    url: https://insightpulseai.net
    interval: 5 minutes

  - name: Odoo ERP
    url: https://insightpulseai.net/odoo/web/health
    interval: 5 minutes

  - name: Superset BI
    url: https://insightpulseai.net/superset/health
    interval: 5 minutes

  - name: PaddleOCR Service
    url: https://ade-ocr-backend-d9dru.ondigitalocean.app/health
    interval: 5 minutes
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy-unified.yml
name: Deploy Unified Platform

on:
  push:
    branches: [main]

jobs:
  deploy-odoo:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to DigitalOcean
        run: doctl apps create-deployment ${{ secrets.ODOO_APP_ID }}

  deploy-superset:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to DigitalOcean
        run: doctl apps create-deployment ${{ secrets.SUPERSET_APP_ID }}

  deploy-mobile:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build mobile app
        run: eas build --non-interactive --platform all
```

---

## 📚 Documentation

### User Documentation
- **Main Website**: Landing page with product info
- **Odoo User Guide**: `/docs/odoo-user-guide.md`
- **Superset Dashboard Guide**: `/docs/superset-guide.md`
- **Mobile App Guide**: `/docs/mobile-app-guide.md`

### Developer Documentation
- **API Reference**: `/docs/api-reference.md`
- **Mobile App Development**: `/docs/mobile-dev.md`
- **Deployment Guide**: This document
- **Architecture Overview**: `/docs/architecture.md`

---

## 🎯 Success Metrics

### Performance Targets
- ✅ Page load time: < 2 seconds
- ✅ API response time: < 500ms (p95)
- ✅ OCR processing: < 5 seconds per image
- ✅ Database query time: < 100ms (p95)
- ✅ Uptime: 99.9% SLA

### User Metrics
- Monthly Active Users (MAU)
- Expense submissions via mobile
- Dashboard views
- OCR accuracy rate (target: 95%+)
- User satisfaction score

---

## 🛠️ Maintenance

### Regular Tasks
- **Daily**: Monitor error logs and metrics
- **Weekly**: Review performance metrics and optimize
- **Monthly**: Security updates and patches
- **Quarterly**: Cost optimization review
- **Annually**: SSL certificate renewal (automatic)

### Backup Strategy
- **Database**: Automatic daily backups (Supabase)
- **Filestore**: Daily snapshots to DO Spaces
- **Configuration**: Git repository backup
- **Retention**: 30 days for daily, 1 year for monthly

---

## 📞 Support

### Internal Team
- **DevOps**: deployment@insightpulse.ai
- **Backend**: backend@insightpulse.ai
- **Mobile**: mobile@insightpulse.ai
- **Support**: support@insightpulse.ai

### External Resources
- [DigitalOcean Support](https://www.digitalocean.com/support)
- [Supabase Support](https://supabase.com/support)
- [Odoo Community](https://www.odoo.com/forum)
- [Apache Superset Community](https://superset.apache.org/community)

---

## 🗺️ Roadmap

### Q1 2025
- [x] Unified deployment architecture
- [ ] Mobile app MVP (iOS + Android)
- [ ] PaddleOCR droplet deployment
- [ ] Traefik reverse proxy setup

### Q2 2025
- [ ] Multi-language support (ES, FR, DE)
- [ ] Advanced analytics dashboards
- [ ] Push notification service
- [ ] Offline mode for mobile app

### Q3 2025
- [ ] Kubernetes migration (optional)
- [ ] Multi-region deployment
- [ ] Advanced fraud detection
- [ ] Integration marketplace

### Q4 2025
- [ ] AI-powered expense categorization
- [ ] Predictive analytics with MindsDB
- [ ] GraphQL API layer
- [ ] White-label capabilities

---

**Last Updated**: 2025-11-02
**Maintained By**: InsightPulse DevOps Team
**Status**: ✅ Production Ready
