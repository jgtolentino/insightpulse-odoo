"""
FinServ Odoo MCP Server
Exposes Odoo ERP operations to Claude Desktop via MCP protocol.
"""

import os
import httpx
from typing import Any, Dict, List
from datetime import datetime

class FinServOdooMCP:
    """MCP server for Odoo ERP operations."""

    def __init__(self):
        self.odoo_url = os.getenv("ODOO_URL", "https://erp.insightpulseai.net")
        self.odoo_key = os.getenv("ODOO_API_KEY")
        self.http = httpx.AsyncClient(timeout=30)

    async def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools."""
        return [
            {
                "name": "odoo_get_sale_order",
                "description": "Get sale order details by number or ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "order_ref": {
                            "type": "string",
                            "description": "Sale order number (e.g., SO001) or ID"
                        }
                    },
                    "required": ["order_ref"]
                }
            },
            {
                "name": "odoo_list_expenses",
                "description": "List expense reports with optional filters",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "integer",
                            "description": "Filter by employee ID"
                        },
                        "state": {
                            "type": "string",
                            "enum": ["draft", "reported", "approved", "done", "refused"],
                            "description": "Filter by state"
                        },
                        "agency_code": {
                            "type": "string",
                            "enum": ["RIM", "CKVC", "BOM", "JPAL", "JLI", "JAP", "LAS", "RMQB"],
                            "description": "Filter by agency"
                        },
                        "limit": {
                            "type": "integer",
                            "default": 10,
                            "description": "Max results to return"
                        }
                    }
                }
            },
            {
                "name": "odoo_get_expense",
                "description": "Get expense details by ID or number",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "expense_ref": {
                            "type": "string",
                            "description": "Expense number (e.g., EXP-001) or ID"
                        }
                    },
                    "required": ["expense_ref"]
                }
            },
            {
                "name": "odoo_create_task",
                "description": "Create a new project task in Odoo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Task title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Task description (markdown supported)"
                        },
                        "project_id": {
                            "type": "integer",
                            "description": "Project ID (optional, defaults to default project)"
                        },
                        "assigned_to": {
                            "type": "integer",
                            "description": "User ID to assign to"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["0", "1", "2", "3"],
                            "default": "1",
                            "description": "Priority (0=Low, 1=Normal, 2=High, 3=Urgent)"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "odoo_get_invoices",
                "description": "List invoices with filters",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "partner_id": {
                            "type": "integer",
                            "description": "Filter by customer/vendor ID"
                        },
                        "state": {
                            "type": "string",
                            "enum": ["draft", "posted", "cancel"],
                            "description": "Filter by state"
                        },
                        "invoice_type": {
                            "type": "string",
                            "enum": ["out_invoice", "in_invoice", "out_refund", "in_refund"],
                            "description": "Invoice type (customer vs vendor)"
                        },
                        "overdue": {
                            "type": "boolean",
                            "description": "Show only overdue invoices"
                        },
                        "limit": {
                            "type": "integer",
                            "default": 20
                        }
                    }
                }
            },
            {
                "name": "odoo_get_partners",
                "description": "Search for customers/vendors",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Search by name (partial match)"
                        },
                        "is_company": {
                            "type": "boolean",
                            "description": "Filter companies only"
                        },
                        "customer_rank": {
                            "type": "boolean",
                            "description": "Filter customers only"
                        },
                        "supplier_rank": {
                            "type": "boolean",
                            "description": "Filter suppliers only"
                        },
                        "limit": {
                            "type": "integer",
                            "default": 10
                        }
                    }
                }
            }
        ]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool and return result."""

        headers = {"Authorization": f"Bearer {self.odoo_key}"}

        try:
            if name == "odoo_get_sale_order":
                order_ref = arguments["order_ref"]
                url = f"{self.odoo_url}/api/sale.order/{order_ref}"
                r = await self.http.get(url, headers=headers)
                r.raise_for_status()
                data = r.json()

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": self._format_sale_order(data)
                        }
                    ]
                }

            elif name == "odoo_list_expenses":
                params = {k: v for k, v in arguments.items() if v is not None}
                url = f"{self.odoo_url}/api/hr.expense"
                r = await self.http.get(url, headers=headers, params=params)
                r.raise_for_status()
                expenses = r.json().get("data", [])

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": self._format_expense_list(expenses)
                        }
                    ]
                }

            elif name == "odoo_get_expense":
                expense_ref = arguments["expense_ref"]
                url = f"{self.odoo_url}/api/hr.expense/{expense_ref}"
                r = await self.http.get(url, headers=headers)
                r.raise_for_status()
                data = r.json()

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": self._format_expense(data)
                        }
                    ]
                }

            elif name == "odoo_create_task":
                url = f"{self.odoo_url}/api/project.task"
                r = await self.http.post(url, headers=headers, json=arguments)
                r.raise_for_status()
                task = r.json()

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"✅ Task created: #{task['id']} - {task['name']}\nURL: {self.odoo_url}/web#id={task['id']}&model=project.task"
                        }
                    ]
                }

            elif name == "odoo_get_invoices":
                params = {k: v for k, v in arguments.items() if v is not None}
                url = f"{self.odoo_url}/api/account.move"
                r = await self.http.get(url, headers=headers, params=params)
                r.raise_for_status()
                invoices = r.json().get("data", [])

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": self._format_invoice_list(invoices)
                        }
                    ]
                }

            elif name == "odoo_get_partners":
                params = {k: v for k, v in arguments.items() if v is not None}
                url = f"{self.odoo_url}/api/res.partner"
                r = await self.http.get(url, headers=headers, params=params)
                r.raise_for_status()
                partners = r.json().get("data", [])

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": self._format_partner_list(partners)
                        }
                    ]
                }

            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Unknown tool: {name}"
                        }
                    ],
                    "isError": True
                }

        except httpx.HTTPStatusError as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Odoo API error: {e.response.status_code} - {e.response.text}"
                    }
                ],
                "isError": True
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                ],
                "isError": True
            }

    def _format_sale_order(self, data: Dict) -> str:
        """Format sale order for display."""
        return f"""**Sale Order: {data['name']}**

Customer: {data['partner_id'][1]}
Amount: ₱{data['amount_total']:,.2f}
Status: {data['state']}
Date: {data['date_order']}

Lines:
{self._format_order_lines(data.get('order_line', []))}

URL: {self.odoo_url}/web#id={data['id']}&model=sale.order
"""

    def _format_order_lines(self, lines: List[Dict]) -> str:
        """Format order lines."""
        if not lines:
            return "- (no lines)"
        result = []
        for line in lines[:10]:  # Max 10 lines
            result.append(f"- {line['name']}: ₱{line['price_subtotal']:,.2f} ({line['product_uom_qty']} x ₱{line['price_unit']:,.2f})")
        return "\n".join(result)

    def _format_expense_list(self, expenses: List[Dict]) -> str:
        """Format expense list."""
        if not expenses:
            return "No expenses found."

        result = ["**Expenses**\n"]
        for exp in expenses:
            result.append(f"- {exp['name']} (₱{exp['total_amount']:,.2f}) - {exp['state']} - {exp['employee_id'][1]}")
        return "\n".join(result)

    def _format_expense(self, data: Dict) -> str:
        """Format single expense."""
        return f"""**Expense: {data['name']}**

Employee: {data['employee_id'][1]}
Amount: ₱{data['total_amount']:,.2f}
Category: {data.get('product_id', ['', 'N/A'])[1]}
Status: {data['state']}
Date: {data['date']}
Description: {data.get('description', 'N/A')}

URL: {self.odoo_url}/web#id={data['id']}&model=hr.expense
"""

    def _format_invoice_list(self, invoices: List[Dict]) -> str:
        """Format invoice list."""
        if not invoices:
            return "No invoices found."

        result = ["**Invoices**\n"]
        for inv in invoices:
            result.append(f"- {inv['name']} - {inv['partner_id'][1]} - ₱{inv['amount_total']:,.2f} - {inv['state']}")
        return "\n".join(result)

    def _format_partner_list(self, partners: List[Dict]) -> str:
        """Format partner list."""
        if not partners:
            return "No partners found."

        result = ["**Partners**\n"]
        for p in partners:
            result.append(f"- [{p['id']}] {p['name']} - {p.get('email', 'N/A')}")
        return "\n".join(result)
