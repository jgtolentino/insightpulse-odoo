#!/usr/bin/env python3
"""
Knowledge Client - Agent interface to knowledge graph

Purpose: Provide agents with semantic search over skills, docs, errors
Impact: Agents answer from 100K+ docs instead of hard-coded prompts

Usage (from agent code):
    from knowledge_client import KnowledgeClient

    client = KnowledgeClient.from_env()

    # Find relevant skills
    skills = client.search_skills("create sales order validation")

    # Search Odoo knowledge
    docs = client.search_knowledge("migration from 18 to 19")

    # Check for known errors
    similar_errors = client.search_errors("ValidationError: Partner ID missing")
"""

from __future__ import annotations
import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from supabase import create_client, Client
from openai import OpenAI


@dataclass
class SearchResult:
    """Generic search result"""
    id: str
    title: str
    content: str
    source_url: Optional[str]
    similarity: float
    metadata: Dict[str, Any]


@dataclass
class SkillResult:
    """Skill search result"""
    skill_id: str
    skill_name: str
    content: str
    similarity: float
    success_rate: float
    category: str
    examples: List[Dict[str, Any]]
    dependencies: List[str]


@dataclass
class ErrorResult:
    """Error search result"""
    error_id: str
    error_signature: str
    resolution_skill_id: Optional[str]
    similarity: float
    occurrences: int
    resolution_notes: Optional[str]


