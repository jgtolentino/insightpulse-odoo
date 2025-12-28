# Apache Superset Dashboard Development Competencies Catalog

> **Committer-Level Skills & Knowledge Framework**
>
> Version: 1.0.0 | Last Updated: 2024-12-28
> Based on Apache Superset 4.x Architecture

## Overview

This catalog defines the comprehensive competencies required for **committer-level** contributions to Apache Superset dashboard development. It covers frontend (React/Redux), backend (Flask/Python), and infrastructure skills organized by domain.

## Competency Levels

| Level | Title | Description |
|-------|-------|-------------|
| **L1** | Contributor | Can fix bugs, add small features, write tests |
| **L2** | Active Contributor | Understands core architecture, reviews PRs, adds features |
| **L3** | Committer | Deep expertise, architectural decisions, mentors others |
| **L4** | PMC Member | Project governance, release management, strategic direction |

---

## 1. Core Architecture Competencies

### 1.1 System Architecture Understanding

**Required for: L2+**

| Component | Technology | Purpose | Documentation |
|-----------|-----------|---------|---------------|
| **Backend** | Python/Flask | REST API, business logic | `superset/` |
| **Frontend** | React/TypeScript | Dashboard UI, interactions | `superset-frontend/` |
| **Database** | PostgreSQL | Metadata storage (dashboards, users) | SQLAlchemy ORM |
| **Cache** | Redis | Query results, session cache | `CACHE_CONFIG` |
| **Async** | Celery | Async queries, scheduled reports | `superset/tasks/` |
| **Charts** | @superset-ui | Visualization plugins | `superset-frontend/plugins/` |

### 1.2 Three-Tier Application Model

```
┌─────────────────────────────────────────────────────────────┐
│  PRESENTATION TIER (React/Redux)                            │
│  • Dashboard components  • Chart renderers  • Filter UI     │
└─────────────────────────────────────────────────────────────┘
                              │ REST API
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  APPLICATION TIER (Flask/Python)                            │
│  • API endpoints  • Security (RBAC)  • Query processing     │
└─────────────────────────────────────────────────────────────┘
                              │ SQLAlchemy
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  DATA TIER                                                  │
│  • Metadata DB (PostgreSQL)  • Data Sources  • Cache Layer  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Frontend Competencies

### 2.1 React/TypeScript Stack

**Required for: L1+**

| Skill | Description | Priority |
|-------|-------------|----------|
| React Hooks | `useState`, `useEffect`, `useCallback`, `useMemo`, `useRef` | Critical |
| TypeScript | Type definitions, generics, utility types | Critical |
| Component Patterns | HOCs, render props, compound components | High |
| Custom Hooks | Creating reusable logic abstractions | High |
| Error Boundaries | Graceful error handling in component tree | Medium |

### 2.2 State Management (Redux)

**Required for: L2+**

| Concept | Application in Superset | Files |
|---------|------------------------|-------|
| Redux Store Shape | Dashboard, filter, chart states | `superset-frontend/src/dashboard/reducers/` |
| Actions & Reducers | Dashboard CRUD, filter updates | `superset-frontend/src/dashboard/actions/` |
| Redux Thunk | Async API calls, data fetching | Async action creators |
| Selectors (Reselect) | Memoized derived state | `selectors.ts` files |
| Redux DevTools | State debugging, action replay | Browser extension |

**Redux Store Structure (Dashboard Domain):**

```typescript
interface SupersetState {
  dashboards: {
    [id: number]: {
      id: number;
      slug: string;
      dashboardTitle: string;
      layout: DashboardLayout;
      charts: { [chartId: number]: ChartState };
      filters: { [filterId: string]: FilterState };
      metadata: DashboardMetadata;
    };
  };
  dashboardFilters: {
    [dashboardId: number]: {
      [filterId: string]: NativeFilter;
    };
  };
  dashboardLayout: {
    isEditing: boolean;
    editingDashboardId: number | null;
  };
}
```

### 2.3 Dashboard Grid System

**Required for: L2+**

| Library | Purpose | Key Concepts |
|---------|---------|--------------|
| `react-grid-layout` | Responsive dashboard grid | 12-column grid, breakpoints |
| Layout Configuration | Grid positioning | `x`, `y`, `w`, `h` coordinates |
| Drag & Drop | Edit mode interactions | `onDragStart`, `onDragEnd` |
| Responsive Design | Mobile/tablet/desktop views | Breakpoint-specific layouts |

**Grid Configuration:**

```typescript
const gridConfig = {
  cols: 12,                    // 12-column grid
  margin: [16, 16],           // Grid margins
  containerPadding: [16, 16], // Container padding
  compactType: 'vertical',    // Vertical compaction
  isDraggable: isEditMode,    // Drag only in edit mode
  isResizable: isEditMode,    // Resize only in edit mode
};
```

### 2.4 Dashboard Component Hierarchy

**Required for: L3+**

```
DashboardContainer (Redux wrapper)
├── DashboardHeader
│   ├── EditModeButton
│   ├── RefreshButton
│   └── ShareButton
├── DashboardGrid (react-grid-layout)
│   └── GridComponent (per item)
│       ├── ChartHolder
│       │   ├── ChartContainer
│       │   ├── CrossFilterBadge
│       │   └── DownloadButton
│       ├── MarkdownComponent
│       └── TabsComponent
└── FilterBar
    ├── NativeFilter
    ├── TimeRangeFilter
    └── FilterIndicator
