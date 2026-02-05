# System Design Map 2026 - InsightPulse Odoo

**Version**: 1.0  
**Last Updated**: 2026-02-05  
**Single Source of Truth (SSOT)**: `ops/ssot/system_design_map.yaml`

---

## Overview

This document provides a comprehensive system design reference for the InsightPulse Odoo platform. It serves as the **canonical documentation** for architecture decisions, technology stack, and operational procedures. All implementation details must align with the SSOT defined in `system_design_map.yaml`.

---

## 1. System Design Fundamentals

### Architecture Principles
- **Microservices Architecture**: Services are loosely coupled and independently deployable
- **Event-Driven Workflows**: Asynchronous processing where appropriate
- **API-First Design**: All functionality exposed via well-defined APIs

### Core Technology Stack
- **Odoo 18 CE**: Enterprise Resource Planning core
- **PostgreSQL 15**: Primary relational database
- **Docker Compose**: Container orchestration
- **Nginx**: Reverse proxy and load balancing
- **Caddy**: Automatic TLS certificate management

### Owners
- DevOps Team
- Backend Team

---

## 2. Service Communication

### Communication Patterns
- **XML-RPC**: Odoo API endpoints
- **REST APIs**: Supabase, n8n, and external integrations
- **PostgreSQL Direct Connections**: ETL and data sync operations
- **Webhooks**: GitHub automation, event notifications

### Inter-Service Communication
- **Synchronous**: XML-RPC calls for immediate responses
- **Asynchronous**: Webhooks for event-driven workflows
- **Database-Level CDC**: Change Data Capture for data synchronization

### Owners
- Backend Team
- Integration Team

---

## 3. Load Balancing & Traffic Management

### Load Balancing Strategy
- **Nginx**: Primary load balancer with round-robin distribution
- **Caddy**: Automatic HTTPS with Let's Encrypt
- **DigitalOcean App Platform**: Managed load balancing for production

### Health Checks
- All services must expose health check endpoints
- Load balancer monitors `/health` endpoints
- Automatic failover on health check failures

### Owners
- DevOps Team
- SRE Team

---

## 4. Database & Storage

### Database Architecture
- **Odoo Primary Database**: PostgreSQL 15 on DigitalOcean Managed Postgres
- **Analytics Warehouse**: Supabase PostgreSQL
- **Object Storage**: MinIO for file storage

### Replication & Backup
- **Master-Replica Replication**: Read scalability
- **Connection Pooling**: PgBouncer for efficient connection management
- **Automated Backups**: Daily at 3 AM UTC
- **PITR**: Point-in-Time Recovery enabled

### Performance Optimization
- Indexed queries on frequently accessed tables
- Connection pooling to reduce overhead
- Read replicas for analytics workloads

### Owners
- Data Engineering Team
- Backend Team

---

## 5. Caching & CDN

### Multi-Level Caching Strategy
- **L1 Cache (Redis)**: Session data, frequently accessed objects
- **L2 Cache (Nginx)**: Proxy cache for static assets
- **Browser Cache**: Client-side caching with proper headers

### Cache Invalidation
- Time-based expiration (TTL)
- Event-based invalidation on data updates
- Manual purge for critical updates

### Owners
- DevOps Team
- Frontend Team

---

## 6. Scalability & Fault Tolerance

### Horizontal Scaling
- **Docker Swarm**: Future implementation for container scaling
- **Database Read Replicas**: Distribute read load
- **Stateless Services**: Enable easy horizontal scaling

### Fault Tolerance Mechanisms
- **Circuit Breaker Pattern**: Prevent cascading failures
- **Graceful Degradation**: Maintain core functionality during partial outages
- **Automated Health Monitoring**: Proactive failure detection

### Disaster Recovery
- **Automated Backups**: Daily database and file backups
- **Quarterly Restore Drills**: Verify backup integrity
- **RPO**: 24 hours (Recovery Point Objective)
- **RTO**: 4 hours (Recovery Time Objective)

### Owners
- DevOps Team
- SRE Team

---

## 7. Observability & Monitoring

### Monitoring Requirements
All services must implement:
- **Health Check Endpoints**: `/health` returning 200 OK
- **Structured JSON Logs**: Parseable, machine-readable logs
- **Correlation IDs**: Track requests across service boundaries
- **Performance Metrics**: Response time, error rate, throughput

### Monitoring Stack
- **Structured Logging**: JSON format with correlation IDs
- **Superset Dashboards**: Business intelligence and metrics
- **GitHub Actions**: CI/CD pipeline monitoring
- **Alert Thresholds**: Defined in SSOT

