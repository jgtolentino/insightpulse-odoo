# Superset Dashboard Automation Skill

**Production-ready Apache Superset deployment for DigitalOcean App Platform**

Annual savings: **$8,400** vs Tableau 10-user license

## What's Included

```
superset-dashboard-automation/
├── SKILL.md                          # Main skill documentation
├── deployment/
│   ├── digitalocean-spec.yaml        # Production app spec
│   └── initialization.md             # Step-by-step setup guide
├── examples/
│   ├── bir-dashboard.md              # BIR compliance dashboard
│   ├── create-dataset.md             # Dataset creation examples
│   ├── chart-selection.md            # Chart type selection
│   └── multi-agency-consolidation.md # Multi-agency reporting
└── reference/
    ├── chart-selection-guide.md      # Visualization best practices
    ├── dataset-patterns.md           # SQL patterns for datasets
    ├── dashboard-templates.md        # Pre-built templates
    ├── performance-tuning.md         # Optimization guide
    └── supabase-integration.md       # Supabase setup
```

## Quick Start

### 1. Upload to Claude

Upload this entire folder to Claude.ai:

1. Go to claude.ai
2. Click **Settings** > **Feature Preview** > **Developer Tools**
3. Enable **Claude Skills**
4. Click **+ Add Skill**
5. Upload the `superset-dashboard-automation` folder

### 2. Deploy Superset

**Option A: App Platform (Easier)**
```bash
# Install doctl
brew install doctl  # macOS
# or: snap install doctl  # Linux

# Authenticate
doctl auth init

# Deploy from spec
doctl apps create --spec deployment/digitalocean-spec.yaml
```

**Option B: Droplets (More Control)**
```bash
# Create droplet
doctl compute droplet create superset-prod \
  --image ubuntu-24-04-x64 \
  --size s-2vcpu-4gb \
  --region sgp1

# SSH and run automated installer
ssh root@DROPLET_IP
curl -fsSL https://example.com/setup.sh | bash
```

See: [Deployment Comparison](deployment/droplet-vs-appplatform.md)

### 3. Initialize Database

```bash
# Get app ID
APP_ID=$(doctl apps list --format ID --no-header | head -1)

# Open console
doctl apps console $APP_ID superset

# Inside console:
superset db upgrade
superset fab create-admin --username admin --email admin@example.com --password YourPassword
superset init
exit
```

### 4. Start Building Dashboards

Ask Claude:
```
"Create BIR compliance dashboard"
"Build expense analytics dashboard"
"Generate dataset for trial balance"
```

## Key Features

### ✅ DO-Aligned Deployment
- Volume persistence at `/app/superset_home`
- Proper instance sizing (professional-xs minimum)
- Manual initialization via console (not jobs)
- Pinned version tags (no 'latest')
- Managed Redis integration

### ✅ Finance SSC Templates
- BIR monthly filing tracker
- AP aging analysis
- Travel & expense analytics
- Month-end closing dashboard
- Multi-agency consolidation

### ✅ Best Practices
- Optimized SQL with materialized views
- Row-level security for multi-agency data
- Automated refresh schedules
- Performance tuning guides
- Chart type selection framework

## Critical Fixes Applied

### Before (Common Mistakes)
```yaml
# ❌ Missing volume
services:
  - name: superset
    # No volumes section

# ❌ POST_DEPLOY job (hangs)
jobs:
  - kind: POST_DEPLOY

# ❌ Instance too small
instance_size_slug: basic-xxs  # 512MB

# ❌ Using 'latest' tag
tag: latest
```

### After (DO Best Practices)
```yaml
# ✅ Volume persistence
volumes:
  - name: superset-data
    mount_path: /app/superset_home

# ✅ Manual initialization
# No jobs section, use console

# ✅ Proper sizing
instance_size_slug: professional-xs  # 1GB

# ✅ Pinned version
tag: "3.1.0"
```

## Cost Analysis