```

### 2.5 Filter System Architecture

**Required for: L3+**

| Filter Type | Description | Implementation |
|-------------|-------------|----------------|
| Native Filters | UI-based dashboard filters | `FilterBar` component |
| Cross Filters | Click-to-filter charts | `updateDataMask` action |
| Time Range | Temporal filtering | `TimeRangeFilter` component |
| Filter Scopes | Which charts receive filters | `filterScopes` metadata |
| Cascading Filters | Parent-child filter dependencies | `cascadeParentIds` |

**Filter Application Flow:**

```
1. User changes filter value
   ↓
2. dispatch(updateDataMask({filterId, filterState}))
   ↓
3. Redux reducer updates filter state
   ↓
4. publishDataMask() updates URL params
   ↓
5. Connected charts receive new filters via selectors
   ↓
6. Charts re-query data with updated filters
```

### 2.6 Superset-UI Plugin System

**Required for: L3+**

| Package | Purpose | Usage |
|---------|---------|-------|
| `@superset-ui/core` | Core utilities, types | All plugins |
| `@superset-ui/chart-controls` | Chart control panels | Configuration UI |
| `@superset-ui/legacy-preset-chart-*` | Legacy chart plugins | Migration support |
| `@superset-ui/plugin-chart-*` | Modern chart plugins | New visualizations |

**Creating Custom Visualization:**

```typescript
import { ChartPlugin, t } from '@superset-ui/core';

export default class MyChartPlugin extends ChartPlugin {
  constructor() {
    super({
      loadChart: () => import('./MyChart'),
      metadata: {
        name: t('My Custom Chart'),
        thumbnail: 'path/to/thumbnail.png',
        useLegacyApi: false,
      },
    });
  }
}
```

---

## 3. Backend Competencies

### 3.1 Flask Application Structure

**Required for: L2+**

| Module | Purpose | Key Files |
|--------|---------|-----------|
| `superset/` | Main application | `app.py`, `config.py` |
| `superset/models/` | SQLAlchemy ORM models | `dashboard.py`, `slice.py` |
| `superset/dashboards/` | Dashboard APIs | `api.py`, `commands/` |
| `superset/views/` | Legacy Flask views | `dashboard.py` |
| `superset/security/` | RBAC, permissions | `manager.py` |
| `superset/commands/` | Business logic layer | CRUD commands |

### 3.2 Dashboard Data Model

**Required for: L2+**

```python
class Dashboard(Model, AuditMixinNullable):
    """Dashboard ORM model"""
    __tablename__ = 'dashboards'

    id = Column(Integer, primary_key=True)
    dashboard_title = Column(String(500))
    position_json = Column(Text)           # Grid layout
    css = Column(Text)                     # Custom CSS
    json_metadata = Column(Text)           # Filters, etc.
    slug = Column(String(255), unique=True)
    published = Column(Boolean, default=False)

    # Relationships
    slices = relationship('Slice', secondary=dashboard_slices)
    owners = relationship('User', secondary=dashboard_user)
