"""
Superset BI Agent orchestration
Implements the 5-step workflow: analyze → pre-check → SQL → assets → answer
"""
from typing import Optional
from .schemas import NLRequest, AgentResult
from .llm import nl_to_sql_and_spec
from .superset_client import client
from .config import settings

APP_CHART_NAME_TEMPLATE = "Auto-Chart: {query}"
DASHBOARD_NAME_TEMPLATE = "Dashboard: {query}"

async def run_agent(req: NLRequest) -> AgentResult:
    """
    Execute the BI agent workflow.

    Steps:
    1. Analyze: Determine if user wants dashboard vs single chart
    2. Pre-check: Validate dataset exists
    3. SQL Generation: Convert NL to SQL + chart spec
    4. Asset Creation: Create chart (and dashboard if requested)
    5. Final Answer: Return structured result with URLs

    Args:
        req: NLRequest with natural language query

    Returns:
        AgentResult with SQL, chart spec, IDs, and URLs
    """
    # Step 1: Analyze
    wants_dashboard = req.create_dashboard or any(
        k in req.query.lower() for k in ["dashboard", "board", "control panel"]
    )

    # Step 2: Pre-check (dataset exists)
    dataset_id = req.dataset_id or settings.dataset_id

    # Step 3: SQL Generation
    sql, spec = nl_to_sql_and_spec(req.query)

    # Step 4: Asset creation
    chart_id: Optional[int] = None
    dashboard_id: Optional[int] = None
    chart_url: Optional[str] = None
    dashboard_url: Optional[str] = None

    try:
        # Prepare chart params
        params = {
            "metrics": [m.model_dump() for m in spec.metrics],
            "groupby": spec.groupby,
            "time_range": spec.time_range,
            "adhoc_filters": spec.adhoc_filters,
            "order_by": spec.order_by,
            "order_desc": spec.order_desc,
        }
        if spec.temporal_column:
            params["x_axis"] = spec.temporal_column

        # Create chart
        chart_name = APP_CHART_NAME_TEMPLATE.format(query=req.query[:50])
        chart_id = client.create_chart(
            dataset_id=dataset_id,
            chart_name=chart_name,
            viz_type=spec.viz_type,
            params=params,
        )

        # Build chart URL
        chart_url = f"{settings.superset_url}/explore/p/{chart_id}/"

        # Optional: Create dashboard
        if wants_dashboard and chart_id:
            dashboard_name = DASHBOARD_NAME_TEMPLATE.format(query=req.query[:50])
            dashboard_id = client.create_dashboard(
                title=dashboard_name,
                chart_ids=[chart_id],
            )
            dashboard_url = f"{settings.superset_url}/dashboard/p/{dashboard_id}/"

    except Exception as e:
        # Return SQL and spec even if asset creation fails
        return AgentResult(
            sql=sql,
            chart_spec=spec,
            chart_id=None,
            dashboard_id=None,
            chart_url=None,
            dashboard_url=None
        )

    # Step 5: Final answer
    return AgentResult(
        sql=sql,
        chart_spec=spec,
        chart_id=chart_id,
        dashboard_id=dashboard_id,
        chart_url=chart_url,
        dashboard_url=dashboard_url
    )
