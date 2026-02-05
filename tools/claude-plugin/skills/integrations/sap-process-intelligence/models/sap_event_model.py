"""
SAP Process Intelligence - Event Models
Pydantic models for SAP process event traces and analytics.

Auto-generates OpenAPI specs via spec-kit for agent tool discovery.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class SAPSystemType(str, Enum):
    """SAP system types"""
    ECC = "ECC"
    S4HANA = "S4HANA"
    S4HANA_CLOUD = "S4HANA_CLOUD"
    BUSINESS_ONE = "BUSINESS_ONE"


class ProcessType(str, Enum):
    """Standard SAP process types"""
    PROCURE_TO_PAY = "PROCURE_TO_PAY"
    ORDER_TO_CASH = "ORDER_TO_CASH"
    RECORD_TO_REPORT = "RECORD_TO_REPORT"
    HIRE_TO_RETIRE = "HIRE_TO_RETIRE"
    ISSUE_TO_RESOLUTION = "ISSUE_TO_RESOLUTION"
    CUSTOM = "CUSTOM"


class EventTrace(BaseModel):
    """
    Individual SAP event trace representing a single activity execution.
    Compatible with IEEE XES standard for process mining.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "event_id": "EVT_2025_001_00123",
                    "process_id": "PO_4500012345",
                    "case_id": "CASE_2025_001",
                    "activity": "Create Purchase Order",
                    "timestamp": "2025-01-15T10:30:00Z",
                    "user_id": "SAP_USER_001",
                    "system": "S4HANA",
                    "system_id": "PRD_100",
                    "metadata": {
                        "plant": "1000",
                        "company_code": "1010",
                        "vendor": "VENDOR_001",
                        "amount": 15000.00,
                        "currency": "USD"
                    }
                }
            ]
        }
    )

    event_id: str = Field(
        ...,
        description="Unique SAP event identifier",
        min_length=1,
        max_length=100
    )
    process_id: str = Field(
        ...,
        description="Process instance ID (e.g., PO number, SO number)",
        min_length=1,
        max_length=50
    )
    case_id: str = Field(
        ...,
        description="Case identifier for grouping related events",
        min_length=1,
        max_length=50
    )
    activity: str = Field(
        ...,
        description="Activity name (e.g., 'Create Purchase Order', 'Approve Invoice')",
        min_length=1,
        max_length=200
    )
    timestamp: datetime = Field(
        ...,
        description="UTC event timestamp in ISO 8601 format"
    )
    user_id: Optional[str] = Field(
        None,
        description="SAP user executing the step",
        max_length=50
    )
    system: SAPSystemType = Field(
        default=SAPSystemType.S4HANA,
        description="SAP system type"
    )
    system_id: str = Field(
        default="SAP_PROD",
        description="SAP system identifier",
        max_length=20
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context (plant, company code, amounts, etc.)"
    )
    duration_seconds: Optional[float] = Field(
        None,
        ge=0,
        description="Activity duration in seconds (if available)"
    )
    resource: Optional[str] = Field(
        None,
        description="Resource or organizational unit",
        max_length=100
    )
    lifecycle: Literal["start", "complete", "abort", "suspend", "resume"] = Field(
        default="complete",
        description="Event lifecycle state"
    )


class ProcessVariant(BaseModel):
    """
    Process variant representing a unique execution path through the process.
    """
    variant_id: str = Field(
        ...,
        description="Unique variant identifier"
    )
    activity_sequence: List[str] = Field(
        ...,
        description="Ordered sequence of activities in this variant"
    )
    frequency: int = Field(
        ...,
        ge=1,
        description="Number of cases following this variant"
    )
    frequency_percentage: float = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage of total cases"
    )
    avg_duration_seconds: float = Field(
        ...,
        ge=0,
        description="Average duration for this variant"
    )
    median_duration_seconds: float = Field(
        ...,
        ge=0,
        description="Median duration for this variant"
    )
    min_duration_seconds: float = Field(
        ...,
        ge=0,
        description="Minimum duration observed"
    )
    max_duration_seconds: float = Field(
        ...,
        ge=0,
        description="Maximum duration observed"
    )
    is_happy_path: bool = Field(
        default=False,
        description="Whether this is the expected/happy path"
    )


class ProcessDeviation(BaseModel):
    """
    Detected deviation from expected process behavior.
    """
    deviation_id: str = Field(..., description="Unique deviation identifier")
    case_id: str = Field(..., description="Case where deviation occurred")
    deviation_type: Literal[
        "missing_activity",
        "unexpected_activity",
        "sequence_violation",
        "timing_anomaly",
        "resource_violation"
    ] = Field(..., description="Type of deviation")
    severity: Literal["low", "medium", "high", "critical"] = Field(
        ...,
        description="Deviation severity"
    )
    description: str = Field(..., description="Human-readable deviation description")
    expected: Optional[str] = Field(None, description="Expected behavior")
    actual: str = Field(..., description="Actual observed behavior")
    timestamp: datetime = Field(..., description="When deviation was detected")
    impact_assessment: Optional[str] = Field(
        None,
        description="Business impact of this deviation"
    )


