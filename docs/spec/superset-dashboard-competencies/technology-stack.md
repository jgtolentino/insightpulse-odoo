# Apache Superset Technology Stack Reference

> Quick reference for technologies used in Superset dashboard development

## Frontend Stack

| Technology | Version | Purpose | Documentation |
|------------|---------|---------|---------------|
| **React** | 18.x | UI Framework | [react.dev](https://react.dev) |
| **TypeScript** | 5.x | Type safety | [typescriptlang.org](https://www.typescriptlang.org) |
| **Redux** | 4.x | State management | [redux.js.org](https://redux.js.org) |
| **Redux Thunk** | 2.x | Async actions | [github.com/reduxjs/redux-thunk](https://github.com/reduxjs/redux-thunk) |
| **Ant Design** | 5.x | UI components | [ant.design](https://ant.design) |
| **Emotion** | 11.x | CSS-in-JS | [emotion.sh](https://emotion.sh) |
| **react-grid-layout** | 1.4.x | Dashboard grid | [github.com/react-grid-layout](https://github.com/react-grid-layout/react-grid-layout) |
| **ECharts** | 5.x | Charts | [echarts.apache.org](https://echarts.apache.org) |
| **Webpack** | 5.x | Bundling | [webpack.js.org](https://webpack.js.org) |

## Backend Stack

| Technology | Version | Purpose | Documentation |
|------------|---------|---------|---------------|
| **Python** | 3.9+ | Runtime | [python.org](https://www.python.org) |
| **Flask** | 2.x | Web framework | [flask.palletsprojects.com](https://flask.palletsprojects.com) |
| **Flask-AppBuilder** | 4.x | Admin/RBAC | [flask-appbuilder.readthedocs.io](https://flask-appbuilder.readthedocs.io) |
| **SQLAlchemy** | 1.4.x | ORM | [sqlalchemy.org](https://www.sqlalchemy.org) |
| **Alembic** | 1.x | Migrations | [alembic.sqlalchemy.org](https://alembic.sqlalchemy.org) |
| **Celery** | 5.x | Task queue | [docs.celeryq.dev](https://docs.celeryq.dev) |
| **Marshmallow** | 3.x | Serialization | [marshmallow.readthedocs.io](https://marshmallow.readthedocs.io) |
| **Gunicorn** | 21.x | WSGI server | [gunicorn.org](https://gunicorn.org) |

## Database & Cache

| Technology | Version | Purpose | Documentation |
|------------|---------|---------|---------------|
| **PostgreSQL** | 13+ | Metadata DB | [postgresql.org](https://www.postgresql.org) |
| **Redis** | 6+ | Cache/Queue | [redis.io](https://redis.io) |
| **psycopg2** | 2.x | PG driver | [psycopg.org](https://www.psycopg.org) |

## Testing Stack

| Technology | Version | Purpose | Documentation |
|------------|---------|---------|---------------|
| **Jest** | 29.x | JS unit tests | [jestjs.io](https://jestjs.io) |
| **React Testing Library** | 14.x | Component tests | [testing-library.com](https://testing-library.com) |
| **Cypress** | 13.x | E2E tests | [cypress.io](https://www.cypress.io) |
| **pytest** | 7.x | Python tests | [pytest.org](https://pytest.org) |
| **Storybook** | 7.x | Visual testing | [storybook.js.org](https://storybook.js.org) |

## DevOps & Infrastructure

| Technology | Version | Purpose | Documentation |
|------------|---------|---------|---------------|
| **Docker** | 24+ | Containerization | [docker.com](https://www.docker.com) |
| **Docker Compose** | 2.x | Local dev | [docs.docker.com/compose](https://docs.docker.com/compose) |
| **Kubernetes** | 1.28+ | Orchestration | [kubernetes.io](https://kubernetes.io) |
| **Helm** | 3.x | K8s packaging | [helm.sh](https://helm.sh) |
| **GitHub Actions** | - | CI/CD | [github.com/features/actions](https://github.com/features/actions) |

## Superset-Specific Packages

| Package | Purpose | npm |
|---------|---------|-----|
| `@superset-ui/core` | Core utilities | [npmjs.com](https://www.npmjs.com/package/@superset-ui/core) |
| `@superset-ui/chart-controls` | Chart config UI | [npmjs.com](https://www.npmjs.com/package/@superset-ui/chart-controls) |
| `@superset-ui/embedded-sdk` | Embedding SDK | [npmjs.com](https://www.npmjs.com/package/@superset-ui/embedded-sdk) |
| `@superset-ui/plugin-chart-*` | Chart plugins | Various |

## Key Configuration Files

| File | Purpose |
|------|---------|
| `superset_config.py` | Main configuration |
| `package.json` | Frontend dependencies |
| `requirements.txt` | Python dependencies |
| `docker-compose.yml` | Local development |
| `tsconfig.json` | TypeScript config |
| `.eslintrc.js` | ESLint rules |
| `pyproject.toml` | Python tools config |

## Minimum Development Requirements

### Hardware
- **RAM**: 8GB minimum, 16GB recommended
- **CPU**: 4 cores minimum
- **Storage**: 20GB free space

### Software
- **OS**: macOS or Linux (Windows via WSL2)
- **Node.js**: 18.x LTS
- **Python**: 3.9+
- **Docker**: 24+
- **Git**: 2.x

### IDE Recommendations
- **VS Code** with extensions:
  - ESLint
  - Prettier
  - Python
  - TypeScript
  - Docker
- **PyCharm Professional** (alternative)

## Version Compatibility Matrix

| Superset Version | Python | Node.js | PostgreSQL | Redis |
|------------------|--------|---------|------------|-------|
| 4.0.x | 3.9-3.11 | 18.x | 13-16 | 6-7 |
| 3.1.x | 3.9-3.11 | 16.x | 12-15 | 6-7 |
| 3.0.x | 3.9-3.10 | 16.x | 12-15 | 6-7 |
| 2.1.x | 3.8-3.10 | 16.x | 12-14 | 5-6 |

## Quick Setup Commands

```bash
# Clone repository
git clone https://github.com/apache/superset.git
cd superset

# Frontend setup
cd superset-frontend
npm ci
npm run dev

# Backend setup (new terminal)
cd superset
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Database setup
superset db upgrade
superset init
superset load-examples

# Run development server
superset run -p 8088 --with-threads --reload
```

## Common Development Ports

| Service | Port | URL |
|---------|------|-----|
| Superset (dev) | 8088 | http://localhost:8088 |
| Frontend (webpack) | 9000 | http://localhost:9000 |
| Storybook | 6006 | http://localhost:6006 |
| PostgreSQL | 5432 | - |
| Redis | 6379 | - |
| Celery Flower | 5555 | http://localhost:5555 |
