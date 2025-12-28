# LangChain Superset Tools

> Adapted from [Tableau LangChain](https://github.com/tableau/tableau_langchain) patterns

## Overview

This spec adapts Tableau's LangChain integration patterns for Superset:

| Tableau Pattern | Superset Equivalent |
|-----------------|---------------------|
| VizQL Data Service | Superset SQL Lab API |
| Connected Apps JWT | Superset API tokens |
| Simple Datasource QA | `superset_dataset_qa` |
| Datasource metadata | Superset dataset schema |

---

## Package Structure

```
langchain-superset/
├── pyproject.toml
├── langchain_superset/
│   ├── __init__.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── jwt.py                 # JWT token handling
│   │   └── api_token.py           # API key auth
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── simple_dataset_qa.py   # Natural language → SQL
│   │   ├── chart_query.py         # Query existing charts
│   │   ├── dashboard_ops.py       # Dashboard CRUD
│   │   └── hybrid_gitops.py       # GitOps operations
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── schema.py              # Dataset schema fetching
│   │   └── prompts.py             # Prompt templates
│   └── agents/
│       ├── __init__.py
│       ├── analyst.py             # Data analyst agent
│       └── dashboard_builder.py   # Dashboard creation agent
└── experimental/
    └── rag_dataset_qa.py          # RAG-enhanced querying
```

---

## Core Tool: Simple Dataset QA

### Input Model (Pydantic)

```python
# langchain_superset/tools/simple_dataset_qa.py
from pydantic import BaseModel, Field
from typing import Optional
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from anthropic import Anthropic
import httpx

class DatasetQAInputs(BaseModel):
    """Inputs for dataset QA tool."""
    user_input: str = Field(
        description="Natural language query like 'total revenue by region for Q4 2024'"
    )
    previous_call_error: Optional[str] = Field(
        default=None,
        description="Error from previous query attempt for retry logic"
    )
    previous_sql_query: Optional[str] = Field(
        default=None,
        description="Previous SQL that failed, to be corrected"
    )
```

### Factory Function Pattern

```python
def initialize_simple_dataset_qa(
    superset_url: str | None = None,
    api_token: str | None = None,
    dataset_id: int | None = None,
    model: str = "claude-3-5-sonnet-20241022",
    temperature: float = 0.0,
) -> callable:
    """
    Factory function to create a Superset dataset QA tool.

    Adapted from Tableau's initialize_simple_datasource_qa pattern.

    Args:
        superset_url: Superset instance URL (or SUPERSET_URL env var)
        api_token: API token (or SUPERSET_API_TOKEN env var)
        dataset_id: Dataset to query (or SUPERSET_DATASET_ID env var)
        model: LLM model for SQL generation
        temperature: LLM temperature (0 for deterministic)

    Returns:
        Decorated LangGraph tool function
    """
    import os

    # Read from env if not provided
    _url = superset_url or os.environ.get("SUPERSET_URL")
    _token = api_token or os.environ.get("SUPERSET_API_TOKEN")
    _dataset_id = dataset_id or int(os.environ.get("SUPERSET_DATASET_ID", "0"))

    if not all([_url, _token, _dataset_id]):
        raise ValueError("Missing required configuration")

    # Initialize LLM
    if "claude" in model.lower():
        client = Anthropic()
        llm_type = "anthropic"
    else:
        client = ChatOpenAI(model=model, temperature=temperature)
        llm_type = "openai"

    @tool(args_schema=DatasetQAInputs)
    async def superset_dataset_qa(
        user_input: str,
        previous_call_error: str | None = None,
        previous_sql_query: str | None = None,
    ) -> str:
        """
        Query a Superset dataset using natural language.

        Generates SQL from natural language input and executes against
        Superset's SQL Lab API.
        """
        # Step 1: Fetch dataset metadata
        schema = await fetch_dataset_schema(_url, _token, _dataset_id)

        # Step 2: Enhance with sample queries
        enhanced_context = enhance_with_samples(schema, user_input)

        # Step 3: Build prompt
        prompt = build_sql_generation_prompt(
            user_input=user_input,
            schema=enhanced_context,
            previous_error=previous_call_error,
            previous_sql=previous_sql_query,
        )

        # Step 4: Generate SQL
        if llm_type == "anthropic":
            response = client.messages.create(
                model=model,
                max_tokens=1024,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            sql_query = extract_sql(response.content[0].text)
        else:
            response = client.invoke(prompt)
            sql_query = extract_sql(response.content)

        # Step 5: Execute query
        try:
            result = await execute_superset_query(_url, _token, _dataset_id, sql_query)
            return format_response(result, schema)
        except SupersetQueryError as e:
            # Return error for retry
            return f"ERROR: {e.message}\nSQL: {sql_query}\nPlease retry with corrected query."

    return superset_dataset_qa
```

### Schema Fetching

```python
# langchain_superset/utils/schema.py
async def fetch_dataset_schema(
    superset_url: str,
    token: str,
    dataset_id: int
) -> dict:
    """Fetch dataset schema from Superset API."""
    async with httpx.AsyncClient() as client:
        # Get dataset metadata
        response = await client.get(
            f"{superset_url}/api/v1/dataset/{dataset_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        dataset = response.json()["result"]

        # Get columns with types
        columns = []
        for col in dataset.get("columns", []):
            columns.append({
                "name": col["column_name"],
                "type": col["type"],
                "filterable": col.get("filterable", True),
                "groupable": col.get("groupby", True),
                "is_temporal": col.get("is_dttm", False),
            })

        # Get metrics
        metrics = []
        for metric in dataset.get("metrics", []):
            metrics.append({
                "name": metric["metric_name"],
                "expression": metric["expression"],
                "description": metric.get("description", ""),
            })

        return {
            "table_name": dataset["table_name"],
            "schema": dataset.get("schema", "public"),
            "database": dataset["database"]["database_name"],
            "columns": columns,
            "metrics": metrics,
            "description": dataset.get("description", ""),
        }


def enhance_with_samples(schema: dict, user_input: str) -> str:
    """Enhance schema with relevant sample queries."""
    samples = [
        f"-- Get total of all metrics grouped by date\n"
        f"SELECT date_column, {', '.join(m['expression'] + ' AS ' + m['name'] for m in schema['metrics'][:3])}\n"
        f"FROM {schema['table_name']}\n"
        f"GROUP BY date_column",

        f"-- Filter by specific values\n"
        f"SELECT * FROM {schema['table_name']}\n"
        f"WHERE column_name = 'value'\n"
        f"LIMIT 100",
    ]

    return f"""
## Dataset Schema

**Table**: {schema['database']}.{schema['schema']}.{schema['table_name']}

**Description**: {schema['description']}

### Columns
{chr(10).join(f"- {c['name']} ({c['type']}) {'[temporal]' if c['is_temporal'] else ''}" for c in schema['columns'])}

### Pre-defined Metrics
{chr(10).join(f"- {m['name']}: {m['expression']}" for m in schema['metrics'])}

### Sample Queries
{chr(10).join(samples)}
"""
```

### Prompt Template

```python
# langchain_superset/utils/prompts.py
SQL_GENERATION_PROMPT = """You are a SQL expert for Apache Superset.

Generate a SQL query to answer the user's question based on the dataset schema.

{schema_context}

## User Question
{user_input}

{error_context}

## Instructions
1. Use only columns and metrics defined in the schema
2. Prefer pre-defined metrics over raw expressions
3. Include appropriate GROUP BY for aggregations
4. Add ORDER BY for sorted results
5. Use LIMIT for large result sets
6. For date filters, use appropriate date functions

## Output
Return ONLY the SQL query, no explanations.

```sql
"""

def build_sql_generation_prompt(
    user_input: str,
    schema: str,
    previous_error: str | None = None,
    previous_sql: str | None = None,
) -> str:
    """Build prompt for SQL generation."""
    error_context = ""
    if previous_error and previous_sql:
        error_context = f"""
## Previous Attempt (FAILED)
The following SQL query failed with an error:

```sql
{previous_sql}
```

Error: {previous_error}

Please generate a corrected query that avoids this error.
"""

    return SQL_GENERATION_PROMPT.format(
        schema_context=schema,
        user_input=user_input,
        error_context=error_context,
    )
```

### Query Execution

```python
# langchain_superset/tools/simple_dataset_qa.py (continued)
class SupersetQueryError(Exception):
    def __init__(self, message: str, sql: str):
        self.message = message
        self.sql = sql


async def execute_superset_query(
    superset_url: str,
    token: str,
    dataset_id: int,
    sql: str,
) -> dict:
    """Execute SQL query via Superset SQL Lab API."""
    async with httpx.AsyncClient() as client:
        # Get database ID from dataset
        dataset_resp = await client.get(
            f"{superset_url}/api/v1/dataset/{dataset_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        database_id = dataset_resp.json()["result"]["database"]["id"]

        # Execute query
        response = await client.post(
            f"{superset_url}/api/v1/sqllab/execute/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={
                "database_id": database_id,
                "sql": sql,
                "runAsync": False,
                "select_as_cta": False,
            },
            timeout=60.0,
        )

        result = response.json()

        if result.get("status") == "error":
            raise SupersetQueryError(
                message=result.get("error", "Unknown error"),
                sql=sql,
            )

        return {
            "columns": result.get("columns", []),
            "data": result.get("data", []),
            "query_id": result.get("query_id"),
        }


def format_response(result: dict, schema: dict) -> str:
    """Format query result for agent consumption."""
    import json

    if not result["data"]:
        return "No results found for the query."

    # Build response
    response = f"## Query Results\n\n"
    response += f"**Dataset**: {schema['table_name']}\n"
    response += f"**Rows returned**: {len(result['data'])}\n\n"

    # Format as table
    if len(result["data"]) <= 20:
        cols = [c["name"] for c in result["columns"]]
        response += "| " + " | ".join(cols) + " |\n"
        response += "| " + " | ".join(["---"] * len(cols)) + " |\n"
        for row in result["data"]:
            response += "| " + " | ".join(str(row.get(c, "")) for c in cols) + " |\n"
    else:
        response += f"```json\n{json.dumps(result['data'][:20], indent=2)}\n```\n"
        response += f"\n*Showing first 20 of {len(result['data'])} rows*"

    return response
```

---

## Additional Tools

### Chart Query Tool

```python
# langchain_superset/tools/chart_query.py
from pydantic import BaseModel, Field

class ChartQueryInputs(BaseModel):
    chart_id: int = Field(description="Superset chart ID to query")
    time_range: str = Field(default="Last 7 days", description="Time range filter")
    filters: list[dict] = Field(default_factory=list, description="Additional filters")


def initialize_chart_query(
    superset_url: str | None = None,
    api_token: str | None = None,
) -> callable:
    """Create a tool to query existing Superset charts."""
    import os

    _url = superset_url or os.environ.get("SUPERSET_URL")
    _token = api_token or os.environ.get("SUPERSET_API_TOKEN")

    @tool(args_schema=ChartQueryInputs)
    async def superset_chart_query(
        chart_id: int,
        time_range: str = "Last 7 days",
        filters: list[dict] = None,
    ) -> str:
        """Query data from an existing Superset chart."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{_url}/api/v1/chart/{chart_id}/data/",
                headers={
                    "Authorization": f"Bearer {_token}",
                    "Content-Type": "application/json",
                },
                json={
                    "queries": [{
                        "time_range": time_range,
                        "filters": filters or [],
                    }]
                },
            )

            result = response.json()
            if "error" in result:
                return f"Error: {result['error']}"

            data = result.get("result", [{}])[0].get("data", [])
            return format_chart_data(data)

    return superset_chart_query
