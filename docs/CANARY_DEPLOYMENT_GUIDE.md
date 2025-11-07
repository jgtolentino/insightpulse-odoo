# Canary Deployment Guide

**Status**: ✅ Production Ready
**Issue**: #308 - Implement Canary Deployment Strategy

## Overview

Canary deployment is a progressive rollout strategy that reduces deployment risk by:
1. Deploying new versions to a small subset of users first
2. Monitoring for errors and performance issues
3. Gradually increasing traffic to the new version
4. Automatically rolling back if problems are detected

## How It Works

```
┌─────────────┐
│   Deploy    │ Deploy new version to canary port (8070)
│   Canary    │ Keep stable version on production port (8069)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Configure  │ Split traffic (e.g., 10% canary, 90% stable)
│   Traffic   │ Using nginx weighted load balancing
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Monitor   │ Monitor canary for X minutes
│   Canary    │ Check health endpoint every 30 seconds
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Decide    │ Error rate < threshold?
│ Promote or  │ ├─ Yes → Promote to 100%
│  Rollback   │ └─ No  → Rollback
└─────────────┘
```

## Quick Start

### Basic Canary Deployment

```bash
# Deploy with 10% canary traffic, monitor for 15 minutes
gh workflow run deploy-canary.yml \
  -f image_tag=prod-abc1234 \
  -f canary_percentage=10 \
  -f monitoring_duration=15 \
  -f error_threshold=5 \
  -f auto_promote=true
```

### Conservative Deployment

```bash
# Start with 10%, longer monitoring, lower error tolerance
gh workflow run deploy-canary.yml \
  -f image_tag=prod-abc1234 \
  -f canary_percentage=10 \
  -f monitoring_duration=30 \
  -f error_threshold=2 \
  -f auto_promote=true
```

### Manual Promotion

```bash
# Deploy canary but don't auto-promote
gh workflow run deploy-canary.yml \
  -f image_tag=prod-abc1234 \
  -f canary_percentage=25 \
  -f monitoring_duration=15 \
  -f error_threshold=5 \
  -f auto_promote=false
```

## Parameters

### `image_tag` (required)
Docker image tag to deploy as canary.

**Example**: `prod-abc1234`, `latest`, `v1.2.3`

### `canary_percentage`
Initial percentage of traffic to route to canary.

**Options**: 10%, 25%, 50%
**Default**: 10%
**Recommendation**: Start with 10% for new features, 25% for bug fixes

### `monitoring_duration`
How long to monitor canary before making promotion decision (in minutes).

**Default**: 15 minutes
**Recommendation**:
- New features: 30 minutes
- Bug fixes: 15 minutes
- Hotfixes: 10 minutes

### `error_threshold`
Maximum acceptable error rate percentage for canary.

**Default**: 5%
**Recommendation**:
- Critical services: 2%
- Standard services: 5%
- Non-critical services: 10%

### `auto_promote`
Automatically promote to 100% if canary is healthy.

**Default**: true
**Recommendation**: Use `false` for high-risk deployments requiring manual approval

## Traffic Splitting

The canary deployment uses nginx weighted load balancing:

```nginx
upstream odoo_backend {
    # Stable version - 90%
    server localhost:8069 weight=90;

    # Canary version - 10%
    server localhost:8070 weight=10;

    # Enable session persistence
    ip_hash;
}
```

### Session Persistence
Uses `ip_hash` to ensure users stay on the same backend during their session, preventing confusing version switches.

### Tracking
Every request includes an `X-Canary-Backend` header showing which backend served the request:
- `localhost:8069` = Stable version
- `localhost:8070` = Canary version

## Monitoring

### Health Checks
The canary is monitored every 30 seconds:
- HTTP request to `/web/health`
- Success = HTTP 200
- Failure = Any other status or timeout

### Error Rate Calculation
```
Error Rate = (Failed Checks / Total Checks) × 100%
```

### Automatic Rollback
If error rate exceeds the threshold at any point:
1. Monitoring stops immediately
2. Canary container is stopped and removed
3. Traffic reverts to 100% stable
4. Deployment marked as failed

## Deployment Outcomes

### ✅ Successful Promotion

**Conditions**:
- Error rate ≤ threshold
- Monitoring duration completed
- `auto_promote=true`

**Actions**:
1. Stop stable container
2. Promote canary to production port (8069)
3. Remove nginx traffic split configuration
4. All traffic now on new version

### ❌ Automatic Rollback

**Conditions**:
- Error rate > threshold

**Actions**:
1. Stop and remove canary container
2. Remove nginx traffic split
3. 100% traffic back to stable version
4. Send failure notification

### ⏸️ Hold for Manual Review

