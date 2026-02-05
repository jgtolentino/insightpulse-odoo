# Monorepo Structure

This repository follows a **Supabase-first monorepo layout** with clear separation of concerns for database, edge functions, runtime execution, and tooling.

## Directory Structure

```
/
├── supabase/                    # 🎯 CANONICAL DEPLOY SURFACE
│   ├── config.toml              # Supabase project configuration
│   ├── migrations/              # Database migrations
│   ├── functions/               # Edge Functions (Deno/TypeScript)
│   ├── seed.sql                 # Database seed data
│   └── sql/                     # SQL utilities and helpers
│
├── runtime/                     # Execution scaffolding
│   ├── odoo/                    # Odoo 19 runtime
│   │   ├── docker-compose.yml   # Odoo + PostgreSQL services
│   │   ├── odoo.conf            # Odoo config (env-substituted)
│   │   ├── entrypoint.d/        # Custom entrypoint scripts
│   │   └── scripts/             # Runtime utilities
│   └── supabase/                # Local Supabase wrappers (optional)
│
├── apps/                        # Application frontends (optional)
│   ├── web/                     # Next.js platform UI
│   └── admin/                   # Internal ops UI
│
├── vendor/                      # External dependencies
│   ├── odoo/                    # Odoo 19 source (git submodule/subtree)
│   └── oca/                     # OCA community modules
│
├── addons/                      # Custom Odoo modules
│   └── ipai/                    # InsightPulse AI addons (OCA-style)
│
├── tools/                       # Development and automation tools
│   └── claude-plugin/           # Claude tooling bundle
│       ├── .claude-plugin/      # Plugin metadata
│       ├── .superclaude/        # Orchestration system
│       ├── agents/              # Agent implementations
│       ├── skills/              # Skills library
│       ├── commands/            # Command definitions
│       └── anthropic_skills/    # Anthropic skills
│
├── scripts/                     # Repository utilities
│   ├── repo_check.sh            # Structure validation
│   ├── odoo_up.sh               # Start Odoo runtime
│   ├── odoo_down.sh             # Stop Odoo runtime
│   ├── supabase_up.sh           # Start Supabase (local)
│   └── validate.sh              # Full validation suite
│
└── .github/workflows/           # CI/CD pipelines
    └── ci.yml                   # Main CI workflow with repo checks
```

## Key Principles

### 1. Supabase is Canonical

The `supabase/` directory is the **single source of truth** for:
- Database schema and migrations
- Edge Functions (serverless TypeScript/Deno)
- Database seeding and fixtures

All deployment tooling assumes `supabase/` as the primary surface.

### 2. Runtime is Scaffolding

The `runtime/` directory contains **execution infrastructure**:
- Docker Compose configurations
- Service orchestration
- Local development wrappers

Runtime configurations:
- Use environment variable substitution
- Never contain secrets (use `.env` files)
- Are optimized for local development and testing

### 3. Vendor for External Code

The `vendor/` directory contains **third-party dependencies**:
- Odoo 19 source code (via git submodule, subtree, or Docker image)
- OCA community modules
- Other external libraries

This keeps external code separate from custom implementations.

### 4. Addons for Custom Code

The `addons/` directory contains **custom Odoo modules** following OCA conventions:
- One module per subdirectory
- Proper `__manifest__.py` files
- Test coverage and documentation
- Clean separation from OCA modules

### 5. Tools for Automation

The `tools/` directory contains **development tooling**:
- Claude plugin bundle (agents, skills, commands)
- CI/CD utilities
- Code generation tools
- Analysis and reporting scripts

Claude tooling is isolated in `tools/claude-plugin/` to avoid contaminating core infrastructure.

## Usage

### Validate Repository Structure

```bash
bash scripts/repo_check.sh
```

This checks for:
- Required directories (`supabase/`, `runtime/odoo/`, etc.)
- Critical configuration files
- Proper isolation of concerns

### Start Odoo Runtime

```bash
bash scripts/odoo_up.sh
# or directly:
cd runtime/odoo
docker compose up -d
```

### Start Supabase (Local Development)

```bash
bash scripts/supabase_up.sh
# or directly:
supabase start
```

### Check Services Status

```bash
# Odoo
cd runtime/odoo
docker compose ps

# Supabase
supabase status
```

## Environment Configuration

Create a `.env` file at the repository root:

```bash
# Odoo Runtime
ODOO_DB_NAME=odoo
ODOO_DB_USER=odoo
ODOO_DB_PASSWORD=your_secure_password

# Supabase (if using local instance)
SUPABASE_PROJECT_ID=your_project_id
SUPABASE_DB_PASSWORD=your_db_password
```

**Never commit the `.env` file.** Use `.env.example` for documentation.

## Integration Patterns

### Supabase ↔ Odoo Sync

For bidirectional sync between Supabase and Odoo:

1. Implement Edge Functions in `supabase/functions/odoo-sync/`
2. Use Odoo XML-RPC/JSON-RPC connectors
3. Add idempotent migrations in `supabase/migrations/`
4. Keep sync logic in Supabase (canonical surface)

Example:
```
supabase/functions/odoo-sync/
├── index.ts              # Main edge function
├── odoo-client.ts        # XML-RPC client
└── sync-handlers.ts      # Sync logic
```

### Adding Custom Odoo Modules

1. Create module in `addons/ipai/your_module/`
2. Follow OCA structure and conventions
3. Add to `addons/` path in `runtime/odoo/odoo.conf`
4. Document in module README

### Deploying Edge Functions

```bash
# Deploy all functions
supabase functions deploy

# Deploy specific function
supabase functions deploy odoo-sync
```

## CI/CD

The `.github/workflows/ci.yml` workflow runs on every PR and push to main:

1. **Repo Structure Check** - Validates directory layout
2. **Lint** - Checks code quality
3. **Test** - Runs test suites
4. **Build** - Validates build artifacts

## Odoo Source Strategy

Three options for Odoo source:

### Option 1: Official Docker Image (Current)

```yaml
# runtime/odoo/docker-compose.yml
services:
  odoo:
    image: odoo:19.0
```

**Pros:** Fast, simple, maintained by Odoo  
**Cons:** Less control over patches

### Option 2: Pinned Version

```yaml
services:
  odoo:
    image: odoo:19.0.20240101
```

**Pros:** Reproducible builds  
**Cons:** Manual version updates

### Option 3: Build from Source

```yaml
services:
  odoo:
    build:
      context: ../../vendor/odoo
      dockerfile: Dockerfile
```

**Pros:** Full control, custom patches  
**Cons:** Longer build times, maintenance overhead

## Migration Guide

If you're working with the previous structure:

1. **Database migrations** → Already in `supabase/migrations/`
2. **Edge Functions** → Already in `supabase/functions/`
3. **Odoo config** → Now in `runtime/odoo/`
4. **Custom modules** → Already in `addons/`
5. **OCA modules** → Already in `vendor/oca/`
6. **Claude tooling** → Now in `tools/claude-plugin/`

The main changes are:
- Runtime execution moved to `runtime/`
- Claude tooling consolidated in `tools/claude-plugin/`
- Clear separation between canonical deploy surface and execution scaffolding

## Further Reading

- [Runtime README](runtime/README.md) - Detailed runtime documentation
- [Claude Plugin README](tools/claude-plugin/README.md) - Claude tooling documentation
- [Supabase Docs](https://supabase.com/docs) - Official Supabase documentation
- [OCA Guidelines](https://github.com/OCA/maintainer-tools) - OCA module standards
