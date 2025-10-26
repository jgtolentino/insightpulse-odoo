# InsightPulse Odoo

Enterprise-grade Odoo 19.0 deployment with advanced BI integrations (Apache Superset, MindsDB) and comprehensive development agent capabilities.

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/jgtolentino/insightpulse-odoo.git
cd insightpulse-odoo

# Start Odoo with Docker
docker compose up -d

# Access Odoo
open http://localhost:8069
```

## 📚 Documentation

### Core Documentation
- **[KNOWLEDGE.md](docs/KNOWLEDGE.md)** - Agent skills, design principles, Odoo-Superset connector implementation
- **[SKILLS.md](docs/SKILLS.md)** - Comprehensive skill listing (Odoo, Python, SQL, BI, Superset, security, deployment)
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Production deployment guide with security, scaling, monitoring, and backup
- **[AGENT.md](docs/AGENT.md)** - Agent setup, usage patterns, and function reference

### BI & Analytics Documentation
- **[SUPERSET_INTEGRATION.md](docs/SUPERSET_INTEGRATION.md)** - Complete Superset integration guide with setup, configuration, and troubleshooting
- **[BI_ARCHITECTURE.md](docs/BI_ARCHITECTURE.md)** - BI architecture, data flow, security layers, and performance optimization
- **[SUPERSET_DASHBOARDS.md](docs/SUPERSET_DASHBOARDS.md)** - Superset dashboard design, RLS, multi-company analytics

### Deployment Guides
- **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - Docker containerization and CI/CD pipeline
- **[MindsDB Integration](docs/mindsdb.md)** - AI-powered analytics integration

## 🛠️ Features

### Odoo Development Agent
Expert-level AI assistant for:
- **Module Development**: Scaffolding, models, views, security
- **Data Connectors**: Odoo → Superset, Odoo → BI tools
- **Dashboard Design**: Professional Superset dashboards
- **Production Deployment**: Docker, CI/CD, security hardening

### Data & Analytics
- **Apache Superset**: Open-source BI with row-level security
- **MindsDB**: AI-powered predictive analytics
- **Analytics Views**: Pre-built SQL views for sales, finance, HR, inventory
- **Multi-Company Support**: Isolated data access per company

### DevOps & CI/CD
- **Docker**: Multi-architecture builds (AMD64, ARM64)
- **GitHub Actions**: Automated testing, building, deployment
- **Monitoring**: Prometheus, Grafana integration ready
- **Backup**: Automated database and filestore backups

## 📁 Repository Structure

```
insightpulse-odoo/
├── .github/
│   └── workflows/          # CI/CD workflows
│       ├── agent-eval.yml  # Agent evaluation and testing
│       ├── dockerhub-publish.yml
│       └── feature-inventory.yml
├── datasets/               # Reference data for agent
│   ├── odoo_sa.json       # Odoo solution architecture
│   ├── oca_index.json     # OCA module index
│   └── market_caps.yaml   # Market capabilities matrix
├── docs/                   # Comprehensive documentation
│   ├── KNOWLEDGE.md       # Agent knowledge base
│   ├── SKILLS.md          # Skills inventory
│   ├── DEPLOYMENT.md      # Production deployment
│   ├── AGENT.md           # Agent usage guide
│   └── SUPERSET_DASHBOARDS.md  # Dashboard design
├── rules/                  # Agent decision rules
│   └── selection.yaml     # Module/pattern selection rules
├── schemas/                # Validation schemas
│   └── feature_request.yaml
├── scripts/                # Utility scripts
│   ├── appsrc.py          # Application source analysis
│   ├── vendor_oca.py      # OCA module vendoring
│   ├── connectors.py      # API connector functions
│   └── feature_inventory.py  # Feature inventory generation
├── docker/                 # Docker configurations
├── Dockerfile             # Multi-stage Odoo build
└── requirements.txt       # Python dependencies
```

## 🔧 Utility Scripts

### Application Source Analysis
Analyze Odoo module structure and dependencies:
```bash
python scripts/appsrc.py --scan ./addons --output datasets/app_structure.json
```

### OCA Module Vendoring
Search and vendor OCA modules:
```bash
# Update OCA index
python scripts/vendor_oca.py --update-index

# Search for modules
python scripts/vendor_oca.py --search "rest api"

# Vendor a module
python scripts/vendor_oca.py --module base_rest --target ./addons/
```

### API Connectors
```python
from scripts.connectors import odoo_rpc_call, supabase_sql, superset_api

# Fetch sales orders via RPC
orders = odoo_rpc_call(
    url='http://localhost:8069',
    db='odoo',
    username='admin',
    password='admin',
    model='sale.order',
    method='search_read',
    args=[[('state', '=', 'sale')], ['name', 'amount_total']]
)

