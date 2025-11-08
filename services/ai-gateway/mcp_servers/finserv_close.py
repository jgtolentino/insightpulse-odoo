"""
FinServ Month-End Close MCP Server
Exposes close operations, checklists, and status to Claude Desktop.
"""

import os
import httpx
from typing import Any, Dict, List
from datetime import datetime

class FinServCloseMCP:
    """MCP server for month-end close operations."""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL", "https://spdtwktxdalcfigzeqrz.supabase.co")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.n8n_url = os.getenv("N8N_URL", "https://n8n.insightpulseai.net")
        self.http = httpx.AsyncClient(timeout=30)

    async def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools."""
        return [
            {
                "name": "close_get_status",
                "description": "Get month-end close status for all entities or specific entity",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "entity_code": {
                            "type": "string",
                            "enum": ["RIM", "CKVC", "BOM", "JPAL", "JLI", "JAP", "LAS", "RMQB", "CONSOLIDATED"],
                            "description": "Entity code (optional, returns all if not specified)"
                        },
                        "period": {
                            "type": "string",
                            "description": "Period in YYYY-MM format (defaults to current month)"
                        }
                    }
                }
            },
            {
                "name": "close_get_checklist",
                "description": "Get detailed close checklist with task status",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "entity_code": {
                            "type": "string",
                            "enum": ["RIM", "CKVC", "BOM", "JPAL", "JLI", "JAP", "LAS", "RMQB"],
                            "description": "Entity code"
                        },
                        "period": {
                            "type": "string",
                            "description": "Period in YYYY-MM format"
                        }
                    },
                    "required": ["entity_code", "period"]
                }
            },
            {
                "name": "close_mark_task_complete",
                "description": "Mark a close task as complete",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "Close task ID"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Completion notes (optional)"
                        }
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "close_get_exceptions",
                "description": "Get open exceptions/blockers for close",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "entity_code": {
                            "type": "string",
                            "description": "Filter by entity"
                        },
                        "severity": {
                            "type": "string",
                            "enum": ["critical", "high", "medium", "low"],
                            "description": "Filter by severity"
                        }
                    }
                }
            },
            {
                "name": "close_get_metrics",
                "description": "Get close cycle metrics (cycle time, exceptions, aging)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "entity_code": {
                            "type": "string",
                            "description": "Filter by entity"
                        },
                        "last_n_periods": {
                            "type": "integer",
                            "default": 6,
                            "description": "Number of historical periods to include"
                        }
                    }
                }
            }
        ]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool and return result."""

        try:
            if name == "close_get_status":
                # Call n8n workflow for aggregated status
                url = f"{self.n8n_url}/webhook/close-status"
                params = {}
                if arguments.get("entity_code"):
                    params["entity"] = arguments["entity_code"]
                if arguments.get("period"):
                    params["period"] = arguments["period"]

                r = await self.http.get(url, params=params)
                r.raise_for_status()
                data = r.json()

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": self._format_close_status(data)
                        }
                    ]
                }

            elif name == "close_get_checklist":
                # Query Supabase for checklist
                entity = arguments["entity_code"]
                period = arguments["period"]

                headers = {
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}"
                }
                url = f"{self.supabase_url}/rest/v1/close_tasks"
                params = {
                    "entity_code": f"eq.{entity}",
                    "period": f"eq.{period}",
                    "select": "*",
                    "order": "sequence.asc"
                }

                r = await self.http.get(url, headers=headers, params=params)
                r.raise_for_status()
                tasks = r.json()

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": self._format_checklist(tasks, entity, period)
                        }
                    ]
                }

            elif name == "close_mark_task_complete":
                task_id = arguments["task_id"]
                notes = arguments.get("notes", "")

                headers = {
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation"
                }
                url = f"{self.supabase_url}/rest/v1/close_tasks"
                params = {"id": f"eq.{task_id}"}
                payload = {
                    "status": "completed",
                    "completed_at": datetime.utcnow().isoformat(),
                    "notes": notes
                }

                r = await self.http.patch(url, headers=headers, params=params, json=payload)
                r.raise_for_status()
                task = r.json()[0]

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"✅ Task #{task_id} marked complete: {task['title']}"
                        }
                    ]
                }

            elif name == "close_get_exceptions":
                headers = {
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}"
                }
                url = f"{self.supabase_url}/rest/v1/close_exceptions"
                params = {"status": "eq.open"}

                if arguments.get("entity_code"):
                    params["entity_code"] = f"eq.{arguments['entity_code']}"
                if arguments.get("severity"):
                    params["severity"] = f"eq.{arguments['severity']}"

                r = await self.http.get(url, headers=headers, params=params)
                r.raise_for_status()
                exceptions = r.json()

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": self._format_exceptions(exceptions)
                        }
                    ]
                }

            elif name == "close_get_metrics":
                url = f"{self.n8n_url}/webhook/close-metrics"
                params = {}
                if arguments.get("entity_code"):
                    params["entity"] = arguments["entity_code"]
                if arguments.get("last_n_periods"):
                    params["periods"] = arguments["last_n_periods"]

                r = await self.http.get(url, params=params)
                r.raise_for_status()
                metrics = r.json()

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": self._format_metrics(metrics)
                        }
                    ]
                }

            else:
                return {
                    "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
                    "isError": True
                }

        except httpx.HTTPStatusError as e:
            return {
                "content": [{"type": "text", "text": f"API error: {e.response.status_code} - {e.response.text}"}],
                "isError": True
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                "isError": True
            }

    def _format_close_status(self, data: Dict) -> str:
        """Format close status."""
        entities = data.get("entities", [])
        if not entities:
            return "No close data available."

        result = [f"**Month-End Close Status** - {data.get('period', 'Current')}\n"]

        for entity in entities:
            code = entity['code']
            total = entity['total_tasks']
            completed = entity['completed_tasks']
            pct = (completed / total * 100) if total > 0 else 0
            status_icon = "✅" if pct == 100 else "🔄" if pct > 50 else "⚠️"

            result.append(f"{status_icon} **{code}**: {completed}/{total} tasks ({pct:.0f}%)")

            if entity.get('exceptions', 0) > 0:
                result.append(f"   ⚠️ {entity['exceptions']} open exceptions")

        result.append(f"\n**Overall**: {data.get('total_completed', 0)}/{data.get('total_tasks', 0)} tasks")
        result.append(f"**Target Close Date**: {data.get('target_close_date', 'N/A')}")

        return "\n".join(result)

    def _format_checklist(self, tasks: List[Dict], entity: str, period: str) -> str:
        """Format checklist."""
        if not tasks:
            return f"No checklist found for {entity} {period}"

        result = [f"**Close Checklist: {entity} - {period}**\n"]

        for task in tasks:
            icon = "✅" if task['status'] == 'completed' else "⏳" if task['status'] == 'in_progress' else "☐"
            result.append(f"{icon} [{task['sequence']}] {task['title']}")
            if task.get('owner'):
                result.append(f"    Owner: {task['owner']}")
            if task.get('due_date'):
                result.append(f"    Due: {task['due_date']}")
            if task.get('notes'):
                result.append(f"    Notes: {task['notes']}")

        return "\n".join(result)

    def _format_exceptions(self, exceptions: List[Dict]) -> str:
        """Format exceptions."""
        if not exceptions:
            return "No open exceptions."

        result = ["**Close Exceptions**\n"]

        for exc in exceptions:
            severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(exc['severity'], "⚪")
            result.append(f"{severity_icon} **{exc['title']}** ({exc['entity_code']})")
            result.append(f"   {exc['description']}")
            if exc.get('suggested_action'):
                result.append(f"   → {exc['suggested_action']}")
            result.append("")

        return "\n".join(result)

    def _format_metrics(self, metrics: Dict) -> str:
        """Format metrics."""
        result = ["**Close Cycle Metrics**\n"]

        result.append(f"**Average Cycle Time**: {metrics.get('avg_cycle_days', 0):.1f} days")
        result.append(f"**Fastest Close**: {metrics.get('min_cycle_days', 0)} days ({metrics.get('fastest_period', 'N/A')})")
        result.append(f"**Slowest Close**: {metrics.get('max_cycle_days', 0)} days ({metrics.get('slowest_period', 'N/A')})")
        result.append(f"\n**Exception Trends**:")
        result.append(f"- Average exceptions: {metrics.get('avg_exceptions', 0):.1f}/period")
        result.append(f"- Critical exceptions: {metrics.get('critical_exceptions', 0)}")

        return "\n".join(result)