```

**Key Relationships:**

```
Dashboard ─────┬───── Slice (Chart)
               │
               ├───── User (Owners)
               │
               ├───── Role (Permissions)
               │
               └───── DashboardFilterState
```

### 3.3 REST API Patterns

**Required for: L2+**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/dashboard/` | GET | List dashboards |
| `/api/v1/dashboard/{id}` | GET | Get dashboard |
| `/api/v1/dashboard/` | POST | Create dashboard |
| `/api/v1/dashboard/{id}` | PUT | Update dashboard |
| `/api/v1/dashboard/{id}` | DELETE | Delete dashboard |
| `/api/v1/dashboard/{id}/charts` | GET | Get dashboard charts |

**API Response Structure:**

```json
{
  "result": {
    "id": 1,
    "dashboard_title": "Sales Dashboard",
    "slug": "sales-dashboard",
    "position_json": "{...}",
    "json_metadata": "{...}",
    "charts": [...]
  },
  "message": "Success"
}
```

### 3.4 Security & Permissions (RBAC)

**Required for: L3+**

| Permission Type | Description | Application |
|-----------------|-------------|-------------|
| Row-Level Security | Filter data by user | SQL template injection |
| Dashboard Access | View/edit permissions | FAB roles |
| Data Source Access | Database/table access | Schema permissions |
| Feature Flags | Enable/disable features | `FEATURE_FLAGS` config |

**Permission Decorators:**

```python
from superset.views.base import (
    DashboardAccessMixin,
    check_dashboard_access,
)

@expose('/api/v1/dashboard/<id>')
@protect()
@safe
@permission_name('can_read')
def get(self, id: int) -> Response:
    """Get dashboard by ID with permission check"""
    dashboard = self.datamodel.get(id)
    if not self.can_access_dashboard(dashboard):
        raise DashboardForbiddenError()
    return self.response(200, result=dashboard.to_dict())
```

### 3.5 Command Pattern (Business Logic)

**Required for: L3+**

```python
# superset/dashboards/commands/create.py
class CreateDashboardCommand(BaseCommand):
    def __init__(self, data: Dict[str, Any]):
        self._properties = data

    def run(self) -> Dashboard:
        self.validate()
        dashboard = Dashboard(**self._properties)
        db.session.add(dashboard)
        db.session.commit()
        return dashboard

    def validate(self) -> None:
        # Validation logic
        exceptions = []
        if not self._properties.get('dashboard_title'):
            exceptions.append(DashboardInvalidError())
        if exceptions:
            raise DashboardCreateFailedError(exceptions)
```

### 3.6 Query Processing

**Required for: L3+**

| Component | Purpose | Files |
|-----------|---------|-------|
| SQLAlchemy | ORM & query building | `superset/sql_lab.py` |
| Jinja Templates | SQL templating | `superset/jinja_context.py` |
| Query Object | Query representation | `superset/common/query_object.py` |
| Query Context | Full query context | `superset/common/query_context.py` |

---

## 4. Infrastructure Competencies

### 4.1 Configuration Management

**Required for: L2+**

| Config Area | File | Key Settings |
|-------------|------|--------------|
| Core Config | `superset_config.py` | `SQLALCHEMY_DATABASE_URI`, `SECRET_KEY` |
| Feature Flags | `FEATURE_FLAGS` | Dashboard features toggle |
| Cache Config | `CACHE_CONFIG` | Redis settings |
| Security | `AUTH_TYPE` | Authentication method |

**Critical Dashboard Feature Flags:**