# Query Superset API
dashboards = superset_api(
    base_url='https://superset.example.com',
    endpoint='/api/v1/dashboard/',
    auth_token='Bearer xxx'
)
```

## 🏗️ Architecture

### Technology Stack
- **Odoo**: 19.0 (Python 3.11)
- **Database**: PostgreSQL 15+
- **Container**: Docker 24.0+
- **BI**: Apache Superset 3.0+
- **Cache**: Redis 7+
- **AI**: MindsDB (optional)

### BI Integration Architecture

```
┌─────────────────┐     Guest Token      ┌─────────────────┐
│   Odoo Users    │ ◄──────────────────► │ Apache Superset │
└────────┬────────┘    Authentication     └────────┬────────┘
         │                                          │
         │ Embedded                        SQL Queries (RLS)
         │ Dashboards                               │
         │                                          │
         ▼                                          ▼
┌─────────────────────────────────────────────────────────┐
│              PostgreSQL (Odoo Database)                 │
│  - Analytics Views (vw_sales_kpi_day, etc.)            │
│  - Row-Level Security                                   │
│  - Read-only user (superset_readonly)                  │
└─────────────────────────────────────────────────────────┘
```

**Key Features:**
- **Secure Embedding**: Guest token authentication for dashboard iframes
- **Row-Level Security (RLS)**: Multi-company data isolation
- **Pre-built Analytics**: SQL views for Sales, Inventory, Accounting, HR
- **SSO Integration**: Seamless authentication between Odoo and Superset

See [BI_ARCHITECTURE.md](docs/BI_ARCHITECTURE.md) for detailed architecture documentation.

### Deployment Options
1. **Development**: `docker compose up`
2. **Production**: See [DEPLOYMENT.md](docs/DEPLOYMENT.md)
3. **Cloud**: DigitalOcean, AWS, Google Cloud, Azure

## 🔐 Security

### Built-in Security Features
- Read-only database users for BI tools
- Row-level security (RLS) for multi-company
- API key authentication
- SSL/TLS encryption
- Automated backup and recovery

See [DEPLOYMENT.md - Security Hardening](docs/DEPLOYMENT.md#security-hardening) for details.

## 📊 Sample Dashboards

Pre-configured Superset dashboards:
- **Sales Executive Overview**: Revenue, orders, trends, top products
- **Financial Performance**: P&L, cash flow, AR aging
- **Inventory Operations**: Stock levels, turnover, warehouse metrics
- **HR Analytics**: Headcount, attendance, productivity

See [SUPERSET_DASHBOARDS.md](docs/SUPERSET_DASHBOARDS.md) for configurations.

## 🤖 Odoo Development Agent

The agent provides expert assistance with:

### Usage Patterns

**Create a Module**:
```
Create a sales commission module that calculates commissions 
for salespeople based on configurable rules.
```

**Implement Data Connector**:
```
Implement a connector to export sales data to Superset with 
daily aggregation and multi-company filtering.
```

**Design Dashboard**:
```
Design a Superset dashboard for sales executives showing 
revenue trends, top products, and regional performance.
```

**Troubleshoot Performance**:
```
Our sales reports are slow. Help diagnose and optimize.
```

See [AGENT.md](docs/AGENT.md) for complete usage guide.

## 🧪 Testing & Quality

### CI/CD Workflows
- **Structure Validation**: Verify required files exist
- **Documentation Validation**: Check documentation completeness
- **Configuration Validation**: Validate YAML/JSON syntax
- **Script Testing**: Test Python scripts
- **Golden Prompts**: Evaluate agent capabilities

### Run Tests Locally
```bash
# Validate structure
python scripts/appsrc.py --scan . --output /tmp/structure.json

# Validate configs
python -m yaml --verify rules/selection.yaml
python -m json.tool datasets/odoo_sa.json > /dev/null

# Test scripts
python scripts/appsrc.py --help
python scripts/vendor_oca.py --help
```

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and validation
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Quality Standards
- Follow OCA guidelines for Odoo modules
- Use type hints in Python code
- Document all functions with docstrings
- Write tests for new features
- Update documentation

## 📝 License

This project is licensed under the LGPL-3.0 License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Odoo Community Association (OCA)](https://github.com/OCA) for community modules
- [Apache Superset](https://superset.apache.org/) for open-source BI
- [MindsDB](https://mindsdb.com/) for AI-powered analytics

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/jgtolentino/insightpulse-odoo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jgtolentino/insightpulse-odoo/discussions)
- **Documentation**: [docs/](docs/)

## 🗺️ Roadmap

- [ ] Kubernetes deployment templates
- [ ] Automated module testing framework
- [ ] Pre-built Superset dashboard library
- [ ] Integration with additional BI tools (Metabase, Grafana)
- [ ] Enhanced MindsDB integration
- [ ] Multi-language documentation

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-26  
**Odoo Version**: 19.0  
**Status**: Production Ready ✅
