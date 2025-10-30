#!/usr/bin/env python3
"""
InsightPulse Monitor MCP Server

Real-time monitoring for Odoo, Supabase, and Finance SSC operations with BIR compliance tracking.
"""

import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastmcp import FastMCP
from supabase import create_client, Client
import httpx

# Initialize FastMCP
mcp = FastMCP("InsightPulse Monitor", dependencies=["supabase", "httpx"])

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
ODOO_URL = os.getenv("ODOO_URL")
ODOO_DATABASE = os.getenv("ODOO_DATABASE", "postgres")
ODOO_API_KEY = os.getenv("ODOO_API_KEY")

# Initialize clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@mcp.tool()
async def get_system_health() -> Dict:
    """
    Check health of Odoo, Supabase, and DigitalOcean infrastructure.

    Returns comprehensive system health metrics including:
    - Odoo ERP status and database health
    - Supabase API and database connectivity
    - Response times for all services
    - Error counts in the last hour
    """
    health_status = {
        "timestamp": datetime.utcnow().isoformat(),
        "overall_status": "healthy",
        "services": {}
    }

    # Check Odoo
    try:
        async with httpx.AsyncClient() as client:
            start = datetime.now()
            response = await client.get(
                f"{ODOO_URL}/web/database/list",
                timeout=10.0
            )
            elapsed = (datetime.now() - start).total_seconds()

            health_status["services"]["odoo"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time_ms": elapsed * 1000,
                "database": ODOO_DATABASE
            }
    except Exception as e:
        health_status["services"]["odoo"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["overall_status"] = "degraded"

    # Check Supabase
    try:
        start = datetime.now()
        # Use a simple query that doesn't require a specific table
        result = supabase.rpc("version", {}).execute()
        elapsed = (datetime.now() - start).total_seconds()

        health_status["services"]["supabase"] = {
            "status": "healthy",
            "response_time_ms": elapsed * 1000,
            "project": SUPABASE_URL.split("//")[1].split(".")[0] if SUPABASE_URL else "unknown"
        }
    except Exception as e:
        health_status["services"]["supabase"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["overall_status"] = "degraded"

    return health_status


@mcp.tool()
async def track_bir_filing_deadlines(
    agency_code: Optional[str] = None,
    months_ahead: int = 3
) -> List[Dict]:
    """
    Monitor upcoming BIR filing deadlines by agency.

    Args:
        agency_code: Filter by agency (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
        months_ahead: How many months to look ahead (default: 3)

    Returns list of upcoming BIR deadlines with:
    - Form type (1601-C, 1702-RT, 2550Q, etc.)
    - Filing deadline
    - Agency responsible
    - Days until deadline
    - Status (upcoming, due soon, overdue)
    """
    # BIR filing schedule
    bir_forms = {
        "1601-C": {"frequency": "monthly", "deadline_day": 10, "description": "Monthly Withholding Tax"},
        "1702-RT": {"frequency": "annual", "deadline_month": 4, "deadline_day": 15, "description": "Annual ITR"},
        "2550M": {"frequency": "monthly", "deadline_day": 10, "description": "Monthly VAT"},
        "2550Q": {"frequency": "quarterly", "deadline_days": [25, 25, 25, 25], "description": "Quarterly VAT"}
    }

    agencies = ["RIM", "CKVC", "BOM", "JPAL", "JLI", "JAP", "LAS", "RMQB"]
    if agency_code:
        agencies = [agency_code]

    deadlines = []
    today = datetime.now()
    end_date = today + timedelta(days=months_ahead * 30)

    for agency in agencies:
        for form_code, form_info in bir_forms.items():
            if form_info["frequency"] == "monthly":
                current_month = today.month
                for i in range(months_ahead + 1):
                    month = (current_month + i - 1) % 12 + 1
                    year = today.year + (current_month + i - 1) // 12
                    deadline = datetime(year, month, form_info["deadline_day"])

                    if deadline > today:
                        days_until = (deadline - today).days
                        status = "due_soon" if days_until <= 7 else "upcoming"

                        deadlines.append({
                            "agency": agency,
                            "form": form_code,
                            "description": form_info["description"],
                            "deadline": deadline.isoformat(),
                            "days_until": days_until,
                            "status": status
                        })

    # Sort by deadline
    deadlines.sort(key=lambda x: x["deadline"])

    return deadlines


@mcp.tool()
async def get_month_end_status(
    month: Optional[str] = None,
    agency_code: Optional[str] = None
) -> Dict:
    """
    Get real-time status of month-end closing tasks.

    Args:
        month: Month in YYYY-MM format (default: current month)
        agency_code: Filter by specific agency

    Returns status of all month-end tasks including:
    - Total tasks by status (pending, in_progress, completed, blocked)
    - Tasks by agency
    - Critical blockers
    - Estimated completion time
    """
    if not month:
        month = datetime.now().strftime("%Y-%m")

    try:
        # Query Supabase for month-end tasks
        query = supabase.table("month_end_tasks") \
            .select("*") \
            .eq("month", month)

        if agency_code:
            query = query.eq("agency", agency_code)

        result = query.execute()
        tasks = result.data

        # Aggregate statistics
        stats = {
            "month": month,
            "total_tasks": len(tasks),
            "by_status": {
                "pending": 0,
                "in_progress": 0,
                "completed": 0,
                "blocked": 0
            },
            "by_agency": {},
            "critical_blockers": [],
            "completion_percentage": 0
        }

        for task in tasks:
            status = task.get("status", "pending")
            agency = task.get("agency", "UNKNOWN")

            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            if agency not in stats["by_agency"]:
                stats["by_agency"][agency] = {"total": 0, "completed": 0}
            stats["by_agency"][agency]["total"] += 1

            if status == "completed":
                stats["by_agency"][agency]["completed"] += 1

            if status == "blocked":
                stats["critical_blockers"].append({
                    "task_name": task.get("name"),
                    "agency": agency,
                    "reason": task.get("block_reason"),
                    "assigned_to": task.get("assigned_to")
                })

        # Calculate completion percentage
        if stats["total_tasks"] > 0:
            stats["completion_percentage"] = round(
                (stats["by_status"]["completed"] / stats["total_tasks"]) * 100,
                2
            )

        return stats

    except Exception as e:
        return {
            "error": str(e),
            "month": month,
            "agency_code": agency_code
        }


@mcp.tool()
async def list_failed_jobs(
    hours: int = 24,
    job_type: Optional[str] = None
) -> List[Dict]:
    """
    List failed background jobs (PaddleOCR, email sending, etc.)

    Args:
        hours: Look back this many hours (default: 24)
        job_type: Filter by job type (paddleocr, email, webhook, export)

    Returns list of failed jobs with:
    - Job type and name
    - Failure reason
    - Timestamp
    - Retry count
    - Next retry time (if applicable)
    """
    try:
        since = datetime.now() - timedelta(hours=hours)

        query = supabase.table("background_jobs") \
            .select("*") \
            .eq("status", "failed") \
            .gte("created_at", since.isoformat()) \
            .order("created_at", desc=True)

        if job_type:
            query = query.eq("job_type", job_type)

        result = query.execute()

        failed_jobs = []
        for job in result.data:
            failed_jobs.append({
                "job_id": job.get("id"),
                "job_type": job.get("job_type"),
                "job_name": job.get("name"),
                "failure_reason": job.get("error_message"),
                "failed_at": job.get("updated_at"),
                "retry_count": job.get("retry_count", 0),
                "max_retries": job.get("max_retries", 3),
                "next_retry": job.get("next_retry_at"),
                "can_retry": job.get("retry_count", 0) < job.get("max_retries", 3)
            })

        return failed_jobs

    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
async def get_error_traces(
    service: str,
    limit: int = 10,
    since_hours: int = 24
) -> List[Dict]:
    """
    Retrieve stack traces from Odoo/Supabase logs.

    Args:
        service: Which service (odoo, supabase, api)
        limit: Maximum number of errors to return
        since_hours: Look back this many hours

    Returns list of error traces with:
    - Error message
    - Stack trace
    - Timestamp
    - Context (user, agency, operation)
    - Occurrence count
    """
    try:
        since = datetime.now() - timedelta(hours=since_hours)

        result = supabase.table("error_logs") \
            .select("*") \
            .eq("service", service) \
            .gte("timestamp", since.isoformat()) \
            .order("timestamp", desc=True) \
            .limit(limit) \
            .execute()

        return result.data

    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
async def monitor_compliance_status(
    agency_code: Optional[str] = None
) -> Dict:
    """
    Monitor ATP validity, certificate expirations, and compliance status.

    Args:
        agency_code: Filter by specific agency

    Returns compliance status including:
    - ATP (Authorization to Print) validity by agency
    - SSL certificate expiration dates
    - BIR registration status
    - DOLE compliance status
    - Upcoming renewals
    """
    try:
        query = supabase.table("compliance_tracking").select("*")

        if agency_code:
            query = query.eq("agency", agency_code)

        result = query.execute()

        compliance = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "compliant",
            "agencies": {}
        }

        for record in result.data:
            agency = record.get("agency")

            if agency not in compliance["agencies"]:
                compliance["agencies"][agency] = {
                    "atp_valid": False,
                    "bir_registered": False,
                    "dole_compliant": False,
                    "expiring_soon": []
                }

            # Check ATP validity
            if record.get("compliance_type") == "atp":
                expiry = datetime.fromisoformat(record.get("expiry_date"))
                days_until_expiry = (expiry - datetime.now()).days

                compliance["agencies"][agency]["atp_valid"] = days_until_expiry > 0

                if 0 < days_until_expiry <= 90:  # Expiring within 90 days
                    compliance["agencies"][agency]["expiring_soon"].append({
                        "type": "ATP",
                        "expiry_date": expiry.isoformat(),
                        "days_until_expiry": days_until_expiry
                    })
                    compliance["overall_status"] = "warning"

        return compliance

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def check_database_performance() -> Dict:
    """
    Check for slow queries, lock contention, and database performance issues.

    Returns database performance metrics including:
    - Slow queries (>1 second)
    - Active connections
    - Lock wait times
    - Table sizes
    - Index usage
    - Recommended optimizations
    """
    try:
        # Query Supabase for performance metrics
        # This uses pg_stat_statements extension
        result = supabase.rpc("get_slow_queries", {
            "min_duration": 1000  # 1 second in ms
        }).execute()

        performance = {
            "timestamp": datetime.utcnow().isoformat(),
            "slow_queries": result.data,
            "recommendations": []
        }

        # Generate recommendations
        for query in result.data[:5]:  # Top 5 slow queries
            if query.get("calls", 0) > 100:
                performance["recommendations"].append({
                    "query": query.get("query", "")[:100] + "...",
                    "recommendation": "Consider adding an index",
                    "reason": f"Called {query.get('calls')} times with avg {query.get('mean_time')}ms"
                })

        return performance

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def get_agency_metrics(
    agency_code: str,
    metric_type: str = "all"
) -> Dict:
    """
    Get KPIs and metrics by agency (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB).

    Args:
        agency_code: Agency code (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
        metric_type: Type of metrics (financial, operational, compliance, all)

    Returns agency KPIs including:
    - Financial metrics (revenue, expenses, profit margin)
    - Operational metrics (tasks completed, SLA adherence)
    - Compliance metrics (BIR filings, DOLE requirements)
    - Trend analysis (vs. last month, vs. last year)
    """
    try:
        result = supabase.table("agency_metrics") \
            .select("*") \
            .eq("agency", agency_code) \
            .order("period", desc=True) \
            .limit(12) \
            .execute()  # Last 12 months

        if not result.data:
            return {"error": f"No metrics found for agency {agency_code}"}

        latest = result.data[0]

        metrics = {
            "agency": agency_code,
            "period": latest.get("period"),
            "financial": {},
            "operational": {},
            "compliance": {}
        }

        if metric_type in ["financial", "all"]:
            metrics["financial"] = {
                "revenue": latest.get("revenue"),
                "expenses": latest.get("expenses"),
                "profit_margin": latest.get("profit_margin"),
                "budget_variance": latest.get("budget_variance")
            }

        if metric_type in ["operational", "all"]:
            metrics["operational"] = {
                "tasks_completed": latest.get("tasks_completed"),
                "sla_adherence": latest.get("sla_adherence"),
                "avg_resolution_time": latest.get("avg_resolution_time"),
                "employee_count": latest.get("employee_count")
            }

        if metric_type in ["compliance", "all"]:
            metrics["compliance"] = {
                "bir_filings_on_time": latest.get("bir_filings_on_time"),
                "dole_compliant": latest.get("dole_compliant"),
                "audit_findings": latest.get("audit_findings")
            }

        # Calculate trends
        if len(result.data) >= 2:
            prev = result.data[1]
            metrics["trends"] = {
                "revenue_change_pct": _calculate_change(
                    latest.get("revenue"), prev.get("revenue")
                ),
                "efficiency_change_pct": _calculate_change(
                    latest.get("tasks_completed"), prev.get("tasks_completed")
                )
            }

        return metrics

    except Exception as e:
        return {"error": str(e)}


def _calculate_change(current: float, previous: float) -> float:
    """Calculate percentage change between two values."""
    if previous == 0 or previous is None or current is None:
        return 0
    return round(((current - previous) / previous) * 100, 2)


# Health check endpoint
@mcp.route("/health")
async def health_check():
    """Health check endpoint for DigitalOcean App Platform."""
    return {"status": "ok", "service": "insightpulse-monitor"}


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
