"""
Supabase RAG Client for Odoo Developer Agent
Handles vector search across Odoo documentation, OCA modules, and past solutions
"""

import os
from typing import List, Dict, Optional
from supabase import create_client, Client
from anthropic import Anthropic
import structlog

logger = structlog.get_logger()


class OdooKnowledgeBase:
    """
    RAG system for retrieving Odoo development knowledge
    """
    
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        self.claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for semantic search
        Note: Using Claude's native understanding instead of separate embedding model
        """
        # For production, use a dedicated embedding model (e.g., Voyage, OpenAI)
        # This is a placeholder that returns a mock embedding
        # In real implementation, integrate with embedding service
        
        logger.info("generating_embedding", text_length=len(text))
        
        # Mock implementation - replace with actual embedding service
        return [0.0] * 1536  # Standard embedding dimension
    
    async def search_odoo_docs(
        self,
        query: str,
        doc_types: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Search Odoo core documentation and OCA modules
        
        Args:
            query: Natural language search query
            doc_types: Filter by ['core', 'oca', 'custom', 'errors']
            top_k: Number of results to return
        """
        logger.info("searching_odoo_docs", query=query, top_k=top_k)
        
        # Generate query embedding
        query_embedding = await self.generate_embedding(query)
        
        # Build filter
        query_builder = self.supabase.table('odoo_knowledge').select('*')
        
        if doc_types:
            query_builder = query_builder.in_('doc_type', doc_types)
        
        # Vector similarity search
        results = query_builder.order(
            'embedding',
            desc=True,
            # Vector distance calculation
        ).limit(top_k).execute()
        
        logger.info("search_complete", results_count=len(results.data))
        
        return results.data
    
    async def search_similar_modules(
        self,
        description: str,
        model_names: Optional[List[str]] = None,
        top_k: int = 3
    ) -> List[Dict]:
        """
        Find OCA modules similar to requirements
        
        Args:
            description: What the module should do
            model_names: Specific Odoo models involved (e.g., ['account.move'])
            top_k: Number of similar modules to return
        """
        logger.info("searching_similar_modules", description=description)
        
        query = f"Odoo module that {description}"
        if model_names:
            query += f" involving models: {', '.join(model_names)}"
        
        results = await self.search_odoo_docs(
            query=query,
            doc_types=['oca', 'custom'],
            top_k=top_k
        )
        
        return results
    
    async def search_error_solutions(
        self,
        error_message: str,
        module_name: Optional[str] = None,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Find similar errors and their solutions
        
        Args:
            error_message: The error traceback or message
            module_name: Specific module where error occurred
            top_k: Number of similar errors to retrieve
        """
        logger.info("searching_error_solutions", error=error_message[:100])
        
        query = f"Odoo error: {error_message}"
        if module_name:
            query += f" in module {module_name}"
        
        # Search in errors and support tickets
        results = await self.search_odoo_docs(
            query=query,
            doc_types=['errors', 'support_tickets'],
            top_k=top_k
        )
        
        return results
    
    async def get_tenant_context(
        self,
        tenant_id: str,
        context_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve tenant-specific configuration and customizations
        
        Args:
            tenant_id: Client tenant identifier
            context_type: Filter by ['config', 'custom_modules', 'integrations']
        """
        logger.info("fetching_tenant_context", tenant_id=tenant_id)
        
        query_builder = self.supabase.table('tenant_knowledge')\
            .select('*')\
            .eq('tenant_id', tenant_id)
        
        if context_type:
            query_builder = query_builder.eq('knowledge_type', context_type)
        
        results = query_builder.execute()
        
        return results.data
    
    async def store_generated_code(
        self,
        module_name: str,
        description: str,
        code_files: Dict[str, str],
        metadata: Dict,
        quality_score: float
    ) -> str:
        """
        Store generated module for future reference
        
        Args:
            module_name: Name of the Odoo module
            description: What the module does
            code_files: Dict of filename -> code content
            metadata: Additional context (models, dependencies, etc.)
            quality_score: OCA quality check score (0-1)
        
        Returns:
            record_id: Database ID of stored module
        """
        logger.info("storing_generated_code", module=module_name)
        
        # Generate embedding for the module description
        embedding = await self.generate_embedding(
            f"{module_name}: {description}\n{metadata}"
        )
        
        result = self.supabase.table('odoo_knowledge').insert({
            'doc_type': 'custom',
            'module_name': module_name,
            'description': description,
            'code_files': code_files,
            'metadata': metadata,
            'embedding': embedding,
            'quality_score': quality_score,
            'source': 'agent_generated',
            'created_at': 'now()'
        }).execute()
        
        return result.data[0]['id']
    
    async def store_error_solution(
        self,
        error_message: str,
        error_context: Dict,
        solution: str,
        tenant_id: Optional[str] = None
    ) -> str:
        """
        Store error and solution for future reference
        
        Args:
            error_message: The error that occurred
            error_context: Module, function, line number, etc.
            solution: How it was fixed
            tenant_id: If tenant-specific
        """
        logger.info("storing_error_solution", error=error_message[:100])
        
        embedding = await self.generate_embedding(
            f"Error: {error_message}\nContext: {error_context}\nSolution: {solution}"
        )
        
        result = self.supabase.table('odoo_knowledge').insert({
            'doc_type': 'errors',
            'content': f"Error: {error_message}",
            'error_context': error_context,
            'solution': solution,
            'tenant_id': tenant_id,
            'embedding': embedding,
            'source': 'agent_solved',
            'created_at': 'now()'
        }).execute()
        
        return result.data[0]['id']
    
    async def get_oca_best_practices(
        self,
        topic: str
    ) -> List[Dict]:
        """
        Retrieve OCA coding standards and best practices
        
        Args:
            topic: Specific area (e.g., 'naming', 'security', 'performance')
        """
        logger.info("fetching_oca_best_practices", topic=topic)
        
        results = await self.search_odoo_docs(
            query=f"OCA best practices for {topic}",
            doc_types=['oca'],
            top_k=5
        )
        
        return results


class RAGContextBuilder:
    """
    Builds comprehensive context for LLM prompts from RAG results
    """
    
    def __init__(self, knowledge_base: OdooKnowledgeBase):
        self.kb = knowledge_base
    
    async def build_module_generation_context(
        self,
        description: str,
        models: List[str]
    ) -> str:
        """
        Gather relevant examples and documentation for module generation
        """
        # Find similar modules
        similar = await self.kb.search_similar_modules(
            description=description,
            model_names=models,
            top_k=3
        )
        
        # Get OCA best practices
        practices = await self.kb.get_oca_best_practices("module_structure")
        
        # Format context
        context = "## Similar Existing Modules\n\n"
        for i, module in enumerate(similar, 1):
            context += f"### Example {i}: {module.get('module_name', 'Unknown')}\n"
            context += f"Description: {module.get('description', 'N/A')}\n"
            context += f"Code snippet:\n```python\n{module.get('code_snippet', 'N/A')}\n```\n\n"
        
        context += "\n## OCA Best Practices\n\n"
        for practice in practices:
            context += f"- {practice.get('content', '')}\n"
        
        return context
    
    async def build_debugging_context(
        self,
        error: str,
        module: str,
        tenant_id: Optional[str] = None
    ) -> str:
        """
        Gather relevant error solutions and tenant context
        """
        # Find similar errors
        similar_errors = await self.kb.search_error_solutions(
            error_message=error,
            module_name=module,
            top_k=5
        )
        
        # Get tenant context if provided
        tenant_context = []
        if tenant_id:
            tenant_context = await self.kb.get_tenant_context(
                tenant_id=tenant_id,
                context_type='config'
            )
        
        # Format context
        context = "## Similar Errors and Solutions\n\n"
        for i, err in enumerate(similar_errors, 1):
            context += f"### Error {i}\n"
            context += f"Problem: {err.get('content', 'N/A')}\n"
            context += f"Solution: {err.get('solution', 'N/A')}\n\n"
        
        if tenant_context:
            context += "\n## Tenant-Specific Configuration\n\n"
            for config in tenant_context:
                context += f"- {config.get('key', '')}: {config.get('value', '')}\n"
        
        return context
