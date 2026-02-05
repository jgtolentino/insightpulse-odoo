"""
Odoo Developer Agent - MCP Server
Production-ready AI agent replacing senior Odoo developer
"""

import asyncio
import os
from typing import Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import structlog

from tools.module_generator import OdooModuleGenerator
from tools.code_analyzer import OdooCodeAnalyzer
from knowledge.rag_client import OdooKnowledgeBase

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

# Initialize MCP server
app = Server("odoo-developer-agent")

# Initialize tools
module_generator = OdooModuleGenerator()
code_analyzer = OdooCodeAnalyzer()
knowledge_base = OdooKnowledgeBase()


@app.list_tools()
async def list_tools() -> List[Tool]:
    """
    List all available tools for the Odoo Developer Agent
    """
    return [
        Tool(
            name="generate_odoo_module",
            description="""
            Generate a complete, production-ready Odoo 18 CE module with:
            - Models (Python classes with fields, methods, constraints)
            - Views (XML: form, tree, search, kanban)
            - Security (ir.model.access.csv, record rules)
            - Tests (pytest test suite with OCA quality checks)
            - Documentation (README.rst in OCA format)
            - i18n support (translation directories)
            
            The module follows OCA standards and includes all necessary files
            for immediate deployment to Odoo.
            
            Best for: Creating custom Odoo modules from requirements
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "module_name": {
                        "type": "string",
                        "description": "Technical module name (e.g., 'insightpulse_bir_compliance')",
                    },
                    "description": {
                        "type": "string",
                        "description": "User-facing description of module functionality",
                    },
                    "models": {
                        "type": "array",
                        "description": "List of Odoo models to create",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "fields": {"type": "array"},
                                "methods": {"type": "array"},
                            }
                        }
                    },
                    "views": {
                        "type": "array",
                        "description": "List of views to create",
                        "items": {
                            "type": "object",
                            "properties": {
                                "model": {"type": "string"},
                                "type": {"type": "string", "enum": ["form", "tree", "search", "kanban"]},
                                "fields": {"type": "array"},
                            }
                        }
                    },
                    "dependencies": {
                        "type": "array",
                        "description": "List of dependent modules (default: ['base'])",
                        "items": {"type": "string"},
                        "default": ["base"]
                    },
                    "category": {
                        "type": "string",
                        "description": "Odoo app category",
                        "default": "Accounting"
                    }
                },
                "required": ["module_name", "description", "models"]
            }
        ),
        Tool(
            name="debug_odoo_error",
            description="""
            Analyze Odoo errors and automatically fix them when confidence is high.
            
            Features:
            - Parse error tracebacks
            - Find similar past errors and solutions
            - Generate specific code fixes
            - Auto-apply fixes if confidence > 90%
            - Store solutions for future reference
            
            Best for: Debugging runtime errors, exceptions, and unexpected behavior
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "error_log": {
                        "type": "string",
                        "description": "Full error traceback from Odoo logs"
                    },
                    "module_name": {
                        "type": "string",
                        "description": "Module where error occurred"
                    },
                    "tenant_id": {
                        "type": "string",
                        "description": "Tenant ID for context (optional)"
                    },
                    "auto_fix": {
                        "type": "boolean",
                        "description": "Auto-apply fix if safe (default: true)",
                        "default": True
                    }
                },
                "required": ["error_log", "module_name"]
            }
        ),
        Tool(
            name="optimize_odoo_code",
            description="""
            Optimize Odoo code for performance, readability, or maintainability.
            
            Optimizations include:
            - Eliminate N+1 query problems
            - Proper @api.depends usage
            - Batch operations instead of loops
            - Memory-efficient data structures
            - SQL query optimization
            - Code readability improvements
            
            Best for: Improving module performance and code quality
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to Python file to optimize"
                    },
                    "optimization_goals": {
                        "type": "array",
                        "description": "Optimization priorities",
                        "items": {
                            "type": "string",
                            "enum": ["performance", "readability", "memory", "sql"]
                        },
                        "default": ["performance", "readability"]
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="review_code_changes",
            description="""
            Review Odoo code changes for quality, security, and OCA compliance.
            
            Checks:
            - OCA coding standards
            - Security vulnerabilities (SQL injection, XSS)
            - Performance issues
            - Missing translations
            - Incomplete tests
            - Breaking changes
            
            Best for: PR reviews and code quality assurance
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "changed_files": {
                        "type": "array",
                        "description": "List of changed file paths",
                        "items": {"type": "string"}
                    },
                    "diff_content": {
                        "type": "string",
                        "description": "Git diff content"
                    }
                },
                "required": ["changed_files", "diff_content"]
            }
        ),
        Tool(
            name="search_odoo_knowledge",
            description="""
            Search Odoo documentation and past solutions.
            
            Sources:
            - Odoo 18 CE core documentation
            - OCA module documentation
            - Past error solutions
            - Custom module examples
            
            Best for: Finding examples, documentation, and past solutions
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query"
                    },
                    "doc_types": {
                        "type": "array",
                        "description": "Filter by document types",
                        "items": {
                            "type": "string",
                            "enum": ["core", "oca", "custom", "errors"]
                        }
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="explain_odoo_code",
            description="""
            Explain how Odoo code works with detailed analysis.
            
            Provides:
            - Line-by-line explanation
            - Odoo API usage explanation
            - Database interaction flow
            - Performance implications
            - Potential issues
            
            Best for: Understanding existing code and onboarding
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Odoo code to explain"
                    },
                    "module_context": {
                        "type": "string",
                        "description": "Module name for additional context (optional)"
                    }
                },
                "required": ["code"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """
    Execute tool based on name
    """
    logger.info("tool_called", tool=name, args=arguments)
    
    try:
        if name == "generate_odoo_module":
            result = await module_generator.generate_module(
                module_name=arguments["module_name"],
                description=arguments["description"],
                models=arguments["models"],
                views=arguments.get("views", []),
                dependencies=arguments.get("dependencies", ["base"]),
                category=arguments.get("category", "Accounting")
            )
            
            return [TextContent(
                type="text",
                text=f"""✅ Module Generated Successfully

**Module:** {result['module_path']}

**Files Created:** {len(result['files_created'])} files
{chr(10).join('- ' + f for f in result['files_created'])}

**Quality Score:** {result['quality_score']:.1%}

**Next Steps:**
{chr(10).join('- ' + step for step in result['next_steps'])}
"""
            )]
        
        elif name == "debug_odoo_error":
            result = await code_analyzer.analyze_error(
                error_log=arguments["error_log"],
                module_name=arguments["module_name"],
                tenant_id=arguments.get("tenant_id"),
                auto_fix=arguments.get("auto_fix", True)
            )
            
            status_emoji = "✅" if result['auto_fix_applied'] else "⚠️"
            
            response = f"""{status_emoji} Error Analysis Complete

**Error Type:** {result['error_type']}

**Root Cause:**
{result['root_cause']}

**Affected Components:**
{chr(10).join('- ' + c for c in result['affected_components'])}

**Fix Steps:**
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(result['fix_steps']))}

**Confidence:** {result['confidence']:.0%}
**Risk Level:** {result['risk_level']}

"""
            
            if result['auto_fix_applied']:
                response += f"""**Auto-Fix Applied:** Yes
**Success Rate:** {result['fix_result']['success_rate']:.0%}
**Files Modified:** {len(result['fix_result']['applied'])}
"""
            else:
                response += f"""**Auto-Fix Applied:** No
**Reason:** {result.get('reason', 'N/A')}
**Manual Review Required**
"""
            
            response += f"""
**Prevention Tips:**
{chr(10).join('- ' + tip for tip in result['prevention_tips'])}
"""
            
            return [TextContent(type="text", text=response)]
        
        elif name == "optimize_odoo_code":
            result = await code_analyzer.optimize_code(
                file_path=arguments["file_path"],
                optimization_goals=arguments.get("optimization_goals")
            )
            
            return [TextContent(
                type="text",
                text=f"""✅ Code Optimization Complete

**File:** {result['original_file']}

**Improvements:**
{chr(10).join(f"- [{imp['type'].upper()}] {imp['description']} (Impact: {imp['impact']})" for imp in result['improvements'])}

**Estimated Speedup:** {result['estimated_speedup']}

**Trade-offs:**
{chr(10).join('- ' + t for t in result['tradeoffs']) if result['tradeoffs'] else 'None'}

**Optimized Code:**
```python
{result['optimized_code']}
```
"""
            )]
        
        elif name == "review_code_changes":
            result = await code_analyzer.review_pull_request(
                changed_files=arguments["changed_files"],
                diff_content=arguments["diff_content"]
            )
            
            status_emoji = {
                "approved": "✅",
                "needs_changes": "⚠️",
                "rejected": "❌"
            }.get(result['approval_status'], "⚠️")
            
            response = f"""{status_emoji} Code Review Complete

**Status:** {result['approval_status'].upper()}

**Summary:**
{result['summary']}

**Checklist:**
{'✅' if result['checklist']['oca_compliant'] else '❌'} OCA Compliant
{'✅' if result['checklist']['security_safe'] else '❌'} Security Safe
{'✅' if result['checklist']['performance_ok'] else '❌'} Performance OK
{'✅' if result['checklist']['tests_included'] else '❌'} Tests Included

**Comments:** {len(result['comments'])}
"""
            
            for i, comment in enumerate(result['comments'], 1):
                severity_emoji = {
                    "critical": "🔴",
                    "warning": "🟡",
                    "suggestion": "🔵"
                }.get(comment['severity'], "⚪")
                
                response += f"""
{severity_emoji} **Comment {i}** [{comment['severity'].upper()}]
File: {comment['file']} (Line {comment['line']})
{comment['message']}
"""
                if comment.get('suggestion'):
                    response += f"Suggestion: {comment['suggestion']}\n"
            
            return [TextContent(type="text", text=response)]
        
        elif name == "search_odoo_knowledge":
            results = await knowledge_base.search_odoo_docs(
                query=arguments["query"],
                doc_types=arguments.get("doc_types"),
                top_k=arguments.get("top_k", 5)
            )
            
            response = f"📚 Found {len(results)} results for: {arguments['query']}\n\n"
            
            for i, result in enumerate(results, 1):
                response += f"""**Result {i}**
Type: {result.get('doc_type', 'N/A')}
Source: {result.get('source', 'N/A')}
Content: {result.get('content', '')[:200]}...

---
"""
            
            return [TextContent(type="text", text=response)]
        
        elif name == "explain_odoo_code":
            # This would use Claude to explain code
            prompt = f"""Explain this Odoo code in detail:

```python
{arguments['code']}
```

Provide:
1. Line-by-line explanation
2. Odoo API methods used
3. Database queries executed
4. Performance considerations
5. Potential issues or improvements
"""
            
            from anthropic import Anthropic
            claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            
            response = await claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return [TextContent(
                type="text",
                text=response.content[0].text
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"❌ Unknown tool: {name}"
            )]
    
    except Exception as e:
        logger.error("tool_execution_failed", tool=name, error=str(e))
        return [TextContent(
            type="text",
            text=f"❌ Tool execution failed: {str(e)}"
        )]


async def main():
    """
    Run the MCP server
    """
    logger.info("starting_odoo_developer_agent")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