```python
FEATURE_FLAGS = {
    'DASHBOARD_NATIVE_FILTERS': True,      # Native filter UI
    'DASHBOARD_CROSS_FILTERS': True,       # Cross-chart filtering
    'DASHBOARD_NATIVE_FILTERS_SET': True,  # Filter sets
    'EMBEDDED_SUPERSET': False,            # Embedding support
    'ENABLE_TEMPLATE_PROCESSING': True,    # Jinja SQL templates
}
```

### 4.2 Database Administration

**Required for: L2+**

| Skill | Description | Commands |
|-------|-------------|----------|
| Migrations | Schema changes | `superset db upgrade` |
| Initialization | Bootstrap data | `superset init` |
| Admin Creation | User management | `superset fab create-admin` |
| Data Import | Sample data | `superset load-examples` |

### 4.3 Caching Strategy

**Required for: L3+**

| Cache Layer | Purpose | Configuration |
|-------------|---------|---------------|
| Redis Cache | Query results | `CACHE_CONFIG` |
| Results Backend | Async query results | `RESULTS_BACKEND` |
| Data Cache | Dashboard data | `DATA_CACHE_CONFIG` |
| Thumbnail Cache | Dashboard previews | `THUMBNAIL_CACHE_CONFIG` |

### 4.4 Deployment Patterns

**Required for: L3+**

| Environment | Approach | Key Considerations |
|-------------|----------|-------------------|
| Development | Docker Compose | Hot reload, debug mode |
| Production | Kubernetes/Docker | HA, horizontal scaling |
| Embedded | Iframe/SDK | CORS, guest tokens |

---

## 5. Testing Competencies

### 5.1 Testing Pyramid

**Required for: L1+**

```
                 /\
               /    \
              / E2E   \        Cypress, Playwright
             /          \
            /──────────────\
           /   Integration   \  React Testing Library
          /                    \
         /───────────────────────\
        /      Unit Tests         \ Jest, pytest
       /─────────────────────────────\
```

### 5.2 Frontend Testing

**Required for: L2+**

| Tool | Purpose | Files |
|------|---------|-------|
| Jest | Unit tests | `*.test.ts` |
| React Testing Library | Component tests | `*.test.tsx` |
| Storybook | Visual testing | `*.stories.tsx` |
| Cypress | E2E tests | `cypress/` |

**Example Component Test:**

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import DashboardComponent from './DashboardComponent';

describe('DashboardComponent', () => {
  it('renders dashboard title', () => {
    render(
      <Provider store={mockStore}>
        <DashboardComponent id={1} />
      </Provider>
    );
    expect(screen.getByText('Test Dashboard')).toBeInTheDocument();
  });
});
```

### 5.3 Backend Testing

**Required for: L2+**

| Tool | Purpose | Files |
|------|---------|-------|
| pytest | Unit/integration tests | `tests/` |
| pytest-cov | Coverage reporting | CI/CD |
| factory_boy | Test data factories | `tests/factories.py` |

**Example API Test:**

```python
def test_get_dashboard(client, dashboard):
    """Test dashboard GET endpoint"""
    response = client.get(f'/api/v1/dashboard/{dashboard.id}')
    assert response.status_code == 200
    assert response.json['result']['id'] == dashboard.id
```

---

## 6. Development Workflow Competencies

### 6.1 Contribution Process

**Required for: L1+**

| Step | Action | Documentation |
|------|--------|---------------|
| 1 | Fork repository | GitHub fork |
| 2 | Create feature branch | `git checkout -b feat/my-feature` |
| 3 | Make changes | Follow code standards |
| 4 | Write tests | Maintain coverage |
| 5 | Create PR | Use PR template |
| 6 | Address reviews | Respond to feedback |
| 7 | Merge | After approval |

### 6.2 Code Quality Standards

**Required for: L1+**

| Tool | Purpose | Config |
|------|---------|--------|
| ESLint | JS/TS linting | `.eslintrc.js` |
| Prettier | Code formatting | `.prettierrc` |
| Black | Python formatting | `pyproject.toml` |
| isort | Import sorting | `pyproject.toml` |
| pylint | Python linting | `.pylintrc` |

### 6.3 PR Requirements

**Required for: L1+**

| Requirement | Description |
|-------------|-------------|
| Tests | All tests passing |
| Coverage | No coverage decrease |
| Linting | No lint errors |
| Documentation | Updated if needed |
| Changelog | Entry if user-facing |
| Screenshots | For UI changes |

---

## 7. Specialized Competencies

### 7.1 Dashboard Embedding

**Required for: L3+**

| Approach | Implementation | Use Case |
|----------|----------------|----------|
| Guest Tokens | JWT-based access | Embedded SDK |
| Public Dashboards | UUID-based URLs | Anonymous access |
| Iframe Embedding | Direct embedding | Simple integration |

**Embedding SDK Usage:**

```typescript
import { embedDashboard } from "@superset-ui/embedded-sdk";

