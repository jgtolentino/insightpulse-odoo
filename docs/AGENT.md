# Odoo Development Agent Documentation

## Overview

The Odoo Development Agent is an expert-level AI assistant specialized in:
- Odoo ERP development (version 19.0)
- Data connector implementation (Odoo → BI tools)
- Apache Superset dashboard creation and customization
- Production deployment and DevOps best practices

This document provides setup instructions, usage guidelines, and extension patterns for leveraging the agent effectively.

---

## Table of Contents

1. [Agent Capabilities](#agent-capabilities)
2. [Setup & Configuration](#setup--configuration)
3. [Usage Patterns](#usage-patterns)
4. [Function Reference](#function-reference)
5. [Knowledge Base](#knowledge-base)
6. [Evaluation & Testing](#evaluation--testing)
7. [Extension Guide](#extension-guide)
8. [Troubleshooting](#troubleshooting)

---

## Agent Capabilities

### Core Competencies

#### 1. Odoo Module Development
- **Scaffolding**: Create properly structured Odoo modules
- **Model Design**: Define models with appropriate fields, constraints, and relationships
- **View Creation**: Generate XML views (form, tree, kanban, pivot, graph)
- **Security**: Configure access rights, record rules, and permissions
- **Business Logic**: Implement methods, computed fields, and workflows
- **Testing**: Write unit tests and integration tests

#### 2. Data Connector Implementation
The agent can design and implement robust data connectors using multiple patterns:

**Pattern Selection Matrix**:
| Use Case | Recommended Pattern | Advantages |
|----------|-------------------|------------|
| Real-time BI reporting | Direct DB (read-only user) | Fast, simple setup |
| Remote BI tool access | JSON-RPC API | Secure, respects Odoo security |
| Complex data transformations | Custom REST endpoints | Full control, can aggregate |
| Scheduled data exports | ETL jobs (cron) | Predictable load, cacheable |

#### 3. Superset BI Integration
- Database connection setup
- Dataset creation from Odoo views
- Dashboard design with best practices
- Row-level security (RLS) configuration
- Embedded analytics implementation
- Performance optimization

#### 4. DevOps & Deployment
- Docker containerization
- Multi-stage builds
- CI/CD pipeline setup (GitHub Actions)
- Production deployment guides
- Monitoring and logging setup
- Backup and recovery procedures

---

## Setup & Configuration

### Prerequisites

1. **Development Environment**:
   ```bash
   # Clone repository
   git clone https://github.com/jgtolentino/insightpulse-odoo.git
   cd insightpulse-odoo
   
   # Install Python dependencies
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt  # If exists
   ```

2. **Docker Environment**:
   ```bash
   # Ensure Docker and Docker Compose are installed
   docker --version  # Should be 24.0+
   docker compose version  # Should be 2.0+
   ```

3. **Access Credentials**:
   - Docker Hub account (for pulling images)
   - GitHub access (for repository)
   - Cloud provider credentials (optional, for deployment)

### Agent Configuration

The agent uses several configuration files and datasets:

```
insightpulse-odoo/
├── rules/
│   └── selection.yaml          # Module and pattern selection rules
├── schemas/
│   └── feature_request.yaml    # Feature request validation schema
├── datasets/
│   ├── odoo_sa.json           # Odoo solution architecture data
│   ├── oca_index.json         # OCA module index
│   └── market_caps.yaml       # Market capabilities matrix
├── scripts/
│   ├── appsrc.py              # Application source analysis
│   └── vendor_oca.py          # OCA module vendoring
└── docs/
    ├── KNOWLEDGE.md           # Agent knowledge base
    ├── SKILLS.md              # Skills inventory
    ├── DEPLOYMENT.md          # Production deployment guide
    └── AGENT.md               # This file
```

### Initialize Agent Environment

```bash
# Set environment variables
export ODOO_VERSION=19.0
export AGENT_MODE=development  # or 'production'

# Initialize datasets (if needed)
python scripts/appsrc.py --scan ./addons
python scripts/vendor_oca.py --update-index
```

---

## Usage Patterns

### Pattern 1: Create New Odoo Module

**Prompt**:
```
Create a new Odoo module called 'sales_commission' that calculates sales commissions 
for salespeople based on their total sales. Include:
- Model for commission rules (percentage, min/max thresholds)
- Computed field on sale.order for commission amount
- Report showing commissions by salesperson
- Security groups for commission managers
```

**Agent Actions**:
1. Analyzes requirement and validates against Odoo best practices
2. Checks if similar OCA modules exist (via `oca_index.json`)
3. Scaffolds module structure using `odoo_scaffold_module` function
4. Generates models, views, and security files
5. Creates sample data for testing
6. Writes unit tests
7. Provides installation and testing instructions

### Pattern 2: Implement Data Connector

**Prompt**:
```
Implement a data connector to export sales order data to Superset. 
Requirements:
- Read-only access
- Daily aggregation of sales metrics
- Support for multi-company filtering
- Materialized view for performance
```

**Agent Actions**:
1. Evaluates requirements using `odoo_choose_studio_vs_code` logic
2. Creates PostgreSQL read-only user
3. Designs star schema with fact/dimension tables
4. Implements SQL views for analytics
5. Sets up materialized views with refresh schedule
6. Configures indexes for query performance
7. Provides Superset connection instructions
8. Documents RLS setup for multi-company

### Pattern 3: Design Superset Dashboard

**Prompt**:
```
Design a Superset dashboard for sales executives showing:
- KPI cards: Revenue, Order Count, Avg Order Value
- Line chart: Revenue trend (last 90 days)
- Bar chart: Top 10 products
- Pivot table: Revenue by salesperson and region
- Ensure dashboard supports filtering by company and date range
```

**Agent Actions**:
1. Reviews `vw_sales_kpi_day` and related views in knowledge base
2. Creates Superset datasets from views
3. Designs charts following visualization best practices
4. Configures dashboard filters (company, date range)
5. Sets up cross-filtering between charts
6. Applies caching for performance
7. Configures RLS for data security
8. Provides dashboard export JSON and import instructions

### Pattern 4: Troubleshoot & Debug

**Prompt**:
```
Our Odoo instance is running slowly. Database queries are taking too long, 
especially for sales reports. Help diagnose and fix the issue.
```

**Agent Actions**:
1. Requests query logs and `pg_stat_statements` output
2. Analyzes slow queries
3. Identifies missing indexes
4. Proposes optimization strategies:
   - Add indexes on frequently filtered columns
   - Create materialized views for heavy aggregations
   - Optimize ORM queries (avoid n+1 queries)
5. Provides SQL commands to implement fixes
6. Suggests monitoring setup to prevent future issues

### Pattern 5: CI/CD Setup

**Prompt**:
```
Set up a CI/CD pipeline to automatically test and deploy Odoo modules 
when code is pushed to the main branch.
```

**Agent Actions**:
1. Creates GitHub Actions workflow (`.github/workflows/ci-cd.yml`)
2. Configures steps:
   - Linting (pylint, flake8)
   - Unit tests
   - Security scan (CodeQL)
   - Docker image build
   - Push to registry
   - Deploy to staging/production
3. Sets up secrets management
4. Configures deployment environments
5. Provides rollback procedures
6. Documents workflow triggers and manual approval gates

---

## Function Reference

### Core Functions

The agent has access to these specialized functions:

#### `odoo_rpc_call(url, db, username, password, model, method, args, kwargs)`
Execute XML-RPC calls to Odoo external API.

**Example**:
```python
# Fetch sales orders
orders = odoo_rpc_call(
    url='http://localhost:8069',
    db='odoo',
    username='admin',
    password='admin',
    model='sale.order',
    method='search_read',
    args=[
        [('state', 'in', ['sale', 'done'])],  # domain
        ['name', 'date_order', 'amount_total']  # fields
    ]
)
```

#### `supabase_sql(connection_string, query)`
Execute SQL queries against Supabase (PostgreSQL) database.

**Example**:
```python
# Get sales metrics
result = supabase_sql(
    connection_string='postgresql://user:pass@host:5432/db',
    query='''
        SELECT 
            date_trunc('month', date_order) as month,
            SUM(amount_total) as revenue
        FROM sale_order
        WHERE state IN ('sale', 'done')
        GROUP BY month
        ORDER BY month DESC
        LIMIT 12
    '''
)
```

#### `superset_api(base_url, endpoint, method='GET', data=None, auth_token=None)`
Interact with Superset REST API.

**Example**:
```python
# Get dashboard list
dashboards = superset_api(
    base_url='https://superset.example.com',
    endpoint='/api/v1/dashboard/',
    auth_token='Bearer <token>'
)

# Create dataset
dataset = superset_api(
    base_url='https://superset.example.com',
    endpoint='/api/v1/dataset/',
    method='POST',
    data={
        'database': 1,
        'table_name': 'vw_sales_kpi_day',
        'schema': 'public'
    },
    auth_token='Bearer <token>'
)
```

### Helper Functions

#### `odoo_scaffold_module(name, path='./addons')`
Create a new Odoo module with proper structure.

#### `odoo_find_reuse(requirement)`
Search OCA and official Odoo modules for reusable solutions.

#### `odoo_tests_generate(module_name)`
Generate unit tests for an Odoo module.

#### `odoo_choose_studio_vs_code(requirement)`
Analyze whether to use Odoo Studio or code-based development.

#### `odoo_ci_release(version, changelog)`
Prepare a release with CI/CD automation.

---

## Knowledge Base

The agent has extensive knowledge stored in:

### `docs/KNOWLEDGE.md`
- Odoo architecture and development patterns
- Data connector design principles
- Superset integration guide
- Security best practices
- Performance optimization techniques
- Troubleshooting common issues

### `docs/SKILLS.md`
- Comprehensive inventory of technical skills
- Python, SQL, Odoo framework proficiency
- BI tools expertise (Superset, Grafana, etc.)
- DevOps and deployment capabilities
- Testing and quality assurance methods

### `datasets/odoo_sa.json`
Odoo solution architecture reference data including:
- Module interdependencies
- Standard field definitions
- Common model patterns
- Security group hierarchies

**Example**:
```json
{
  "modules": {
    "sale": {
      "depends": ["base", "product", "account"],
      "key_models": ["sale.order", "sale.order.line"],
      "common_fields": {
        "sale.order": ["partner_id", "date_order", "amount_total", "state"]
      }
    }
  }
}
```

### `datasets/oca_index.json`
Index of OCA (Odoo Community Association) modules for reuse.

**Example**:
```json
{
  "repositories": [
    {
      "name": "server-tools",
      "url": "https://github.com/OCA/server-tools",
      "modules": [
        {
          "name": "base_jsonify",
          "summary": "JSON serialization for Odoo models",
          "use_case": "API development, data export"
        }
      ]
    }
  ]
}
```

### `datasets/market_caps.yaml`
Market capabilities and feature comparison matrix.

**Example**:
```yaml
capabilities:
  sales_analytics:
    odoo_native: true
    requires_modules: [sale, stock]
    superset_charts:
      - revenue_trend
      - product_performance
      - customer_segmentation
    estimated_complexity: medium
```

### `rules/selection.yaml`
Decision rules for module selection and pattern recommendations.

**Example**:
```yaml
rules:
  - condition: "requirement contains 'real-time reporting'"
    recommendation: "direct_database_view"
    rationale: "Minimal latency, no API overhead"
  
  - condition: "requirement contains 'external system integration'"
    recommendation: "json_rpc_api"
    rationale: "Secure, respects Odoo permissions"
  
  - condition: "requirement contains 'complex data transformation'"
    recommendation: "custom_rest_endpoint"
    rationale: "Full control over business logic"
```

### `schemas/feature_request.yaml`
Schema for validating and processing feature requests.

**Example**:
```yaml
feature_request_schema:
  type: object
  required: [title, description, functional_area]
  properties:
    title:
      type: string
      minLength: 10
      maxLength: 200
    description:
      type: string
      minLength: 50
    functional_area:
      type: string
      enum: [sales, purchasing, inventory, accounting, hr, project, crm]
    priority:
      type: string
      enum: [low, medium, high, critical]
    estimated_effort:
      type: string
      enum: [small, medium, large]
    dependencies:
      type: array
      items:
        type: string
```

---

## Evaluation & Testing

### Golden Prompts

The agent is evaluated against a set of 20 "golden prompts" covering:

1. **Model Development**: Create models with constraints
2. **View Generation**: Form, tree, kanban views
3. **Security**: Access rights, record rules
4. **Cron Jobs**: Scheduled actions
5. **Reports**: QWeb reports
6. **API Integration**: REST/JSON-RPC
7. **Data Migration**: Upgrade scripts
8. **Testing**: Unit and integration tests
9. **Performance**: Query optimization
10. **BI Connectors**: Database views, Superset integration

### CI Workflow for Evaluation

```yaml
# .github/workflows/agent-eval.yml
name: Agent Evaluation
on:
  pull_request:
    branches: [main]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Golden Prompts
        run: |
          python scripts/eval_agent.py \
            --prompts datasets/golden_prompts.json \
            --output results/eval_results.json
      
      - name: Check for Regressions
        run: |
          python scripts/check_regression.py \
            --baseline results/baseline.json \
            --current results/eval_results.json
      
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: eval-results
          path: results/
```

### Manual Testing Procedure

1. **Prompt the Agent**: Use one of the golden prompts
2. **Review Output**: Check for completeness, correctness, best practices
3. **Deploy & Test**: Actually install the module or run the code
4. **Validate Functionality**: Ensure it works as expected
5. **Performance Check**: Verify no performance regressions
6. **Security Audit**: Check for vulnerabilities
7. **Documentation**: Ensure proper documentation is included

---

## Extension Guide

### Adding New Data Sources

To add support for a new data source (e.g., MySQL, MongoDB):

1. **Create Connection Function**:
   ```python
   # scripts/connectors/mysql_connector.py
   def mysql_query(host, database, query, user, password):
       import mysql.connector
       conn = mysql.connector.connect(
           host=host,
           database=database,
           user=user,
           password=password
       )
       cursor = conn.cursor(dictionary=True)
       cursor.execute(query)
       results = cursor.fetchall()
       cursor.close()
       conn.close()
       return results
   ```

2. **Update Knowledge Base**:
   Add connection patterns to `docs/KNOWLEDGE.md`:
   ```markdown
   ### MySQL Integration
   - Use case: Legacy data migration
   - Connection: Direct SQL via mysql-connector-python
   - Security: Read-only user, SSL required
   ```

3. **Add to OCA Index** (if applicable):
   ```json
   {
     "name": "connector_mysql",
     "summary": "MySQL connector for Odoo",
     "repository": "custom"
   }
   ```

4. **Create Test Cases**:
   ```python
   def test_mysql_connector():
       result = mysql_query(
           host='localhost',
           database='test',
           query='SELECT 1 as test',
           user='test_user',
           password='test_pass'
       )
       assert result[0]['test'] == 1
   ```

### Adding New BI Tools

To add support for a new BI tool (e.g., Metabase, Tableau):

1. **Research Connection Methods**:
   - Direct database connection
   - REST API integration
   - ODBC/JDBC drivers

2. **Create Integration Guide**:
   ```markdown
   # docs/integrations/metabase.md
   
   ## Metabase Integration
   
   ### Connection Setup
   1. In Metabase, go to Admin > Databases
   2. Select PostgreSQL
   3. Enter Odoo database credentials (read-only user)
   4. Test connection
   
   ### Best Practices
   - Use views, not direct tables
   - Enable query caching
   - Set up row-level permissions
   ```

3. **Add Sample Queries**:
   ```sql
   -- Metabase-friendly view
   CREATE VIEW metabase_sales_overview AS
   SELECT 
       so.id::text as "Order ID",
       so.name::text as "Order Number",
       -- Metabase prefers text for IDs and categorical data
       ...
   ```

4. **Update Market Capabilities**:
   ```yaml
   # datasets/market_caps.yaml
   bi_tools:
     metabase:
       pros: [open_source, easy_setup, self_service]
       cons: [limited_advanced_features]
       best_for: [small_teams, quick_insights]
   ```

### Custom Agent Behaviors

To customize agent behavior for specific use cases:

1. **Create Custom Rules**:
   ```yaml
   # rules/custom_selection.yaml
   custom_rules:
     - name: "Healthcare Compliance"
       condition: "industry == 'healthcare'"
       additional_checks:
         - hipaa_compliance
         - audit_logging
         - data_encryption
   ```

2. **Extend Knowledge Base**:
   Add domain-specific knowledge to `docs/KNOWLEDGE.md`

3. **Add Validation Functions**:
   ```python
   # scripts/validators/hipaa_validator.py
   def validate_hipaa_compliance(module_path):
       # Check for required security measures
       pass
   ```

---

## Troubleshooting

### Common Issues

#### Agent Produces Incorrect Code

**Symptom**: Generated code has syntax errors or doesn't follow Odoo conventions.

**Solutions**:
1. Verify knowledge base is up to date
2. Check if prompt is clear and specific
3. Review golden prompts for similar patterns
4. Provide more context in the prompt (Odoo version, dependencies)

#### Agent Can't Find Reusable Modules

**Symptom**: Agent creates from scratch when OCA modules exist.

**Solutions**:
1. Update OCA index: `python scripts/vendor_oca.py --update-index`
2. Check `datasets/oca_index.json` for the module
3. Explicitly mention "check OCA first" in prompt

#### Performance Issues

**Symptom**: Agent takes too long to respond.

**Solutions**:
1. Break complex requests into smaller prompts
2. Use specific rather than open-ended questions
3. Reference specific knowledge base sections
4. Leverage cached responses when possible

#### Integration Failures

**Symptom**: Superset/API integrations fail.

**Solutions**:
1. Verify credentials and connection strings
2. Check network connectivity and firewalls
3. Review API version compatibility
4. Enable debug logging for detailed error messages

### Debug Mode

Enable detailed logging:

```bash
export AGENT_DEBUG=1
export AGENT_LOG_LEVEL=DEBUG

# Run agent with verbose output
python scripts/agent_cli.py --verbose --prompt "Create sales module"
```

### Getting Help

1. **Documentation**: Review `docs/KNOWLEDGE.md` and `docs/SKILLS.md`
2. **Examples**: Check `examples/` directory for working code
3. **Issues**: Open GitHub issue with:
   - Prompt used
   - Expected vs. actual output
   - Environment details (Odoo version, OS, etc.)
4. **Community**: Odoo forums, OCA mailing list

---

## Best Practices

### Effective Prompting

**Good Prompts**:
- Specific and detailed
- Include context (Odoo version, existing modules)
- Specify constraints (performance, security)
- Mention expected output format

**Example Good Prompt**:
```
In Odoo 19.0, create a module 'inventory_forecast' that:
- Adds a 'forecasted_qty' computed field to product.product
- Calculation: average sales from last 90 days * lead time in days
- Only for products with type='product' and tracking enabled
- Include unit tests for the calculation
- Follow OCA coding guidelines
```

**Bad Prompts**:
- "Make a sales module" (too vague)
- "Fix my Odoo" (no context)
- "Create everything" (too broad)

### Iterative Development

1. **Start Small**: Begin with core functionality
2. **Test Incrementally**: Verify each component works
3. **Refine**: Add features based on testing
4. **Document**: Keep documentation in sync with code

### Security First

Always consider:
- Input validation
- Access control
- SQL injection prevention
- Secure credential storage
- Audit logging

---

## Appendix

### Agent Metadata

```yaml
agent:
  name: "Odoo Development Agent"
  version: "1.0.0"
  odoo_version: "19.0"
  specializations:
    - odoo_module_development
    - data_connectors
    - superset_bi_integration
    - devops_deployment
  languages:
    - python: 3.11+
    - sql: postgresql_15+
    - javascript: es6+
  frameworks:
    - odoo: 19.0
    - superset: 3.0+
    - docker: 24.0+
```

### Useful Commands

```bash
# Initialize agent environment
./scripts/init_agent.sh

# Update knowledge base
python scripts/update_kb.py --source docs/ --output kb.json

# Run evaluation
python scripts/eval_agent.py --prompts datasets/golden_prompts.json

# Generate module documentation
python scripts/doc_generator.py --module my_module

# Vendor OCA module
python scripts/vendor_oca.py --module base_jsonify --target ./addons/

# Analyze application structure
python scripts/appsrc.py --scan ./addons --output datasets/app_structure.json
```

### Resources

- **Odoo Developer Documentation**: https://www.odoo.com/documentation/19.0/developer.html
- **OCA Guidelines**: https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst
- **Superset Documentation**: https://superset.apache.org/docs/intro
- **PostgreSQL Performance**: https://wiki.postgresql.org/wiki/Performance_Optimization

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-26  
**Maintained By**: InsightPulse Team  
**License**: MIT
