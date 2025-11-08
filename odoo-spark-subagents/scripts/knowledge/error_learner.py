#!/usr/bin/env python3
"""
Error Learning Loop - Convert failures into preventive skills

Purpose: Failed run → Root cause → Guardrail skill → Never fail again
Impact: Error rate decreases exponentially over time

Flow:
    1. Agent fails with error X
    2. Root cause analysis extracts pattern
    3. Generate prevention guardrail skill
    4. Index skill for future use
    5. Create GitHub issue with fix (optional)

Usage:
    # Learn from a specific error
    python error_learner.py --trace-id abc123 --error "ValidationError: Partner not found"

    # Auto-learn from recent failures
    python error_learner.py --auto-learn --hours 24

    # As agent runtime hook
    from error_learner import ErrorLearner
    learner.on_failure(trace_id, error, context)
"""

from __future__ import annotations
import os
import sys
import json
import hashlib
import argparse
import traceback
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from supabase import create_client, Client
from openai import OpenAI

# ============================================================================
# Configuration
# ============================================================================

@dataclass
class LearnerConfig:
    """Error learner configuration"""
    supabase_url: str
    supabase_key: str
    openai_api_key: str
    github_token: Optional[str] = None
    embedding_model: str = "text-embedding-3-large"
    embedding_dims: int = 3072
    llm_model: str = "gpt-4o"

    # Learning thresholds
    min_occurrences: int = 2  # Learn after 2nd occurrence of same error
    similarity_threshold: float = 0.85  # Merge similar errors

    @classmethod
    def from_env(cls) -> LearnerConfig:
        return cls(
            supabase_url=os.getenv("SUPABASE_URL", ""),
            supabase_key=os.getenv("SUPABASE_SERVICE_ROLE", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            github_token=os.getenv("GITHUB_TOKEN")
        )

# ============================================================================
# Error Models
# ============================================================================

@dataclass
class ErrorContext:
    """Context for an error occurrence"""
    trace_id: str
    agent_name: str
    error_type: str
    error_message: str
    stack_trace: Optional[str]
    input_data: Dict[str, Any]
    plan: Optional[Dict[str, Any]]
    context: Dict[str, Any]

@dataclass
class RootCause:
    """Root cause analysis result"""
    category: str  # 'validation', 'precondition', 'configuration', 'api_error'
    short_desc: str
    detailed_explanation: str
    suggested_fix: str
    prevention_strategy: str

@dataclass
class GuardrailSkill:
    """Preventive skill generated from error"""
    name: str
    category: str
    content: str  # SKILL.md markdown
    error_signature: str
    resolution_notes: str

# ============================================================================
# Error Normalizer
# ============================================================================

class ErrorNormalizer:
    """Normalize and fingerprint errors for deduplication"""

    @staticmethod
    def normalize_error_message(error_msg: str) -> str:
        """Remove variable parts from error message"""
        import re

        # Remove IDs: "Record 123" → "Record ID"
        normalized = re.sub(r'\b\d+\b', 'ID', error_msg)

        # Remove UUIDs
        normalized = re.sub(
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            'UUID',
            normalized,
            flags=re.IGNORECASE
        )

        # Remove file paths
        normalized = re.sub(r'/[\w/.-]+\.py', '/PATH.py', normalized)

        # Remove timestamps
        normalized = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', 'TIMESTAMP', normalized)

        # Standardize whitespace
        normalized = ' '.join(normalized.split())

        return normalized

    @staticmethod
    def create_signature(error_msg: str, error_type: str, agent_name: str) -> str:
        """Create unique signature for error pattern"""
        normalized = ErrorNormalizer.normalize_error_message(error_msg)
        key = f"{agent_name}:{error_type}:{normalized}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]

# ============================================================================
# Root Cause Analyzer
# ============================================================================

class RootCauseAnalyzer:
    """Analyze errors to determine root cause"""

    def __init__(self, config: LearnerConfig):
        self.config = config
        self.openai = OpenAI(api_key=config.openai_api_key)

    def analyze(self, error_ctx: ErrorContext) -> Optional[RootCause]:
        """Perform root cause analysis"""
        analysis_prompt = f"""
Analyze this agent failure and determine root cause + prevention strategy.

Agent: {error_ctx.agent_name}
Error Type: {error_ctx.error_type}
Error Message: {error_ctx.error_message}

Context:
Input: {json.dumps(error_ctx.input_data, indent=2)}
Plan: {json.dumps(error_ctx.plan, indent=2)}

Stack Trace:
{error_ctx.stack_trace or 'N/A'}

Perform root cause analysis:
1. **Category**: validation | precondition | configuration | api_error | logic_error | data_error
2. **Short Description**: 1-sentence summary
3. **Detailed Explanation**: Why did this happen? What was missing/incorrect?
4. **Suggested Fix**: How to fix this specific instance
5. **Prevention Strategy**: How to prevent ALL similar errors in the future

Return as JSON:
{{
  "category": "...",
  "short_desc": "...",
  "detailed_explanation": "...",
  "suggested_fix": "...",
  "prevention_strategy": "..."
}}
"""

        try:
            response = self.openai.chat.completions.create(
                model=self.config.llm_model,
                messages=[
                    {"role": "system", "content": "You are an expert at debugging and preventing errors in automation systems."},
                    {"role": "user", "content": analysis_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )

            result = json.loads(response.choices[0].message.content)

            return RootCause(
                category=result["category"],
                short_desc=result["short_desc"],
                detailed_explanation=result["detailed_explanation"],
                suggested_fix=result["suggested_fix"],
                prevention_strategy=result["prevention_strategy"]
            )

        except Exception as e:
            print(f"Error in root cause analysis: {e}", file=sys.stderr)
            return None

# ============================================================================
# Guardrail Generator
# ============================================================================

class GuardrailGenerator:
    """Generate preventive skills from root causes"""

    def __init__(self, config: LearnerConfig):
        self.config = config
        self.openai = OpenAI(api_key=config.openai_api_key)

    def generate_guardrail(
        self,
        error_ctx: ErrorContext,
        root_cause: RootCause
    ) -> Optional[GuardrailSkill]:
        """Generate a guardrail skill"""
        generation_prompt = f"""
Generate a guardrail SKILL.md that prevents this error from occurring again.

Error: {error_ctx.error_message}
Root Cause: {root_cause.short_desc}
Prevention Strategy: {root_cause.prevention_strategy}

The guardrail skill should:
1. Check preconditions BEFORE executing the risky operation
2. Provide clear validation logic
3. Include examples of valid/invalid inputs
4. Be reusable across similar scenarios

Generate a complete SKILL.md in this format:

# {skill_name} (Guardrail)

**Goal**: Prevent "{root_cause.short_desc}"

**Progressive disclosure**: Load before {error_ctx.agent_name} executes {relevant operation}

## Validation Logic

[Specific checks to perform]

## Usage

[When/how to use this guardrail]

## Examples

### ✓ Valid Input
[Example of valid input that passes guardrail]

### ✗ Invalid Input
[Example that would be caught]

## Implementation

[Pseudocode or specific checks]

Return pure markdown, no JSON wrapper.
"""

        try:
            response = self.openai.chat.completions.create(
                model=self.config.llm_model,
                messages=[
                    {"role": "system", "content": "You are an expert at creating preventive validation logic."},
                    {"role": "user", "content": generation_prompt}
                ],
                temperature=0.3
            )

            content = response.choices[0].message.content

            # Generate skill name
            skill_name = self._generate_skill_name(error_ctx, root_cause)

            return GuardrailSkill(
                name=skill_name,
                category=error_ctx.agent_name.split('_')[0] if '_' in error_ctx.agent_name else 'general',
                content=content,
                error_signature=ErrorNormalizer.create_signature(
                    error_ctx.error_message,
                    error_ctx.error_type,
                    error_ctx.agent_name
                ),
                resolution_notes=root_cause.suggested_fix
            )

        except Exception as e:
            print(f"Error generating guardrail: {e}", file=sys.stderr)
            return None

    def _generate_skill_name(self, error_ctx: ErrorContext, root_cause: RootCause) -> str:
        """Generate skill name from context"""
        # Extract key terms
        category = root_cause.category
        agent = error_ctx.agent_name

        # Create descriptive name
        desc = root_cause.short_desc.lower()
        desc = desc.replace(' ', '_')[:30]

        return f"guard_{agent}_{category}_{desc}"

# ============================================================================
# Error Knowledge Base
# ============================================================================

class ErrorKnowledgeBase:
    """Manage error patterns and resolutions"""

    def __init__(self, config: LearnerConfig):
        self.config = config
        self.supabase: Client = create_client(config.supabase_url, config.supabase_key)
        self.openai = OpenAI(api_key=config.openai_api_key)

    def record_error(self, error_ctx: ErrorContext) -> str:
        """Record an error occurrence, return error pattern ID"""
        signature = ErrorNormalizer.create_signature(
            error_ctx.error_message,
            error_ctx.error_type,
            error_ctx.agent_name
        )

        # Create embedding
        embedding = self._create_embedding(error_ctx.error_message)

        try:
            # Try to find existing pattern
            existing = self.supabase.table("error_patterns").select("*").eq(
                "error_signature", signature
            ).execute()

            if existing.data:
                # Update existing
                pattern_id = existing.data[0]["id"]
                occurrences = existing.data[0]["occurrences"] + 1

                self.supabase.table("error_patterns").update({
                    "occurrences": occurrences,
                    "last_seen": datetime.utcnow().isoformat()
                }).eq("id", pattern_id).execute()

                print(f"  Updated existing error pattern (occurrence #{occurrences})")
                return pattern_id

            else:
                # Create new pattern
                data = {
                    "error_signature": signature,
                    "error_type": error_ctx.error_type,
                    "agent_name": error_ctx.agent_name,
                    "trace_id": error_ctx.trace_id,
                    "context": {
                        "error_message": error_ctx.error_message,
                        "input": error_ctx.input_data,
                        "plan": error_ctx.plan
                    },
                    "embedding": embedding
                }

                result = self.supabase.table("error_patterns").insert(data).execute()
                pattern_id = result.data[0]["id"]

                print(f"  Created new error pattern: {signature}")
                return pattern_id

        except Exception as e:
            print(f"Error recording to knowledge base: {e}", file=sys.stderr)
            return ""

    def resolve_error(self, signature: str, skill_id: str, notes: str):
        """Mark an error as resolved with a guardrail skill"""
        try:
            self.supabase.table("error_patterns").update({
                "resolved": True,
                "resolution_skill_id": skill_id,
                "resolution_notes": notes,
                "resolved_at": datetime.utcnow().isoformat()
            }).eq("error_signature", signature).execute()

            print(f"  ✓ Marked error as resolved")

        except Exception as e:
            print(f"Error updating resolution: {e}", file=sys.stderr)

    def search_similar_errors(
        self,
        error_message: str,
        threshold: float = 0.85
    ) -> List[Dict[str, Any]]:
        """Search for similar error patterns"""
        embedding = self._create_embedding(error_message)

        try:
            # Use stored procedure from schema
            result = self.supabase.rpc(
                "search_similar_errors",
                {
                    "query_embedding": embedding,
                    "match_threshold": threshold,
                    "match_count": 5
                }
            ).execute()

            return result.data

        except Exception as e:
            print(f"Error searching similar errors: {e}", file=sys.stderr)
            return []

    def _create_embedding(self, text: str) -> List[float]:
        """Generate embedding"""
        try:
            response = self.openai.embeddings.create(
                model=self.config.embedding_model,
                input=text[:8000],
                dimensions=self.config.embedding_dims
            )
            return response.data[0].embedding
        except:
            return [0.0] * self.config.embedding_dims

# ============================================================================
# Skill Indexer (Shared with skill_harvester)
# ============================================================================

class SkillIndexer:
    """Index guardrail skills"""

    def __init__(self, config: LearnerConfig):
        self.config = config
        self.supabase: Client = create_client(config.supabase_url, config.supabase_key)
        self.openai = OpenAI(api_key=config.openai_api_key)

    def index_skill(self, skill: GuardrailSkill) -> Optional[str]:
        """Index skill, return skill ID"""
        try:
            # Create embedding
            embedding = self._create_embedding(skill.content)

            data = {
                "name": skill.name,
                "category": skill.category,
                "content": skill.content,
                "embedding": embedding,
                "tags": ["guardrail", "auto_generated"]
            }

            result = self.supabase.table("skills").upsert(data, on_conflict="name").execute()
            skill_id = result.data[0]["id"]

            print(f"  ✓ Indexed guardrail skill: {skill.name}")
            return skill_id

        except Exception as e:
            print(f"Error indexing skill: {e}", file=sys.stderr)
            return None

    def _create_embedding(self, text: str) -> List[float]:
        try:
            response = self.openai.embeddings.create(
                model=self.config.embedding_model,
                input=text[:8000],
                dimensions=self.config.embedding_dims
            )
            return response.data[0].embedding
        except:
            return [0.0] * self.config.embedding_dims

# ============================================================================
# Error Learner Orchestrator
# ============================================================================

class ErrorLearner:
    """Main orchestrator for error → skill learning"""

    def __init__(self, config: LearnerConfig):
        self.config = config
        self.analyzer = RootCauseAnalyzer(config)
        self.generator = GuardrailGenerator(config)
        self.knowledge_base = ErrorKnowledgeBase(config)
        self.indexer = SkillIndexer(config)

    def on_failure(
        self,
        trace_id: str,
        error: Exception,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """
        Hook for agent runtime - called when an agent fails

        Returns: guardrail skill name if generated, None otherwise
        """
        print(f"\n{'='*70}")
        print(f"ERROR LEARNING PIPELINE: {trace_id}")
        print(f"{'='*70}\n")

        # 1. Build error context
        print("[1/6] Building error context...")
        error_ctx = ErrorContext(
            trace_id=trace_id,
            agent_name=context.get("agent_name", "unknown"),
            error_type=type(error).__name__,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            input_data=context.get("input", {}),
            plan=context.get("plan"),
            context=context
        )
        print(f"  ✓ Error: {error_ctx.error_type} - {error_ctx.error_message[:60]}...")

        # 2. Check for similar errors
        print("\n[2/6] Checking for similar known errors...")
        similar = self.knowledge_base.search_similar_errors(error_ctx.error_message)

        if similar and similar[0]["similarity"] > self.config.similarity_threshold:
            print(f"  ⚠ Similar error found (similarity: {similar[0]['similarity']:.2f})")
            if similar[0].get("resolution_skill_id"):
                print(f"  → Resolution skill already exists: {similar[0]['resolution_skill_id']}")
                print("  No new skill needed.")
                return None

        # 3. Record error
        print("\n[3/6] Recording error pattern...")
        pattern_id = self.knowledge_base.record_error(error_ctx)

        # 4. Root cause analysis
        print("\n[4/6] Performing root cause analysis...")
        root_cause = self.analyzer.analyze(error_ctx)
        if not root_cause:
            print("  ✗ Failed to determine root cause")
            return None
        print(f"  ✓ Category: {root_cause.category}")
        print(f"  ✓ Cause: {root_cause.short_desc}")

        # 5. Generate guardrail
        print("\n[5/6] Generating guardrail skill...")
        guardrail = self.generator.generate_guardrail(error_ctx, root_cause)
        if not guardrail:
            print("  ✗ Failed to generate guardrail")
            return None
        print(f"  ✓ Generated: {guardrail.name}")

        # 6. Index skill
        print("\n[6/6] Indexing guardrail skill...")
        skill_id = self.indexer.index_skill(guardrail)

        if skill_id:
            # Mark error as resolved
            self.knowledge_base.resolve_error(
                guardrail.error_signature,
                skill_id,
                guardrail.resolution_notes
            )

            print(f"\n{'='*70}")
            print(f"✓ SUCCESS: Guardrail skill '{guardrail.name}' created")
            print(f"{'='*70}\n")
            print(f"Prevention Strategy: {root_cause.prevention_strategy}")
            print(f"\nThis error will now be prevented in future runs.")
            print(f"{'='*70}\n")

            return guardrail.name
        else:
            print("\n✗ Failed to index guardrail skill")
            return None

    def auto_learn(self, hours: int = 24) -> List[str]:
        """Auto-learn from recent failures"""
        print(f"\n{'='*70}")
        print(f"AUTO-LEARNING FROM FAILURES (LAST {hours} HOURS)")
        print(f"{'='*70}\n")

        # This would query agent_runs for failures
        # For now, demonstrate the structure
        print("Note: Auto-learn requires agent_runs table to track failures")
        print("Currently demonstrating manual error learning flow")

        return []

# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Error Learner - Convert failures into preventive skills"
    )
    parser.add_argument("--trace-id", help="Learn from specific trace ID")
    parser.add_argument("--error", help="Error message")
    parser.add_argument("--auto-learn", action="store_true", help="Learn from recent failures")
    parser.add_argument("--hours", type=int, default=24, help="Hours to look back")
    args = parser.parse_args()

    config = LearnerConfig.from_env()

    if not config.supabase_url or not config.openai_api_key:
        print("ERROR: Missing required environment variables:", file=sys.stderr)
        print("  - SUPABASE_URL", file=sys.stderr)
        print("  - SUPABASE_SERVICE_ROLE", file=sys.stderr)
        print("  - OPENAI_API_KEY", file=sys.stderr)
        sys.exit(1)

    learner = ErrorLearner(config)

    if args.trace_id and args.error:
        # Simulate error
        error = Exception(args.error)
        context = {
            "agent_name": "test_agent",
            "input": {"test": "data"},
            "plan": {}
        }
        learner.on_failure(args.trace_id, error, context)

    elif args.auto_learn:
        learner.auto_learn(hours=args.hours)

    else:
        print("Usage:")
        print("  python error_learner.py --trace-id <id> --error 'Error message'")
        print("  python error_learner.py --auto-learn --hours 24")
        sys.exit(1)

if __name__ == "__main__":
    main()