embedDashboard({
  id: "dashboard-uuid",
  supersetDomain: "https://superset.example.com",
  mountPoint: document.getElementById("dashboard"),
  fetchGuestToken: async () => {
    return await getGuestToken();
  },
});
```

### 7.2 Custom Visualization Development

**Required for: L3+**

| Step | Action | Files |
|------|--------|-------|
| 1 | Scaffold plugin | Yeoman generator |
| 2 | Implement chart | React component |
| 3 | Define controls | Control panel config |
| 4 | Add transformProps | Data transformation |
| 5 | Register plugin | `MainPreset.ts` |
| 6 | Write tests | Jest + RTL |
| 7 | Add Storybook | Visual testing |

### 7.3 Performance Optimization

**Required for: L3+**

| Technique | Application | Benefit |
|-----------|-------------|---------|
| React.memo | Chart components | Prevent re-renders |
| Lazy Loading | Charts below fold | Faster initial load |
| Virtualization | Large dashboards | Memory efficiency |
| Query Batching | Multiple charts | Fewer API calls |
| Cache Strategy | Query results | Faster refresh |

---

## 8. Competency Assessment Matrix

### L1 - Contributor Checklist

- [ ] Understand React/TypeScript fundamentals
- [ ] Know Redux basics (actions, reducers)
- [ ] Can write Jest/pytest unit tests
- [ ] Follow code style guidelines
- [ ] Create properly formatted PRs
- [ ] Respond to review feedback

### L2 - Active Contributor Checklist

- [ ] Deep Redux understanding (thunks, selectors)
- [ ] Understand dashboard component hierarchy
- [ ] Know Flask API patterns
- [ ] Can review others' PRs
- [ ] Understand filter system
- [ ] Write integration tests

### L3 - Committer Checklist

- [ ] Architectural decision making
- [ ] Performance optimization expertise
- [ ] Security & permissions deep knowledge
- [ ] Embedding implementation skills
- [ ] Custom visualization development
- [ ] Mentoring other contributors
- [ ] Release process knowledge

### L4 - PMC Member Checklist

- [ ] Project governance experience
- [ ] Release management capability
- [ ] Strategic direction input
- [ ] Community leadership
- [ ] Cross-project coordination
- [ ] Apache Way expertise

---

## 9. Learning Resources

### Official Documentation

- [Apache Superset Docs](https://superset.apache.org/docs/)
- [Contributing Guide](https://superset.apache.org/docs/contributing/)
- [Development How-tos](https://superset.apache.org/docs/contributing/howtos/)

### Source Code Reference

| Area | Location |
|------|----------|
| Dashboard Frontend | `superset-frontend/src/dashboard/` |
| Dashboard Backend | `superset/dashboards/` |
| Models | `superset/models/` |
| API Layer | `superset/views/` |
| Plugins | `superset-frontend/plugins/` |

### Community Resources

- [GitHub Discussions](https://github.com/apache/superset/discussions)
- [Apache Superset Slack](https://apache-superset.slack.com)
- [Preset Blog](https://preset.io/blog/) (tutorials)

---

## Document Metadata

| Field | Value |
|-------|-------|
| Catalog ID | `SUPERSET-DASH-COMP-001` |
| Version | 1.0.0 |
| Status | Active |
| Created | 2024-12-28 |
| Author | Claude Code |
| Source | Apache Superset 4.x |