**Conditions**:
- Error rate ≤ threshold
- `auto_promote=false`

**Actions**:
1. Keep canary running at configured percentage
2. Wait for manual promotion
3. Manual promotion required via workflow

## Manual Promotion After Hold

If you chose `auto_promote=false` and want to promote after verifying canary:

```bash
# SSH into the droplet
ssh root@165.227.10.178

# Promote canary to production
docker stop odoo
docker rename odoo-canary odoo
docker update --restart=unless-stopped -p 8069:8069 odoo

# Remove traffic split
rm /etc/nginx/conf.d/odoo-canary.conf
nginx -s reload
```

## Manual Rollback

To manually rollback a held canary:

```bash
# SSH into the droplet
ssh root@165.227.10.178

# Remove canary
docker stop odoo-canary
docker rm odoo-canary

# Remove traffic split
rm /etc/nginx/conf.d/odoo-canary.conf
nginx -s reload
```

## Progressive Rollout Strategy

For ultra-conservative deployments:

```bash
# Stage 1: 10% for 15 minutes
gh workflow run deploy-canary.yml \
  -f image_tag=prod-abc1234 \
  -f canary_percentage=10 \
  -f monitoring_duration=15 \
  -f auto_promote=false

# Wait, review metrics, then...

# Stage 2: 25% for 15 minutes
gh workflow run deploy-canary.yml \
  -f image_tag=prod-abc1234 \
  -f canary_percentage=25 \
  -f monitoring_duration=15 \
  -f auto_promote=false

# Stage 3: 50% for 15 minutes
gh workflow run deploy-canary.yml \
  -f image_tag=prod-abc1234 \
  -f canary_percentage=50 \
  -f monitoring_duration=15 \
  -f auto_promote=true
```

## Troubleshooting

### Canary not receiving traffic

**Check nginx configuration**:
```bash
cat /etc/nginx/conf.d/odoo-canary.conf
nginx -t
```

**Check canary is running**:
```bash
docker ps | grep canary
curl http://localhost:8070/web/health
```

### High error rate

**Check canary logs**:
```bash
docker logs odoo-canary
docker logs odoo-canary --tail 100 --follow
```

**Check database connection**:
```bash
docker exec odoo-canary odoo shell -d odoo_canary
```

### Canary not starting

**Check image exists**:
```bash
docker images | grep odoo-erp
```

**Check port conflicts**:
```bash
netstat -tlnp | grep 8070
```

## Best Practices

### 1. Use for High-Risk Changes
- New features
- Database migrations
- Third-party API integrations
- Performance optimizations

### 2. Skip for Low-Risk Changes
- Documentation updates
- CSS/styling changes
- Non-critical bug fixes

### 3. Monitor External Metrics
While canary monitors health endpoints, also watch:
- Error rates in application logs
- Response times
- Database query performance
- User feedback/support tickets

### 4. Plan Rollback Time
Keep stable version ready for immediate rollback. Don't delete old containers/images until canary is fully promoted.

### 5. Communicate During Canary
Notify your team when canary is running:
- Some users will see new version
- Bug reports may vary
- Metrics may show dual-version behavior

## Integration with Other Workflows

### With Consolidated Deployment
```bash
# 1. Build and push image
gh workflow run deploy-consolidated.yml \
  -f environment=production \
  -f deployment_type=odoo-only

# 2. Get the image tag from workflow output

# 3. Deploy as canary
gh workflow run deploy-canary.yml \
  -f image_tag=prod-abc1234 \
  -f canary_percentage=10
```

### With Rollback Workflow
```bash
# If canary is promoted but issues arise later
gh workflow run rollback.yml \
  -f environment=production \
  -f deployment_id=<previous-deployment>
```

## Metrics and Monitoring

### Key Metrics to Watch

| Metric | Source | Healthy Threshold |
|--------|--------|-------------------|
| HTTP 200 rate | Health endpoint | > 95% |
| Response time | Application logs | < 2s |
| Error logs | Docker logs | < 10/min |
| Database connections | PostgreSQL | < 80% max |

### Monitoring Commands

```bash
# Watch canary logs
docker logs odoo-canary -f

# Check current traffic split
curl -I https://erp.insightpulseai.net | grep X-Canary-Backend

# Monitor error rate
docker logs odoo-canary --tail 100 | grep ERROR | wc -l
```

## Related Documentation
- [Deployment Consolidation](DEPLOYMENT_CONSOLIDATION.md)
- [Rollback Guide](../README.md#rollback)
- [Health Monitoring](REAL_TIME_ALERTS_SETUP.md)

## Related Issues
- Issue #308: Implement Canary Deployment Strategy ✅ Completed
- Issue #305: Consolidate Deployment Workflows ✅ Completed