```

### Dashboard Operations Tool

```python
# langchain_superset/tools/dashboard_ops.py
from pydantic import BaseModel, Field
from typing import Literal

class DashboardOpsInputs(BaseModel):
    operation: Literal["list", "get", "create", "export"] = Field(
        description="Operation to perform"
    )
    dashboard_id: int | None = Field(default=None, description="Dashboard ID for get/export")
    title: str | None = Field(default=None, description="Title for create")
    slug: str | None = Field(default=None, description="Slug for create")


def initialize_dashboard_ops(
    superset_url: str | None = None,
    api_token: str | None = None,
) -> callable:
    """Create a tool for dashboard operations."""
    import os

    _url = superset_url or os.environ.get("SUPERSET_URL")
    _token = api_token or os.environ.get("SUPERSET_API_TOKEN")

    @tool(args_schema=DashboardOpsInputs)
    async def superset_dashboard_ops(
        operation: str,
        dashboard_id: int | None = None,
        title: str | None = None,
        slug: str | None = None,
    ) -> str:
        """Perform dashboard operations in Superset."""
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {_token}"}

            if operation == "list":
                response = await client.get(
                    f"{_url}/api/v1/dashboard/",
                    headers=headers,
                )
                dashboards = response.json().get("result", [])
                return "\n".join(
                    f"- [{d['id']}] {d['dashboard_title']} ({d['slug']})"
                    for d in dashboards[:20]
                )

            elif operation == "get":
                response = await client.get(
                    f"{_url}/api/v1/dashboard/{dashboard_id}",
                    headers=headers,
                )
                return json.dumps(response.json().get("result", {}), indent=2)

            elif operation == "create":
                response = await client.post(
                    f"{_url}/api/v1/dashboard/",
                    headers={**headers, "Content-Type": "application/json"},
                    json={"dashboard_title": title, "slug": slug},
                )
                result = response.json()
                return f"Created dashboard: {result.get('id')}"

            elif operation == "export":
                response = await client.get(
                    f"{_url}/api/v1/dashboard/export/?q=[{dashboard_id}]",
                    headers=headers,
                )
                return f"Exported dashboard {dashboard_id}"

    return superset_dashboard_ops