### Alert Thresholds
| Metric | Warning | Critical |
|--------|---------|----------|
| CPU Usage | 70% | 85% |
| Memory Usage | 75% | 90% |
| Disk Usage | 80% | 90% |
| Response Time | 2000ms | 5000ms |

### Owners
- SRE Team
- DevOps Team

---

## 8. Security & Reliability

### Secrets Management
- **No Secrets in Git**: Enforced via pre-commit hooks
- **GitHub Secrets**: CI/CD environment variables
- **Supabase Vault**: Edge function secrets
- **Environment Files**: DO droplet secrets (outside repo)

### Security Controls
- **TLS Everywhere**: TLS 1.3 minimum
- **Row-Level Security (RLS)**: Supabase table-level access control
- **Security Headers**: HSTS, CSP, X-Frame-Options
- **Automated Secret Rotation**: Quarterly or on-demand

### Compliance Requirements
- All secrets must be in secure vaults
- Quarterly secret rotation
- TLS 1.3 minimum protocol version
- Security headers properly configured

### Owners
- Security Team
- DevOps Team

---

## 9. Real-World Production Patterns

### Deployment Strategies
- **Blue-Green Deployments**: Zero-downtime updates
- **Canary Releases**: Gradual rollout to production
- **Automated Rollbacks**: Revert on health check failures

### Production Infrastructure
- **DigitalOcean Droplets**: Primary compute
- **DigitalOcean Managed Postgres**: Production database
- **Supabase**: Managed backend services
- **GitHub Actions**: CI/CD automation

### Operational Procedures
- **Daily Automated Backups**: 3 AM UTC (Odoo DB), 4 AM UTC (files)
- **Quarterly Restore Drills**: Validate backup/restore process
- **Monthly Security Patches**: Operating system and dependencies
- **On-Demand Scaling**: Vertical scaling for traffic spikes

### Owners
- DevOps Team
- SRE Team

---

## Operational Standards

### Backup Schedule
| Component | Schedule | Retention |
|-----------|----------|-----------|
| Odoo Database | Daily 3 AM UTC | 30 days |
| Supabase | Continuous PITR | 7 days |
| File Storage | Daily 4 AM UTC | 30 days |

### Recovery Objectives
- **RPO (Recovery Point Objective)**: 24 hours
- **RTO (Recovery Time Objective)**: 4 hours

### Required Health Endpoints
| Service | Endpoint | Expected Response |
|---------|----------|-------------------|
| Odoo | `/health` | 200 OK |
| Supabase | `/rest/v1/` | 200 OK |
| n8n | `/healthz` | 200 OK |

---

## Compliance & Standards

### Enterprise Standards
✅ Enterprise-grade backups  
✅ Observability minimum  
✅ Secrets management  
✅ Disaster recovery  

### Required Runbooks
1. **Backups and Restore Drill** (`docs/runbooks/RUNBOOK_Backups_Restore_Drill.md`)
2. **Observability Minimum** (`docs/runbooks/RUNBOOK_Observability_Minimum.md`)
3. **Secrets Management** (`docs/runbooks/RUNBOOK_Secrets_Management.md`)
4. **Incident Response** (existing in `docs/runbooks/`)
5. **Service Restart Procedures** (`docs/runbooks/service-restart.md`)

---

## Validation & Enforcement

### CI/CD Enforcement
All pull requests must pass enterprise standards validation:

```bash
python scripts/validate_enterprise_standards.py
```

This validation checks:
- ✅ Required SSOT files exist
- ✅ YAML structure is valid
- ✅ All 9 domains are defined
- ✅ Each domain has `stack` and `owners`
- ✅ Required runbooks are present

### Failure Handling
PRs that fail validation will be blocked until:
1. Missing files are added
2. SSOT structure is corrected
3. Domain definitions are complete

---

## Maintenance & Updates

### SSOT Maintenance
- **Owner**: DevOps Team Lead
- **Review Cycle**: Quarterly or on architectural changes
- **Update Process**:
  1. Propose changes via PR
  2. Review with stakeholders
  3. Update SSOT YAML
  4. Update this documentation
  5. Communicate changes to teams

### Version History
| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-02-05 | Initial SSOT creation | GitHub Copilot |

---

## References

- **SSOT YAML**: `ops/ssot/system_design_map.yaml`
- **Architecture Docs**: `docs/architecture/`
- **Runbooks**: `docs/runbooks/`
- **CI Workflows**: `.github/workflows/enterprise-standards.yml`

---

**This is a living document**. All changes must be synchronized with the SSOT YAML file to maintain consistency.
