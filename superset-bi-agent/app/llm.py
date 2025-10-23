"""
LLM module for NL → SQL + Chart Spec generation
Uses OpenAI GPT-4o-mini for fast, cost-effective NL processing
"""
from typing import Tuple
import json
from openai import OpenAI
from .schemas import ChartSpec, Metric
from .config import settings

# Initialize OpenAI client
client = OpenAI(api_key=settings.openai_api_key)

# Odoo database schema hint
ODOO_SCHEMA_HINT = """
Odoo 19 database schema (PostgreSQL):

**Tables**:
- `hr_expense` - Employee expenses
  - id (integer), name (varchar), employee_id (integer), product_id (integer)
  - unit_amount (numeric), quantity (numeric), total_amount (numeric)
  - date (date), state (varchar), company_id (integer)
  - account_id (integer), analytic_account_id (integer)

- `account_move` - Accounting entries
  - id (integer), name (varchar), date (date), state (varchar)
  - partner_id (integer), amount_total (numeric), company_id (integer)
  - move_type (varchar), invoice_date (date)

- `account_move_line` - Accounting entry lines
  - id (integer), move_id (integer), account_id (integer)
  - debit (numeric), credit (numeric), balance (numeric)
  - date (date), partner_id (integer), product_id (integer)

- `product_product` - Products
  - id (integer), name (varchar), default_code (varchar)
  - list_price (numeric), standard_price (numeric)
  - categ_id (integer), active (boolean)

- `res_partner` - Partners (customers/suppliers)
  - id (integer), name (varchar), company_id (integer)
  - email (varchar), phone (varchar), city (varchar)
  - country_id (integer), is_company (boolean)

- `res_company` - Companies
  - id (integer), name (varchar), currency_id (integer)
  - country_id (integer), email (varchar)
"""

SYSTEM_PROMPT = f"""You are a Superset BI agent that converts natural language questions into SQL queries and chart specifications.

{ODOO_SCHEMA_HINT}

**Your Task**:
1. Analyze the natural language question
2. Generate a PostgreSQL SQL query to answer it
3. Determine the best chart type for visualization
4. Return JSON with SQL and chart spec

**Chart Types**:
- `bar_chart` - Categorical comparisons (e.g., "top 10 categories")
- `line_chart` - Trends over time (e.g., "monthly revenue")
- `pie` - Proportions/percentages (e.g., "expense breakdown")
- `table` - Detailed data listing
- `big_number_total` - Single KPI metric
- `area` - Cumulative trends
- `scatter` - Correlation analysis

**Response Format** (JSON):
{{
  "sql": "SELECT ... FROM ... WHERE ... GROUP BY ... ORDER BY ...",
  "viz_type": "bar_chart",
  "groupby": ["column_name"],
  "metrics": [
    {{"label": "Total Revenue", "expression": "SUM(amount)", "alias": "total_revenue"}}
  ],
  "temporal_column": "date" (optional, for time series),
  "time_range": "Last 12 months" (or "All time"),
  "adhoc_filters": [],
  "order_by": "total_revenue",
  "order_desc": true
}}

**Examples**:

Q: "Show top 10 expense categories by total amount"
A: {{
  "sql": "SELECT product_product.name AS category, SUM(hr_expense.total_amount) AS total FROM hr_expense JOIN product_product ON hr_expense.product_id = product_product.id WHERE hr_expense.state = 'done' GROUP BY product_product.name ORDER BY total DESC LIMIT 10",
  "viz_type": "bar_chart",
  "groupby": ["category"],
  "metrics": [{{"label": "Total Amount", "expression": "SUM(total_amount)", "alias": "total"}}],
  "time_range": "All time",
  "order_by": "total",
  "order_desc": true
}}

Q: "Monthly expense trends for the last year"
A: {{
  "sql": "SELECT DATE_TRUNC('month', date) AS month, SUM(total_amount) AS monthly_total FROM hr_expense WHERE date >= CURRENT_DATE - INTERVAL '12 months' AND state = 'done' GROUP BY DATE_TRUNC('month', date) ORDER BY month",
  "viz_type": "line_chart",
  "groupby": ["month"],
  "metrics": [{{"label": "Monthly Total", "expression": "SUM(total_amount)", "alias": "monthly_total"}}],
  "temporal_column": "month",
  "time_range": "Last 12 months",
  "order_by": "month",
  "order_desc": false
}}

Now analyze the user's question and respond with JSON only (no markdown, no explanation).
"""

def nl_to_sql_and_spec(nl: str) -> Tuple[str, ChartSpec]:
    """
    Convert natural language to SQL query and Superset chart specification.

    Args:
        nl: Natural language question

    Returns:
        Tuple of (SQL query, ChartSpec)
    """
    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": nl}
            ],
            temperature=0.2,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )

        result = response.choices[0].message.content
        data = json.loads(result)

        # Extract SQL
        sql = data["sql"]

        # Build ChartSpec
        metrics = [Metric(**m) for m in data["metrics"]]
        spec = ChartSpec(
            viz_type=data["viz_type"],
            groupby=data.get("groupby", []),
            metrics=metrics,
            temporal_column=data.get("temporal_column"),
            time_range=data.get("time_range", "All time"),
            adhoc_filters=data.get("adhoc_filters", []),
            order_by=data.get("order_by"),
            order_desc=data.get("order_desc", True)
        )

        return sql, spec

    except Exception as e:
        # Fallback to simple query
        sql = """
        SELECT
            product_product.name AS category,
            SUM(hr_expense.total_amount) AS total
        FROM hr_expense
        JOIN product_product ON hr_expense.product_id = product_product.id
        WHERE hr_expense.state = 'done'
        GROUP BY product_product.name
        ORDER BY total DESC
        LIMIT 10
        """
        spec = ChartSpec(
            viz_type="bar_chart",
            groupby=["category"],
            metrics=[Metric(
                label="Total Amount",
                expression="SUM(total_amount)",
                alias="total"
            )],
            time_range="All time",
            order_by="total",
            order_desc=True
        )
        return sql, spec