**DigitalOcean Stack:**
- Superset (professional-xs): $12/month
- Managed Redis: $15/month
- **Total: $27/month = $324/year**

**Tableau Alternative:**
- 10-user license: $700/month
- **Total: $8,400/year**

**Annual Savings: $8,076** 🎯

## Use Cases

### BIR Compliance (Philippines)
- Track Form 1601-C withholding
- Monitor 2550Q VAT filing
- ATP expiry calendar
- Multi-agency tax consolidation

### Finance Shared Service Center
- Cash position monitoring
- AP aging analysis
- AR collections tracking
- Month-end closing progress
- Budget vs actual reporting

### Operational Analytics
- Travel & expense tracking
- Vendor performance analysis
- Department cost allocation
- Procurement analytics
- Project financial tracking

## Documentation

### Deployment
- `deployment/digitalocean-spec.yaml` - Complete app spec with comments
- `deployment/initialization.md` - Step-by-step setup guide

### Examples
- `examples/bir-dashboard.md` - BIR compliance dashboard walkthrough
- `examples/create-dataset.md` - Dataset creation patterns
- `examples/chart-selection.md` - Choosing the right visualization

### Reference
- `reference/chart-selection-guide.md` - Visualization framework
- `reference/dataset-patterns.md` - SQL best practices
- `reference/dashboard-templates.md` - Pre-built templates
- `reference/performance-tuning.md` - Optimization techniques
- `reference/supabase-integration.md` - Database connection setup

## Troubleshooting

### Issue: Deployment Hangs
**Cause**: POST_DEPLOY job with console command  
**Fix**: Remove jobs, use manual console initialization

### Issue: Data Lost on Redeploy
**Cause**: Missing volume configuration  
**Fix**: Add volumes section mounting `/app/superset_home`

### Issue: Out of Memory
**Cause**: Instance too small (basic-xxs = 512MB)  
**Fix**: Upgrade to professional-xs (1GB) minimum

### Issue: Can't Login
**Cause**: Database not initialized  
**Fix**: Run `superset db upgrade` and `superset init` via console

See `deployment/initialization.md` for complete troubleshooting guide.

## Integration with Your Stack

### Supabase PostgreSQL
```yaml
- key: DATABASE_URL
  value: postgresql://postgres:password@db.spdtwktxdalcfigzeqrz.supabase.co:5432/postgres
  type: SECRET
```

### Odoo ERP
Connect to Odoo database for financial data:
```
Database: Odoo Production
URI: postgresql://odoo:password@odoo-host:5432/odoo
```

### Multi-Agency Architecture
Row-level security for RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB agencies.

## Support

- **DigitalOcean Support**: https://docs.digitalocean.com/products/app-platform/
- **Superset Documentation**: https://superset.apache.org/docs/intro
- **GitHub Issues**: Report bugs or request features

## Version History

### v2.0.0 (Current)
- ✅ DO-aligned deployment (no POST_DEPLOY jobs)
- ✅ Volume persistence configuration
- ✅ Proper instance sizing guidance
- ✅ Manual initialization workflow
- ✅ Managed Redis integration
- ✅ Pinned version tags

### v1.0.0
- Initial release
- Basic deployment spec
- Dashboard templates
- Chart selection guide

## License

MIT License - Free to use and modify

## Contributing

Improvements welcome! Key areas:
- Additional dashboard templates
- More SQL patterns for specific use cases
- Performance optimization techniques
- Integration examples with other tools

## Next Steps

1. ✅ Upload skill to Claude
2. ✅ Deploy Superset to DigitalOcean
3. ✅ Initialize via console
4. ✅ Create first dashboard
5. ✅ Set up automated refreshes
6. ✅ Configure row-level security
7. ✅ Add custom domain

**Your production-ready Tableau alternative awaits!** 📊

---

**Questions?** Ask Claude:
```
"Help me deploy Superset"
"How do I create a BIR dashboard?"
"Show me AP aging visualization"
"Optimize my dataset queries"
```
