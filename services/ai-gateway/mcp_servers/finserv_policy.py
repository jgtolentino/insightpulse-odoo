"""
FinServ Policy QA MCP Server
Semantic search over policy docs, SOPs, and compliance guides with citations.
"""

import os
import httpx
from typing import Any, Dict, List

class FinServPolicyMCP:
    """MCP server for policy/SOP question answering with RAG."""

    def __init__(self):
        self.vector_url = os.getenv("VECTOR_API_URL", "https://mcp.insightpulseai.net/vector")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.http = httpx.AsyncClient(timeout=45)

    async def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools."""
        return [
            {
                "name": "policy_qa",
                "description": "Ask a question about company policies, SOPs, or compliance requirements. Returns answer with citations.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "Your question about policies/procedures/compliance"
                        },
                        "category": {
                            "type": "string",
                            "enum": ["accounting", "finance", "hr", "procurement", "compliance", "bir", "all"],
                            "default": "all",
                            "description": "Category filter (optional)"
                        },
                        "top_k": {
                            "type": "integer",
                            "default": 6,
                            "description": "Number of relevant chunks to retrieve"
                        }
                    },
                    "required": ["question"]
                }
            },
            {
                "name": "policy_search",
                "description": "Search policy documents by keyword or phrase",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "category": {
                            "type": "string",
                            "enum": ["accounting", "finance", "hr", "procurement", "compliance", "bir", "all"],
                            "default": "all"
                        },
                        "limit": {
                            "type": "integer",
                            "default": 10,
                            "description": "Max results"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "policy_get_document",
                "description": "Get full policy document by ID or title",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "doc_id": {
                            "type": "string",
                            "description": "Document ID or slug"
                        }
                    },
                    "required": ["doc_id"]
                }
            },
            {
                "name": "policy_list_categories",
                "description": "List all available policy categories with document counts",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool and return result."""

        try:
            if name == "policy_qa":
                # Call vector DB with semantic search + LLM synthesis
                url = f"{self.vector_url}/qa"
                payload = {
                    "question": arguments["question"],
                    "category": arguments.get("category", "all"),
                    "top_k": arguments.get("top_k", 6)
                }

                r = await self.http.post(url, json=payload)
                r.raise_for_status()
                result = r.json()

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": self._format_qa_response(result)
                        }
                    ]
                }

            elif name == "policy_search":
                url = f"{self.vector_url}/search"
                payload = {
                    "query": arguments["query"],
                    "category": arguments.get("category", "all"),
                    "limit": arguments.get("limit", 10)
                }

                r = await self.http.post(url, json=payload)
                r.raise_for_status()
                results = r.json().get("results", [])

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": self._format_search_results(results)
                        }
                    ]
                }

            elif name == "policy_get_document":
                doc_id = arguments["doc_id"]
                url = f"{self.vector_url}/documents/{doc_id}"

                r = await self.http.get(url)
                r.raise_for_status()
                doc = r.json()

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": self._format_document(doc)
                        }
                    ]
                }

            elif name == "policy_list_categories":
                url = f"{self.vector_url}/categories"

                r = await self.http.get(url)
                r.raise_for_status()
                categories = r.json().get("categories", [])

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": self._format_categories(categories)
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
                "content": [{"type": "text", "text": f"Vector API error: {e.response.status_code} - {e.response.text}"}],
                "isError": True
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                "isError": True
            }

    def _format_qa_response(self, result: Dict) -> str:
        """Format QA response with citations."""
        answer = result.get("answer", "No answer generated.")
        citations = result.get("citations", [])
        confidence = result.get("confidence", 0)

        output = [f"**Answer** (confidence: {confidence:.0%})\n"]
        output.append(answer)
        output.append("\n\n**Sources**:")

        if citations:
            for i, cite in enumerate(citations, 1):
                output.append(f"{i}. **{cite['title']}** (§{cite.get('section', 'N/A')})")
                output.append(f"   {cite['url']}")
                if cite.get('excerpt'):
                    output.append(f"   > {cite['excerpt'][:150]}...")
        else:
            output.append("- No citations found")

        return "\n".join(output)

    def _format_search_results(self, results: List[Dict]) -> str:
        """Format search results."""
        if not results:
            return "No results found."

        output = ["**Search Results**\n"]

        for i, res in enumerate(results, 1):
            output.append(f"{i}. **{res['title']}** ({res['category']})")
            output.append(f"   {res['url']}")
            if res.get('snippet'):
                output.append(f"   > {res['snippet']}")
            output.append("")

        return "\n".join(output)

    def _format_document(self, doc: Dict) -> str:
        """Format full document."""
        output = [f"**{doc['title']}**\n"]
        output.append(f"Category: {doc['category']}")
        output.append(f"Version: {doc.get('version', 'N/A')}")
        output.append(f"Last Updated: {doc.get('updated_at', 'N/A')}")
        output.append(f"\n{doc['content']}")

        return "\n".join(output)

    def _format_categories(self, categories: List[Dict]) -> str:
        """Format category list."""
        output = ["**Policy Categories**\n"]

        for cat in categories:
            output.append(f"- **{cat['name']}**: {cat['doc_count']} documents")

        return "\n".join(output)