class VariantSummary(BaseModel):
    """
    Summary of process variant analysis.
    """
    total_cases: int = Field(..., ge=0, description="Total number of process cases")
    total_variants: int = Field(..., ge=0, description="Total number of unique variants")
    variants: List[ProcessVariant] = Field(
        ...,
        description="List of process variants sorted by frequency"
    )
    deviations: List[ProcessDeviation] = Field(
        default_factory=list,
        description="Detected process deviations"
    )
    conformance_rate: float = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage of cases conforming to expected behavior"
    )
    avg_case_duration_seconds: float = Field(
        ...,
        ge=0,
        description="Average case duration"
    )
    process_type: ProcessType = Field(
        default=ProcessType.CUSTOM,
        description="Type of business process"
    )


class Bottleneck(BaseModel):
    """
    Identified process bottleneck.
    """
    activity: str = Field(..., description="Activity name where bottleneck occurs")
    avg_wait_time_seconds: float = Field(
        ...,
        ge=0,
        description="Average wait time before this activity"
    )
    p90_wait_time_seconds: float = Field(
        ...,
        ge=0,
        description="90th percentile wait time"
    )
    frequency: int = Field(
        ...,
        ge=1,
        description="Number of times this bottleneck was observed"
    )
    impact_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Bottleneck impact score (0-100)"
    )
    root_cause_hypothesis: Optional[str] = Field(
        None,
        description="Hypothesized root cause"
    )


class ResourceUtilization(BaseModel):
    """
    Resource utilization metrics.
    """
    resource_id: str = Field(..., description="Resource identifier (user, department)")
    total_activities: int = Field(..., ge=0, description="Total activities performed")
    avg_activity_duration_seconds: float = Field(
        ...,
        ge=0,
        description="Average activity duration"
    )
    utilization_percentage: float = Field(
        ...,
        ge=0,
        le=100,
        description="Resource utilization percentage"
    )
    workload_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Distribution of activities by type"
    )


class KPIForecast(BaseModel):
    """
    KPI prediction with confidence intervals.
    """
    kpi_type: Literal["throughput", "delay", "anomaly_risk", "cost"] = Field(
        ...,
        description="Type of KPI being predicted"
    )
    predicted_value: float = Field(..., description="Predicted KPI value")
    confidence_lower: float = Field(..., description="Lower bound of 95% CI")
    confidence_upper: float = Field(..., description="Upper bound of 95% CI")
    prediction_timestamp: datetime = Field(
        ...,
        description="When prediction was made"
    )
    model_version: str = Field(..., description="ML model version used")
    risk_factors: List[str] = Field(
        default_factory=list,
        description="Identified risk factors"
    )
    confidence_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Prediction confidence score (0-100)"
    )


class ProcessMapStatistics(BaseModel):
    """
    Statistics for generated process map.
    """
    total_activities: int = Field(..., ge=0)
    total_transitions: int = Field(..., ge=0)
    start_activities: List[str] = Field(default_factory=list)
    end_activities: List[str] = Field(default_factory=list)
    avg_path_length: float = Field(..., ge=0)
    max_parallel_activities: int = Field(..., ge=0)
    transition_frequencies: Dict[str, int] = Field(default_factory=dict)


# Request/Response Models for API endpoints

class ExtractEventsRequest(BaseModel):
    """Request to extract process events from SAP"""
    process_id: str = Field(..., min_length=1)
    date_range: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}/\d{4}-\d{2}-\d{2}$",
        description="ISO 8601 date range (YYYY-MM-DD/YYYY-MM-DD)"
    )
    system_id: str = Field(default="SAP_PROD")
    process_type: Optional[ProcessType] = None


class ExtractEventsResponse(BaseModel):
    """Response containing extracted events"""
    events: List[EventTrace]
    total_events: int
    extraction_timestamp: datetime
    system_id: str


class CorrelateVariantsRequest(BaseModel):
    """Request to correlate process variants"""
    events: List[EventTrace]
    reference_model: Optional[str] = None


class CorrelateVariantsResponse(BaseModel):
    """Response containing variant analysis"""
    variant_summary: VariantSummary
    deviations: List[ProcessDeviation]


class PredictKPIRequest(BaseModel):
    """Request to predict KPI"""
    variant_summary: VariantSummary
    kpi_type: Literal["throughput", "delay", "anomaly_risk", "cost"]


class PredictKPIResponse(BaseModel):
    """Response containing KPI prediction"""
    kpi_forecast: KPIForecast
    recommendations: List[str]


class AnalyzeBottlenecksRequest(BaseModel):
    """Request to analyze bottlenecks"""
    events: List[EventTrace]
    threshold_percentile: float = Field(default=90, ge=0, le=100)


class AnalyzeBottlenecksResponse(BaseModel):
    """Response containing bottleneck analysis"""
    bottlenecks: List[Bottleneck]
    resource_utilization: List[ResourceUtilization]


class GenerateProcessMapRequest(BaseModel):
    """Request to generate process map"""
    events: List[EventTrace]
    output_format: Literal["mermaid", "bpmn", "drawio", "json"] = "mermaid"


class GenerateProcessMapResponse(BaseModel):
    """Response containing process map"""
    process_map: str
    statistics: ProcessMapStatistics
    format: str