class KnowledgeClient:
    """Client for querying the knowledge graph"""

    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        openai_api_key: str,
        embedding_model: str = "text-embedding-3-large",
        embedding_dims: int = 3072
    ):
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.openai = OpenAI(api_key=openai_api_key)
        self.embedding_model = embedding_model
        self.embedding_dims = embedding_dims

    @classmethod
    def from_env(cls) -> KnowledgeClient:
        """Create client from environment variables"""
        return cls(
            supabase_url=os.getenv("SUPABASE_URL", ""),
            supabase_key=os.getenv("SUPABASE_SERVICE_ROLE", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", "")
        )

    # ========================================================================
    # Skill Search
    # ========================================================================

    def search_skills(
        self,
        query: str,
        category: Optional[str] = None,
        threshold: float = 0.7,
        limit: int = 5
    ) -> List[SkillResult]:
        """
        Search for relevant skills by natural language query

        Args:
            query: Natural language description of desired skill
            category: Optional filter ('odoo', 'git', 'automation', 'conflict')
            threshold: Minimum similarity score
            limit: Max results

        Returns:
            List of matching skills ordered by relevance
        """
        embedding = self._create_embedding(query)

        try:
            # Use stored function from schema
            result = self.supabase.rpc(
                "search_skills",
                {
                    "query_embedding": embedding,
                    "match_threshold": threshold,
                    "match_count": limit
                }
            ).execute()

            skills = []
            for row in result.data:
                # Fetch full skill details
                full_skill = self.supabase.table("skills").select("*").eq(
                    "id", row["skill_id"]
                ).execute()

                if full_skill.data:
                    skill_data = full_skill.data[0]
                    skills.append(SkillResult(
                        skill_id=row["skill_id"],
                        skill_name=row["skill_name"],
                        content=row["skill_content"],
                        similarity=row["similarity"],
                        success_rate=row["success_rate"],
                        category=skill_data.get("category", "unknown"),
                        examples=skill_data.get("examples", []),
                        dependencies=skill_data.get("dependencies", [])
                    ))

            # Optional category filter
            if category:
                skills = [s for s in skills if s.category == category]

            return skills

        except Exception as e:
            print(f"Error searching skills: {e}")
            return []

    def get_skill_by_name(self, skill_name: str) -> Optional[SkillResult]:
        """Get a specific skill by exact name"""
        try:
            result = self.supabase.table("skills").select("*").eq(
                "name", skill_name
            ).execute()

            if result.data:
                skill = result.data[0]
                return SkillResult(
                    skill_id=skill["id"],
                    skill_name=skill["name"],
                    content=skill["content"],
                    similarity=1.0,
                    success_rate=skill.get("success_rate", 0.5),
                    category=skill.get("category", "unknown"),
                    examples=skill.get("examples", []),
                    dependencies=skill.get("dependencies", [])
                )
        except Exception as e:
            print(f"Error fetching skill: {e}")

        return None

    # ========================================================================
    # Knowledge Search
    # ========================================================================

    def search_knowledge(
        self,
        query: str,
        source_type: Optional[str] = None,
        odoo_version: Optional[str] = None,
        threshold: float = 0.7,
        limit: int = 10
    ) -> List[SearchResult]:
        """
        Search Odoo knowledge base (docs, forum, GitHub)

        Args:
            query: Natural language query
            source_type: Optional filter ('docs', 'forum', 'github_issue')
            odoo_version: Optional version filter ('19.0', '18.0', etc.)
            threshold: Minimum similarity
            limit: Max results

        Returns:
            List of relevant knowledge documents
        """
        embedding = self._create_embedding(query)

        try:
            result = self.supabase.rpc(
                "search_odoo_knowledge",
                {
                    "query_embedding": embedding,
                    "target_version": odoo_version,
                    "match_threshold": threshold,
                    "match_count": limit
                }
            ).execute()

            results = []
            for row in result.data:
                results.append(SearchResult(
                    id=row["knowledge_id"],
                    title=row["title"],
                    content=row["content"],
                    source_url=row.get("source_url"),
                    similarity=row["similarity"],
                    metadata={
                        "is_solved": row.get("is_solved", False)
                    }
                ))

            # Optional source type filter
            if source_type:
                # Would need to add source_type to search results
                pass

            return results

        except Exception as e:
            print(f"Error searching knowledge: {e}")
            return []

    # ========================================================================
    # Error Search
    # ========================================================================

    def search_errors(
        self,
        error_message: str,
        threshold: float = 0.8,
        limit: int = 5
    ) -> List[ErrorResult]:
        """
        Search for similar known errors

        Args:
            error_message: The error message to search for
            threshold: Minimum similarity (higher for errors = more precise)
            limit: Max results

        Returns:
            List of similar errors with resolutions
        """
        embedding = self._create_embedding(error_message)

        try:
            result = self.supabase.rpc(
                "search_similar_errors",
                {
                    "query_embedding": embedding,
                    "match_threshold": threshold,
                    "match_count": limit
                }
            ).execute()

            errors = []
            for row in result.data:
                # Fetch resolution notes
                full_error = self.supabase.table("error_patterns").select("*").eq(
                    "id", row["error_id"]
                ).execute()

                resolution_notes = None
                if full_error.data:
                    resolution_notes = full_error.data[0].get("resolution_notes")

                errors.append(ErrorResult(
                    error_id=row["error_id"],
                    error_signature=row["error_signature"],
                    resolution_skill_id=row.get("resolution_skill_id"),
                    similarity=row["similarity"],
                    occurrences=row["occurrences"],
                    resolution_notes=resolution_notes
                ))

            return errors

        except Exception as e:
            print(f"Error searching errors: {e}")
            return []

    # ========================================================================
    # Composite Queries (Agent-Friendly)
    # ========================================================================

    def get_context_for_task(
        self,
        task_description: str,
        agent_name: str,
        include_examples: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive context for an agent task

        Returns:
            - relevant_skills: Skills that match the task
            - knowledge_docs: Related documentation
            - known_errors: Similar errors to watch for
            - examples: Concrete examples from skills
        """
        # Determine category from agent name
        category_map = {
            "git_specialist": "git",
            "automation_executor": "odoo",
            "automation_gap_analyzer": "automation",
            "conflict_manager": "conflict"
        }
        category = category_map.get(agent_name, None)

        # Search skills
        skills = self.search_skills(
            query=task_description,
            category=category,
            limit=3
        )

        # Search knowledge
        docs = self.search_knowledge(
            query=task_description,
            limit=5
        )

        # Collect examples
        examples = []
        if include_examples:
            for skill in skills:
                examples.extend(skill.examples)

        return {
            "task": task_description,
            "relevant_skills": [
                {
                    "name": s.skill_name,
                    "content": s.content,
                    "similarity": s.similarity,
                    "success_rate": s.success_rate
                }
                for s in skills
            ],
            "knowledge_docs": [
                {
                    "title": d.title,
                    "content": d.content[:500],  # Truncate
                    "url": d.source_url,
                    "similarity": d.similarity
                }
                for d in docs
            ],
            "examples": examples[:3],  # Top 3 examples
            "suggested_dependencies": list(set(
                dep for skill in skills for dep in skill.dependencies
            ))
        }

    def check_for_known_errors(
        self,
        error_message: str
    ) -> Optional[Dict[str, Any]]:
        """
        Check if an error is known and has a resolution

        Returns:
            - is_known: bool
            - resolution_skill: skill name if available
            - prevention_notes: how to prevent
        """
        errors = self.search_errors(error_message, threshold=0.85, limit=1)

        if errors and errors[0].similarity > 0.85:
            error = errors[0]

            resolution_skill = None
            if error.resolution_skill_id:
                skill = self.supabase.table("skills").select("name").eq(
                    "id", error.resolution_skill_id
                ).execute()
                if skill.data:
                    resolution_skill = skill.data[0]["name"]

            return {
                "is_known": True,
                "similarity": error.similarity,
                "occurrences": error.occurrences,
                "resolution_skill": resolution_skill,
                "prevention_notes": error.resolution_notes
            }

        return {
            "is_known": False,
            "suggestion": "This is a new error. It will be analyzed and added to the knowledge base."
        }

    # ========================================================================
    # Analytics
    # ========================================================================

    def get_growth_metrics(self) -> Dict[str, Any]:
        """Get knowledge growth metrics"""
        try:
            # Skill growth
            skill_growth = self.supabase.table("skill_growth_metrics").select("*").limit(12).execute()

            # Agent improvement
            agent_metrics = self.supabase.table("agent_improvement_metrics").select("*").limit(12).execute()

            # Knowledge growth
            knowledge_growth = self.supabase.table("knowledge_growth_metrics").select("*").limit(12).execute()

            return {
                "skill_growth": skill_growth.data,
                "agent_improvement": agent_metrics.data,
                "knowledge_growth": knowledge_growth.data
            }

        except Exception as e:
            print(f"Error fetching metrics: {e}")
            return {}

    # ========================================================================
    # Helpers
    # ========================================================================

    def _create_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        try:
            response = self.openai.embeddings.create(
                model=self.embedding_model,
                input=text[:8000],
                dimensions=self.embedding_dims
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error creating embedding: {e}")
            return [0.0] * self.embedding_dims


# ============================================================================
# CLI Demo
# ============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python knowledge_client.py search-skills 'create sales order'")
        print("  python knowledge_client.py search-knowledge 'migration guide'")
        print("  python knowledge_client.py search-errors 'ValidationError'")
        print("  python knowledge_client.py get-context 'create PR with fixes' git_specialist")
        sys.exit(1)

    client = KnowledgeClient.from_env()
    command = sys.argv[1]

    if command == "search-skills" and len(sys.argv) == 3:
        results = client.search_skills(sys.argv[2])
        print(f"\nFound {len(results)} skills:\n")
        for r in results:
            print(f"  • {r.skill_name} (similarity: {r.similarity:.2f}, success: {r.success_rate:.0%})")
            print(f"    Category: {r.category}")

    elif command == "search-knowledge" and len(sys.argv) == 3:
        results = client.search_knowledge(sys.argv[2])
        print(f"\nFound {len(results)} documents:\n")
        for r in results:
            print(f"  • {r.title} (similarity: {r.similarity:.2f})")
            print(f"    {r.source_url}")

    elif command == "search-errors" and len(sys.argv) == 3:
        results = client.search_errors(sys.argv[2])
        print(f"\nFound {len(results)} similar errors:\n")
        for r in results:
            print(f"  • {r.error_signature} (similarity: {r.similarity:.2f})")
            print(f"    Occurrences: {r.occurrences}")
            if r.resolution_skill_id:
                print(f"    ✓ Resolved by skill: {r.resolution_skill_id}")

    elif command == "get-context" and len(sys.argv) == 4:
        context = client.get_context_for_task(sys.argv[2], sys.argv[3])
        print(f"\nContext for: {context['task']}\n")
        print(f"Skills: {len(context['relevant_skills'])}")
        print(f"Docs: {len(context['knowledge_docs'])}")
        print(f"Examples: {len(context['examples'])}")

    else:
        print("Invalid command or arguments")
        sys.exit(1)