```

### Hybrid GitOps Tool

```python
# langchain_superset/tools/hybrid_gitops.py
from pydantic import BaseModel, Field
from typing import Literal
import subprocess

class HybridGitOpsInputs(BaseModel):
    operation: Literal["compile", "validate", "plan", "apply", "drift", "promote"] = Field(
        description="GitOps operation to perform"
    )
    env: str = Field(default="dev", description="Target environment")
    force: bool = Field(default=False, description="Force apply without confirmation")


def initialize_hybrid_gitops(
    repo_path: str | None = None,
) -> callable:
    """Create a tool for hybrid control plane GitOps operations."""
    import os

    _repo = repo_path or os.environ.get("HYBRID_REPO_PATH", "/app/superset-assets")

    @tool(args_schema=HybridGitOpsInputs)
    def superset_hybrid_gitops(
        operation: str,
        env: str = "dev",
        force: bool = False,
    ) -> str:
        """Execute hybrid control plane GitOps operations."""
        commands = {
            "compile": f"hybrid compile --env {env}",
            "validate": f"hybrid validate --env {env}",
            "plan": f"hybrid plan --env {env}",
            "apply": f"hybrid apply --env {env}{' --force' if force else ''}",
            "drift": f"hybrid drift-plan --env {env}",
            "promote": f"hybrid promote --chain dev,staging,prod",
        }

        cmd = commands.get(operation)
        if not cmd:
            return f"Unknown operation: {operation}"

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=_repo,
        )

        if result.returncode != 0:
            return f"❌ {operation} failed:\n{result.stderr}"

        return f"✅ {operation} completed:\n{result.stdout}"

    return superset_hybrid_gitops
