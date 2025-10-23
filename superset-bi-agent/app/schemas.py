from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

class Metric(BaseModel):
    """Superset metric definition"""
    label: str
    expression: str
    alias: str

class ChartSpec(BaseModel):
    """Superset chart specification"""
    viz_type: Literal[
        "bar_chart", "line_chart", "table", "big_number_total",
        "pie", "area", "scatter", "box_plot", "histogram"
    ]
    groupby: List[str] = Field(default_factory=list)
    metrics: List[Metric]
    temporal_column: Optional[str] = None
    time_range: str = "All time"
    adhoc_filters: List[Dict[str, Any]] = Field(default_factory=list)
    order_by: Optional[str] = None
    order_desc: bool = True

class NLRequest(BaseModel):
    """Natural language query request"""
    query: str = Field(..., description="Natural language question")
    dataset_id: Optional[int] = Field(None, description="Target Superset dataset ID")
    create_dashboard: bool = Field(False, description="Create dashboard instead of single chart")

class AgentResult(BaseModel):
    """Agent execution result"""
    sql: str = Field(..., description="Generated SQL query")
    chart_spec: ChartSpec = Field(..., description="Superset chart specification")
    chart_id: Optional[int] = Field(None, description="Created chart ID")
    dashboard_id: Optional[int] = Field(None, description="Created dashboard ID (if requested)")
    chart_url: Optional[str] = Field(None, description="Chart URL for embedding")
    dashboard_url: Optional[str] = Field(None, description="Dashboard URL for embedding")

class DatasetCreateRequest(BaseModel):
    """Request to create Superset dataset"""
    database_id: int
    schema: str = "public"
    table_name: str

class DashboardCreateRequest(BaseModel):
    """Request to create Superset dashboard"""
    title: str
    chart_ids: List[int]
    css: Optional[str] = None
