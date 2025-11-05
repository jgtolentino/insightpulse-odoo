#!/usr/bin/env python3
"""
DeepCode MCP Server
Paper2Code + Text2Web + Text2Backend for InsightPulse AI Finance SSC

Integrates DeepCode's multi-agent capabilities with Claude Code via MCP.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
        LoggingLevel
    )
except ImportError:
    print("Error: MCP library not found. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("deepcode-mcp")

# Import DeepCode components
try:
    from .deepcode_client import DeepCodeClient
    from .workflows import WorkflowEngine
    from .bir_generator import BIRAlgorithmGenerator
except ImportError:
    logger.warning("DeepCode client modules not found, using fallback mode")
    DeepCodeClient = None
    WorkflowEngine = None
    BIRAlgorithmGenerator = None


class DeepCodeMCPServer:
    """MCP Server for DeepCode integration"""

    def __init__(self):
        self.server = Server("deepcode-server")
        self.workspace_dir = Path(os.getenv("WORKSPACE_DIR", "/home/user/insightpulse-odoo"))
        self.config_path = Path(os.getenv("CONFIG_PATH", "./config"))

        # Initialize DeepCode client
        if DeepCodeClient:
            self.client = DeepCodeClient(self.config_path)
            self.workflow_engine = WorkflowEngine(self.client)
            self.bir_generator = BIRAlgorithmGenerator(self.client)
        else:
            logger.warning("Running in fallback mode without DeepCode client")
            self.client = None

        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register MCP tool handlers"""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available DeepCode tools"""
            return [
                Tool(
                    name="deepcode_paper2code",
                    description="Convert research papers to production code. Supports arXiv, HuggingFace Papers, and PDF files.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "paper_source": {
                                "type": "string",
                                "description": "URL or path to paper (arXiv URL, HuggingFace Papers URL, or local PDF path)"
                            },
                            "output_type": {
                                "type": "string",
                                "enum": ["algorithm", "model", "full_module"],
                                "description": "Type of code to generate",
                                "default": "algorithm"
                            },
                            "target_framework": {
                                "type": "string",
                                "enum": ["odoo", "fastapi", "django", "generic"],
                                "description": "Target framework for code generation",
                                "default": "generic"
                            },
                            "optimizations": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Optimization flags (e.g., ['gpu', 'batch', 'rtx4090'])",
                                "default": []
                            },
                            "output_path": {
                                "type": "string",
                                "description": "Where to save generated code (relative to workspace)"
                            }
                        },
                        "required": ["paper_source", "output_path"]
                    }
                ),
                Tool(
                    name="deepcode_text2web",
                    description="Generate frontend applications from natural language descriptions.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "Natural language description of the frontend app"
                            },
                            "framework": {
                                "type": "string",
                                "enum": ["react", "vue", "svelte"],
                                "description": "Frontend framework",
                                "default": "react"
                            },
                            "styling": {
                                "type": "string",
                                "enum": ["tailwind", "bootstrap", "material-ui", "none"],
                                "description": "CSS framework",
                                "default": "tailwind"
                            },
                            "features": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of required features",
                                "default": []
                            },
                            "output_path": {
                                "type": "string",
                                "description": "Where to save generated frontend code"
                            }
                        },
                        "required": ["description", "output_path"]
                    }
                ),
                Tool(
                    name="deepcode_text2backend",
                    description="Generate backend systems from requirements.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "requirements": {
                                "type": "string",
                                "description": "Natural language description or structured specification"
                            },
                            "framework": {
                                "type": "string",
                                "enum": ["fastapi", "django", "flask"],
                                "description": "Backend framework",
                                "default": "fastapi"
                            },
                            "database": {
                                "type": "string",
                                "enum": ["postgresql", "supabase", "mongodb", "sqlite"],
                                "description": "Database system",
                                "default": "postgresql"
                            },
                            "features": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of required features (auth, api, webhooks, etc.)",
                                "default": []
                            },
                            "output_path": {
                                "type": "string",
                                "description": "Where to save generated backend code"
                            }
                        },
                        "required": ["requirements", "output_path"]
                    }
                ),
                Tool(
                    name="deepcode_bir_algorithm",
                    description="Generate BIR (Philippine tax) algorithms from specifications. Specialized for BIR forms like 1601-C, 2550-Q, 1702-RT, etc.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "bir_form": {
                                "type": "string",
                                "description": "BIR form identifier (e.g., '1601c', '2550q', '1702rt')"
                            },
                            "spec_source": {
                                "type": "string",
                                "description": "Path to BIR specification document (PDF, DOCX, or URL)"
                            },
                            "include_validation": {
                                "type": "boolean",
                                "description": "Include validation logic",
                                "default": True
                            },
                            "include_tests": {
                                "type": "boolean",
                                "description": "Generate test cases",
                                "default": True
                            },
                            "output_path": {
                                "type": "string",
                                "description": "Where to save generated BIR algorithm code"
                            }
                        },
                        "required": ["bir_form", "spec_source", "output_path"]
                    }
                ),
                Tool(
                    name="deepcode_odoo_module",
                    description="Generate complete Odoo module with models, views, and business logic.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "module_name": {
                                "type": "string",
                                "description": "Name of the Odoo module (snake_case)"
                            },
                            "description": {
                                "type": "string",
                                "description": "What the module should do"
                            },
                            "models": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of required models",
                                "default": []
                            },
                            "views": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of required views (tree, form, kanban, etc.)",
                                "default": ["tree", "form"]
                            },
                            "features": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Additional features (workflow, reporting, api, etc.)",
                                "default": []
                            },
                            "output_path": {
                                "type": "string",
                                "description": "Where to save the Odoo module"
                            }
                        },
                        "required": ["module_name", "description", "output_path"]
                    }
                ),
                Tool(
                    name="deepcode_optimize_algorithm",
                    description="Optimize existing algorithms using latest research. Searches for recent papers and applies optimizations.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "algorithm_path": {
                                "type": "string",
                                "description": "Path to current algorithm implementation"
                            },
                            "research_query": {
                                "type": "string",
                                "description": "What to search for (e.g., 'OCR optimization 2025')"
                            },
                            "target_hardware": {
                                "type": "string",
                                "enum": ["cpu", "gpu", "rtx4090", "tpu", "any"],
                                "description": "Target hardware for optimization",
                                "default": "any"
                            },
                            "metrics": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Metrics to optimize (speed, accuracy, memory, etc.)",
                                "default": ["speed", "accuracy"]
                            }
                        },
                        "required": ["algorithm_path", "research_query"]
                    }
                ),
                Tool(
                    name="deepcode_workflow",
                    description="Execute predefined multi-step DeepCode workflows (bir_full_compliance, finance_dashboard, ocr_pipeline, etc.)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workflow_name": {
                                "type": "string",
                                "enum": ["bir_full_compliance", "finance_dashboard", "ocr_pipeline", "custom"],
                                "description": "Name of the workflow to execute"
                            },
                            "workflow_spec": {
                                "type": "object",
                                "description": "Workflow definition (for custom workflows)",
                                "default": {}
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Workflow-specific parameters",
                                "default": {}
                            }
                        },
                        "required": ["workflow_name"]
                    }
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
            """Handle tool calls"""
            try:
                logger.info(f"Tool called: {name} with arguments: {arguments}")

                if name == "deepcode_paper2code":
                    return await self._handle_paper2code(arguments)
                elif name == "deepcode_text2web":
                    return await self._handle_text2web(arguments)
                elif name == "deepcode_text2backend":
                    return await self._handle_text2backend(arguments)
                elif name == "deepcode_bir_algorithm":
                    return await self._handle_bir_algorithm(arguments)
                elif name == "deepcode_odoo_module":
                    return await self._handle_odoo_module(arguments)
                elif name == "deepcode_optimize_algorithm":
                    return await self._handle_optimize_algorithm(arguments)
                elif name == "deepcode_workflow":
                    return await self._handle_workflow(arguments)
                else:
                    return [TextContent(
                        type="text",
                        text=f"Error: Unknown tool '{name}'"
                    )]

            except Exception as e:
                logger.error(f"Error executing tool {name}: {str(e)}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]

    async def _handle_paper2code(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        """Handle paper2code requests"""
        paper_source = arguments["paper_source"]
        output_type = arguments.get("output_type", "algorithm")
        target_framework = arguments.get("target_framework", "generic")
        optimizations = arguments.get("optimizations", [])
        output_path = Path(self.workspace_dir) / arguments["output_path"]

        logger.info(f"Generating {output_type} from {paper_source}")

        if not self.client:
            return [TextContent(
                type="text",
                text="Error: DeepCode client not initialized. Please install deepcode-hku: pip install deepcode-hku"
            )]

        try:
            # Generate code from paper
            result = await self.client.paper2code(
                paper_source=paper_source,
                output_type=output_type,
                target_framework=target_framework,
                optimizations=optimizations,
                output_path=str(output_path)
            )

            return [TextContent(
                type="text",
                text=f"✅ Successfully generated {output_type} from paper\n\n"
                     f"**Source:** {paper_source}\n"
                     f"**Framework:** {target_framework}\n"
                     f"**Output:** {output_path}\n\n"
                     f"**Files generated:**\n{result['files']}\n\n"
                     f"**Summary:**\n{result['summary']}"
            )]

        except Exception as e:
            logger.error(f"Paper2Code error: {str(e)}")
            return [TextContent(
                type="text",
                text=f"❌ Error generating code from paper: {str(e)}"
            )]

    async def _handle_text2web(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        """Handle text2web requests"""
        description = arguments["description"]
        framework = arguments.get("framework", "react")
        styling = arguments.get("styling", "tailwind")
        features = arguments.get("features", [])
        output_path = Path(self.workspace_dir) / arguments["output_path"]

        logger.info(f"Generating {framework} frontend")

        if not self.client:
            return [TextContent(
                type="text",
                text="Error: DeepCode client not initialized"
            )]

        try:
            result = await self.client.text2web(
                description=description,
                framework=framework,
                styling=styling,
                features=features,
                output_path=str(output_path)
            )

            return [TextContent(
                type="text",
                text=f"✅ Successfully generated {framework} frontend\n\n"
                     f"**Framework:** {framework}\n"
                     f"**Styling:** {styling}\n"
                     f"**Output:** {output_path}\n\n"
                     f"**Components:**\n{result['components']}\n\n"
                     f"**Next steps:**\n"
                     f"```bash\n"
                     f"cd {output_path}\n"
                     f"npm install\n"
                     f"npm run dev\n"
                     f"```"
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Error: {str(e)}"
            )]

    async def _handle_text2backend(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        """Handle text2backend requests"""
        requirements = arguments["requirements"]
        framework = arguments.get("framework", "fastapi")
        database = arguments.get("database", "postgresql")
        features = arguments.get("features", [])
        output_path = Path(self.workspace_dir) / arguments["output_path"]

        logger.info(f"Generating {framework} backend")

        if not self.client:
            return [TextContent(
                type="text",
                text="Error: DeepCode client not initialized"
            )]

        try:
            result = await self.client.text2backend(
                requirements=requirements,
                framework=framework,
                database=database,
                features=features,
                output_path=str(output_path)
            )

            return [TextContent(
                type="text",
                text=f"✅ Successfully generated {framework} backend\n\n"
                     f"**Framework:** {framework}\n"
                     f"**Database:** {database}\n"
                     f"**Output:** {output_path}\n\n"
                     f"**Endpoints:**\n{result['endpoints']}\n\n"
                     f"**Next steps:**\n"
                     f"```bash\n"
                     f"cd {output_path}\n"
                     f"pip install -r requirements.txt\n"
                     f"uvicorn main:app --reload\n"
                     f"```"
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Error: {str(e)}"
            )]

    async def _handle_bir_algorithm(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        """Handle BIR algorithm generation"""
        bir_form = arguments["bir_form"]
        spec_source = arguments["spec_source"]
        include_validation = arguments.get("include_validation", True)
        include_tests = arguments.get("include_tests", True)
        output_path = Path(self.workspace_dir) / arguments["output_path"]

        logger.info(f"Generating BIR Form {bir_form} algorithm")

        if not self.bir_generator:
            return [TextContent(
                type="text",
                text="Error: BIR generator not initialized"
            )]

        try:
            result = await self.bir_generator.generate(
                bir_form=bir_form,
                spec_source=spec_source,
                include_validation=include_validation,
                include_tests=include_tests,
                output_path=str(output_path)
            )

            return [TextContent(
                type="text",
                text=f"✅ Successfully generated BIR Form {bir_form} algorithm\n\n"
                     f"**Form:** {bir_form}\n"
                     f"**Output:** {output_path}\n\n"
                     f"**Generated files:**\n{result['files']}\n\n"
                     f"**Features:**\n"
                     f"- Tax computation logic\n"
                     f"- {'Validation rules' if include_validation else 'No validation'}\n"
                     f"- {'Test cases' if include_tests else 'No tests'}\n\n"
                     f"**Integration:**\n{result['integration_guide']}"
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Error: {str(e)}"
            )]

    async def _handle_odoo_module(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        """Handle Odoo module generation"""
        module_name = arguments["module_name"]
        description = arguments["description"]
        models = arguments.get("models", [])
        views = arguments.get("views", ["tree", "form"])
        features = arguments.get("features", [])
        output_path = Path(self.workspace_dir) / arguments["output_path"]

        logger.info(f"Generating Odoo module: {module_name}")

        if not self.client:
            return [TextContent(
                type="text",
                text="Error: DeepCode client not initialized"
            )]

        try:
            result = await self.client.generate_odoo_module(
                module_name=module_name,
                description=description,
                models=models,
                views=views,
                features=features,
                output_path=str(output_path)
            )

            return [TextContent(
                type="text",
                text=f"✅ Successfully generated Odoo module: {module_name}\n\n"
                     f"**Module:** {module_name}\n"
                     f"**Output:** {output_path}\n\n"
                     f"**Structure:**\n{result['structure']}\n\n"
                     f"**Models:** {', '.join(models)}\n"
                     f"**Views:** {', '.join(views)}\n\n"
                     f"**Next steps:**\n"
                     f"```bash\n"
                     f"# Install module\n"
                     f"docker-compose exec odoo /opt/odoo/odoo-bin \\\n"
                     f"  -c /etc/odoo/odoo.conf -d odoo19 \\\n"
                     f"  -i {module_name} --stop-after-init\n"
                     f"```"
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Error: {str(e)}"
            )]

    async def _handle_optimize_algorithm(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        """Handle algorithm optimization"""
        algorithm_path = Path(self.workspace_dir) / arguments["algorithm_path"]
        research_query = arguments["research_query"]
        target_hardware = arguments.get("target_hardware", "any")
        metrics = arguments.get("metrics", ["speed", "accuracy"])

        logger.info(f"Optimizing algorithm: {algorithm_path}")

        if not self.client:
            return [TextContent(
                type="text",
                text="Error: DeepCode client not initialized"
            )]

        try:
            result = await self.client.optimize_algorithm(
                algorithm_path=str(algorithm_path),
                research_query=research_query,
                target_hardware=target_hardware,
                metrics=metrics
            )

            return [TextContent(
                type="text",
                text=f"✅ Algorithm optimization complete\n\n"
                     f"**Original:** {algorithm_path}\n"
                     f"**Optimized:** {result['output_path']}\n\n"
                     f"**Papers used:**\n{result['papers']}\n\n"
                     f"**Improvements:**\n{result['improvements']}\n\n"
                     f"**Benchmarks:**\n{result['benchmarks']}"
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Error: {str(e)}"
            )]

    async def _handle_workflow(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        """Handle workflow execution"""
        workflow_name = arguments["workflow_name"]
        workflow_spec = arguments.get("workflow_spec", {})
        parameters = arguments.get("parameters", {})

        logger.info(f"Executing workflow: {workflow_name}")

        if not self.workflow_engine:
            return [TextContent(
                type="text",
                text="Error: Workflow engine not initialized"
            )]

        try:
            result = await self.workflow_engine.execute(
                workflow_name=workflow_name,
                workflow_spec=workflow_spec,
                parameters=parameters
            )

            return [TextContent(
                type="text",
                text=f"✅ Workflow complete: {workflow_name}\n\n"
                     f"**Steps executed:** {result['steps_completed']}\n"
                     f"**Duration:** {result['duration']}s\n\n"
                     f"**Results:**\n{result['summary']}\n\n"
                     f"**Outputs:**\n{result['outputs']}"
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Error: {str(e)}"
            )]

    async def run(self):
        """Run the MCP server"""
        logger.info("Starting DeepCode MCP Server...")
        logger.info(f"Workspace: {self.workspace_dir}")
        logger.info(f"Config: {self.config_path}")

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def main():
    """Main entry point"""
    server = DeepCodeMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