```

---

## Agent: Data Analyst

```python
# langchain_superset/agents/analyst.py
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic

def create_analyst_agent(
    superset_url: str,
    api_token: str,
    dataset_ids: list[int],
    model: str = "claude-3-5-sonnet-20241022",
):
    """Create a data analyst agent with Superset tools."""

    # Initialize LLM
    llm = ChatAnthropic(model=model, temperature=0)

    # Create tools
    tools = []
    for dataset_id in dataset_ids:
        tool = initialize_simple_dataset_qa(
            superset_url=superset_url,
            api_token=api_token,
            dataset_id=dataset_id,
            model=model,
        )
        tools.append(tool)

    tools.append(initialize_chart_query(superset_url, api_token))
    tools.append(initialize_dashboard_ops(superset_url, api_token))

    # System prompt
    system_message = SystemMessage(content="""You are a data analyst with access to Superset.

You can:
1. Query datasets using natural language (superset_dataset_qa)
2. Query existing charts (superset_chart_query)
3. List and manage dashboards (superset_dashboard_ops)

When answering questions:
- First check if an existing chart already answers the question
- If not, query the appropriate dataset
- Provide clear, actionable insights
- Include relevant numbers and trends

If a query fails, analyze the error and retry with corrected SQL.
""")

    # Create agent
    agent = create_react_agent(
        llm,
        tools,
        state_modifier=system_message,
    )

    return agent


# Usage
async def main():
    agent = create_analyst_agent(
        superset_url="https://superset.insightpulseai.net",
        api_token=os.environ["SUPERSET_API_TOKEN"],
        dataset_ids=[1, 2, 3],  # Sales, Invoices, Customers
    )

    result = await agent.ainvoke({
        "messages": [HumanMessage(content="What were total sales by region in Q4 2024?")]
    })

    print(result["messages"][-1].content)
```

---

## Installation & Usage

### Install

```bash
pip install langchain-superset
```

### Quick Start

```python
from langchain_superset import initialize_simple_dataset_qa

# Create tool
qa_tool = initialize_simple_dataset_qa(
    superset_url="https://superset.example.com",
    api_token="your-token",
    dataset_id=42,
)

# Use in LangGraph agent
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
agent = create_react_agent(llm, [qa_tool])

result = await agent.ainvoke({
    "messages": [{"role": "user", "content": "Show me revenue by product category"}]
})
```

### Environment Variables

```bash
# .env
SUPERSET_URL=https://superset.insightpulseai.net
SUPERSET_API_TOKEN=your-api-token
SUPERSET_DATASET_ID=42
ANTHROPIC_API_KEY=your-anthropic-key
```

---

## Key Patterns Stolen from Tableau

| Pattern | Tableau Implementation | Our Superset Adaptation |
|---------|----------------------|------------------------|
| Factory function | `initialize_simple_datasource_qa()` | `initialize_simple_dataset_qa()` |
| Pydantic inputs | `DataSourceQAInputs` | `DatasetQAInputs` |
| Retry logic | `previous_call_error` | `previous_call_error`, `previous_sql_query` |
| Metadata enhancement | VizQL schema + samples | Superset schema + sample queries |
| Prompt templating | VDS query template | SQL generation template |
| Temperature=0 | Deterministic SQL | Deterministic SQL |
| JWT auth | Connected Apps | API tokens |
| Monorepo structure | `pkg/` + `experimental/` | Same pattern |

---

## Resources

- [Tableau LangChain](https://github.com/tableau/tableau_langchain)
- [LangChain Tools](https://python.langchain.com/docs/modules/tools/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [Superset API](https://superset.apache.org/docs/api)
