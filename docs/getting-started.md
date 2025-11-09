# Getting Started with InsightPulse Odoo

Quick guide to setting up and running InsightPulse Odoo platform.

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- PostgreSQL 15
- DigitalOcean account (for production)

## Local Development Setup

```bash
# Clone the repository
git clone https://github.com/jgtolentino/insightpulse-odoo
cd insightpulse-odoo

# Start services
docker compose up -d

# Access Odoo
# http://localhost:8069
```

## Configuration

1. **Environment Variables**: Copy `.env.example` to `.env`
2. **Database**: Configure PostgreSQL connection
3. **OAuth**: Set up Google OAuth credentials (see spec/platform_spec.json)

## Next Steps

- See [Architecture](architecture.md) for system overview
- See [Deployment Guide](deployments/overview.md) for production setup
- See [Platform Spec](spec-kit/PRD_PLATFORM.md) for detailed requirements

## Documentation

- [Platform Spec](spec-kit/)
- [Pulser Spec](pulser/)
- [Guides](guides/)

## Support

- GitHub Issues: https://github.com/jgtolentino/insightpulse-odoo/issues
- Documentation: https://jgtolentino.github.io/insightpulse-odoo/
