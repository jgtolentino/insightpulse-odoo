#!/usr/bin/env python3
"""
Skill Harvester - Auto-generate skills from successful agent runs

Purpose: Observe successful workflows → Extract patterns → Create reusable skills
Impact: Exponential skill growth - every successful run becomes a reusable asset

Usage:
    # Harvest skill from a specific trace
    python skill_harvester.py --trace-id abc123

    # Auto-harvest from recent successful runs
    python skill_harvester.py --auto-harvest --hours 24

    # Run as post-execution hook (in agent runtime)
    from skill_harvester import SkillHarvester
    harvester.maybe_harvest(trace_id, outcome='success', human_approved=True)
"""

from __future__ import annotations
import os
import sys
import json
import re
import argparse
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

from supabase import create_client, Client
from openai import OpenAI

# ============================================================================
# Configuration
# ============================================================================

@dataclass
class HarvesterConfig:
    """Harvester configuration"""
    supabase_url: str
    supabase_key: str
    openai_api_key: str
    embedding_model: str = "text-embedding-3-large"
    embedding_dims: int = 3072
    llm_model: str = "gpt-4o"

    # Harvesting thresholds
    min_confidence: float = 0.75  # Only harvest high-confidence runs
    min_steps: int = 2  # Skip trivial single-step workflows
    max_steps: int = 20  # Skip overly complex flows

    @classmethod
    def from_env(cls) -> HarvesterConfig:
        return cls(
            supabase_url=os.getenv("SUPABASE_URL", ""),
            supabase_key=os.getenv("SUPABASE_SERVICE_ROLE", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", "")
        )

# ============================================================================
# Skill Models
# ============================================================================

@dataclass
class ExtractedPattern:
    """Pattern extracted from a successful workflow"""
    name: str
    category: str  # 'odoo', 'git', 'automation', 'conflict'
    description: str
    steps: List[Dict[str, Any]]
    inputs: Dict[str, str]  # {param_name: type}
    outputs: Dict[str, str]  # {output_name: type}
    examples: List[Dict[str, Any]]
    dependencies: List[str]  # Required other skills
    tags: List[str]

@dataclass
class SkillTemplate:
    """Generated skill ready for storage"""
    name: str
    category: str
    content: str  # Full SKILL.md markdown
    examples: List[Dict[str, Any]]
    dependencies: List[str]
    tags: List[str]
    created_from_trace_id: str

# ============================================================================
# Trace Analyzer
# ============================================================================

class TraceAnalyzer:
    """Analyze OTEL traces to extract reusable patterns"""

    def __init__(self, config: HarvesterConfig):
        self.config = config
        self.supabase: Client = create_client(config.supabase_url, config.supabase_key)
        self.openai = OpenAI(api_key=config.openai_api_key)

    def fetch_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Fetch trace from agent_runs table"""
        try:
            result = self.supabase.table("agent_runs").select("*").eq("trace_id", trace_id).execute()
            if result.data:
                return result.data[0]
        except Exception as e:
            print(f"Error fetching trace {trace_id}: {e}", file=sys.stderr)
        return None

    def is_harvestable(self, trace_data: Dict[str, Any]) -> bool:
        """Determine if a trace is worth harvesting"""
        # Must be successful
        if trace_data.get("status") != "success":
            return False

        # Must be human-approved (or high confidence)
        if not trace_data.get("human_approved", False):
            confidence = trace_data.get("confidence_score", 0)
            if confidence < self.config.min_confidence:
                return False

        # Check plan complexity
        plan = trace_data.get("plan", {})
        steps = plan.get("steps", [])

        if len(steps) < self.config.min_steps:
            return False  # Too trivial

        if len(steps) > self.config.max_steps:
            return False  # Too complex

        return True

    def extract_pattern(self, trace_data: Dict[str, Any]) -> Optional[ExtractedPattern]:
        """Extract a reusable pattern from the trace"""
        plan = trace_data.get("plan", {})
        input_data = trace_data.get("input", {})
        output_data = trace_data.get("output", {})
        agent_name = trace_data.get("agent_name", "unknown")

        # Use LLM to analyze pattern
        pattern_prompt = f"""
Analyze this successful agent workflow and extract a reusable pattern.

Agent: {agent_name}
Input: {json.dumps(input_data, indent=2)}
Plan: {json.dumps(plan, indent=2)}
Output: {json.dumps(output_data, indent=2)}

Extract:
1. **Pattern Name**: concise, descriptive (snake_case)
2. **Category**: odoo | git | automation | conflict
3. **Description**: 1-2 sentences, what problem it solves
4. **Generalized Steps**: abstract the specific values into parameters
5. **Input Parameters**: what inputs are needed (types)
6. **Outputs**: what it produces
7. **Dependencies**: any prerequisite skills or setup
8. **Tags**: relevant keywords

Return as JSON:
{{
  "name": "...",
  "category": "...",
  "description": "...",
  "steps": [
    {{"action": "...", "params": {{}}, "checkpoint": true}}
  ],
  "inputs": {{"param_name": "type"}},
  "outputs": {{"output_name": "type"}},
  "dependencies": ["skill_name"],
  "tags": ["tag1", "tag2"]
}}
"""

        try:
            response = self.openai.chat.completions.create(
                model=self.config.llm_model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting reusable automation patterns from successful workflows."},
                    {"role": "user", "content": pattern_prompt}
                ],
                response_format={"type": "json_object"}
            )

            pattern_json = json.loads(response.choices[0].message.content)

            return ExtractedPattern(
                name=pattern_json["name"],
                category=pattern_json["category"],
                description=pattern_json["description"],
                steps=pattern_json["steps"],
                inputs=pattern_json["inputs"],
                outputs=pattern_json["outputs"],
                examples=[{
                    "input": input_data,
                    "output": output_data,
                    "trace_id": trace_data["trace_id"]
                }],
                dependencies=pattern_json.get("dependencies", []),
                tags=pattern_json.get("tags", [])
            )

        except Exception as e:
            print(f"Error extracting pattern: {e}", file=sys.stderr)
            return None

# ============================================================================
# Skill Generator
# ============================================================================

class SkillGenerator:
    """Generate SKILL.md markdown from extracted patterns"""

    def __init__(self, config: HarvesterConfig):
        self.config = config
        self.openai = OpenAI(api_key=config.openai_api_key)

    def generate_skill_markdown(self, pattern: ExtractedPattern) -> str:
        """Generate complete SKILL.md content"""
        # Use LLM to generate high-quality markdown
        generation_prompt = f"""
Generate a comprehensive SKILL.md file for this automation pattern:

Pattern: {pattern.name}
Category: {pattern.category}
Description: {pattern.description}
Steps: {json.dumps(pattern.steps, indent=2)}
Inputs: {json.dumps(pattern.inputs, indent=2)}
Outputs: {json.dumps(pattern.outputs, indent=2)}

The SKILL.md should include:
1. **Title and Purpose**: Clear goal statement
2. **Progressive Disclosure**: When to load this skill
3. **Inputs**: Required parameters
4. **Steps**: Detailed workflow
5. **Outputs**: What it produces
6. **Guardrails**: Safety constraints
7. **Checkpoints**: Where to save/restore state
8. **Examples**: Concrete usage scenarios

Use the format of existing skills (automation_executor, git_specialist, etc.).
Return pure markdown, no JSON wrapper.
"""

        try:
            response = self.openai.chat.completions.create(
                model=self.config.llm_model,
                messages=[
                    {"role": "system", "content": "You are an expert technical writer creating agent skill documentation."},
                    {"role": "user", "content": generation_prompt}
                ],
                temperature=0.3
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error generating markdown: {e}", file=sys.stderr)
            # Fallback to basic template
            return self._basic_template(pattern)

    def _basic_template(self, pattern: ExtractedPattern) -> str:
        """Fallback basic template if LLM fails"""
        steps_md = "\n".join([
            f"{i+1}. **{step.get('action', 'step')}**: {step.get('params', {})}"
            for i, step in enumerate(pattern.steps)
        ])

        inputs_md = "\n".join([
            f"- `{name}`: {type_}" for name, type_ in pattern.inputs.items()
        ])

        outputs_md = "\n".join([
            f"- `{name}`: {type_}" for name, type_ in pattern.outputs.items()
        ])

        return f"""# {pattern.name}

**Goal**: {pattern.description}

**Progressive disclosure**: Load this skill when {pattern.category} domain goals are detected.

## Inputs

{inputs_md}

## Steps

{steps_md}

## Outputs

{outputs_md}

## Guardrails

- All operations must be atomic
- Dry-run mode enabled by default
- Human approval required for production execution

## Checkpoints

- Checkpoint after each major step
- Enable rollback on failure

## Dependencies

{', '.join(pattern.dependencies) if pattern.dependencies else 'None'}

## Tags

{', '.join(pattern.tags)}
"""

    def create_skill_template(
        self,
        pattern: ExtractedPattern,
        trace_id: str
    ) -> SkillTemplate:
        """Create complete skill template ready for storage"""
        markdown = self.generate_skill_markdown(pattern)

        return SkillTemplate(
            name=pattern.name,
            category=pattern.category,
            content=markdown,
            examples=pattern.examples,
            dependencies=pattern.dependencies,
            tags=pattern.tags,
            created_from_trace_id=trace_id
        )

# ============================================================================
# Skill Indexer
# ============================================================================

class SkillIndexer:
    """Store skills in Supabase with embeddings"""

    def __init__(self, config: HarvesterConfig):
        self.config = config
        self.supabase: Client = create_client(config.supabase_url, config.supabase_key)
        self.openai = OpenAI(api_key=config.openai_api_key)

    def create_embedding(self, text: str) -> List[float]:
        """Generate embedding for skill content"""
        try:
            response = self.openai.embeddings.create(
                model=self.config.embedding_model,
                input=text[:8000],
                dimensions=self.config.embedding_dims
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error creating embedding: {e}", file=sys.stderr)
            return [0.0] * self.config.embedding_dims

    def index_skill(self, skill: SkillTemplate) -> bool:
        """Index skill into database"""
        try:
            # Create embedding from content
            embedding = self.create_embedding(skill.content)

            # Prepare data
            data = {
                "name": skill.name,
                "category": skill.category,
                "content": skill.content,
                "embedding": embedding,
                "examples": skill.examples,
                "dependencies": skill.dependencies,
                "tags": skill.tags,
                "created_from_trace_id": skill.created_from_trace_id
            }

            # Insert or update
            result = self.supabase.table("skills").upsert(data, on_conflict="name").execute()

            print(f"✓ Indexed skill: {skill.name}")
            return True

        except Exception as e:
            print(f"Error indexing skill {skill.name}: {e}", file=sys.stderr)
            return False

    def check_duplicate(self, skill_name: str) -> bool:
        """Check if skill already exists"""
        try:
            result = self.supabase.table("skills").select("id").eq("name", skill_name).execute()
            return len(result.data) > 0
        except:
            return False

# ============================================================================
# Skill Harvester Orchestrator
# ============================================================================

class SkillHarvester:
    """Main orchestrator for skill harvesting"""

    def __init__(self, config: HarvesterConfig):
        self.config = config
        self.analyzer = TraceAnalyzer(config)
        self.generator = SkillGenerator(config)
        self.indexer = SkillIndexer(config)
        self.supabase: Client = create_client(config.supabase_url, config.supabase_key)

    def harvest_from_trace(self, trace_id: str, force: bool = False) -> Optional[str]:
        """
        Harvest a skill from a specific trace

        Returns: skill name if successful, None otherwise
        """
        print(f"\n{'='*70}")
        print(f"HARVESTING SKILL FROM TRACE: {trace_id}")
        print(f"{'='*70}\n")

        # 1. Fetch trace
        print("[1/5] Fetching trace data...")
        trace_data = self.analyzer.fetch_trace(trace_id)
        if not trace_data:
            print("  ✗ Trace not found")
            return None
        print(f"  ✓ Found trace from agent: {trace_data.get('agent_name')}")

        # 2. Check if harvestable
        print("\n[2/5] Checking if harvestable...")
        if not force and not self.analyzer.is_harvestable(trace_data):
            print("  ✗ Trace does not meet harvesting criteria")
            print(f"    - Status: {trace_data.get('status')}")
            print(f"    - Confidence: {trace_data.get('confidence_score')}")
            print(f"    - Human approved: {trace_data.get('human_approved')}")
            return None
        print("  ✓ Trace meets criteria")

        # 3. Extract pattern
        print("\n[3/5] Extracting reusable pattern...")
        pattern = self.analyzer.extract_pattern(trace_data)
        if not pattern:
            print("  ✗ Failed to extract pattern")
            return None
        print(f"  ✓ Extracted pattern: {pattern.name}")
        print(f"    Category: {pattern.category}")
        print(f"    Steps: {len(pattern.steps)}")

        # 4. Check for duplicates
        if not force and self.indexer.check_duplicate(pattern.name):
            print(f"\n  ⚠ Skill '{pattern.name}' already exists (use --force to overwrite)")
            return None

        # 5. Generate skill
        print("\n[4/5] Generating SKILL.md content...")
        skill = self.generator.create_skill_template(pattern, trace_id)
        print(f"  ✓ Generated {len(skill.content)} characters of markdown")

        # 6. Index skill
        print("\n[5/5] Indexing into database...")
        success = self.indexer.index_skill(skill)

        if success:
            print(f"\n{'='*70}")
            print(f"✓ SUCCESS: Skill '{skill.name}' harvested and indexed")
            print(f"{'='*70}\n")
            return skill.name
        else:
            print(f"\n✗ Failed to index skill")
            return None

    def auto_harvest(self, hours: int = 24, min_confidence: float = 0.8) -> List[str]:
        """
        Auto-harvest skills from recent successful runs

        Returns: list of harvested skill names
        """
        print(f"\n{'='*70}")
        print(f"AUTO-HARVESTING FROM LAST {hours} HOURS")
        print(f"{'='*70}\n")

        # Fetch recent successful runs
        since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()

        try:
            result = self.supabase.table("agent_runs").select("*").gte(
                "created_at", since
            ).eq("status", "success").gte("confidence_score", min_confidence).execute()

            candidates = result.data
            print(f"Found {len(candidates)} candidate runs")

            harvested_skills = []

            for i, trace_data in enumerate(candidates, 1):
                print(f"\n[{i}/{len(candidates)}] Processing trace {trace_data['trace_id']}...")

                # Check if already harvested
                if trace_data.get("trace_id") in self._get_harvested_traces():
                    print("  ⊘ Already harvested, skipping")
                    continue

                skill_name = self.harvest_from_trace(trace_data["trace_id"])
                if skill_name:
                    harvested_skills.append(skill_name)

            print(f"\n{'='*70}")
            print(f"AUTO-HARVEST COMPLETE")
            print(f"{'='*70}")
            print(f"Total Candidates: {len(candidates)}")
            print(f"Successfully Harvested: {len(harvested_skills)}")
            print(f"Skills: {', '.join(harvested_skills)}")
            print(f"{'='*70}\n")

            return harvested_skills

        except Exception as e:
            print(f"Error in auto-harvest: {e}", file=sys.stderr)
            return []

    def _get_harvested_traces(self) -> set:
        """Get set of trace IDs that have already been harvested"""
        try:
            result = self.supabase.table("skills").select("created_from_trace_id").execute()
            return {row["created_from_trace_id"] for row in result.data if row["created_from_trace_id"]}
        except:
            return set()

    def maybe_harvest(
        self,
        trace_id: str,
        outcome: str,
        human_approved: bool = False
    ) -> Optional[str]:
        """
        Lightweight hook for agent runtime - conditionally harvest

        Use in agent execution flow:
            result = agent.execute(input)
            harvester.maybe_harvest(result.trace_id, result.outcome, result.human_approved)
        """
        if outcome == "success" and human_approved:
            return self.harvest_from_trace(trace_id)
        return None

# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Skill Harvester - Auto-generate skills from successful runs"
    )
    parser.add_argument("--trace-id", help="Harvest from specific trace ID")
    parser.add_argument("--auto-harvest", action="store_true", help="Auto-harvest recent runs")
    parser.add_argument("--hours", type=int, default=24, help="Hours to look back (for auto-harvest)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing skills")
    args = parser.parse_args()

    # Load config
    config = HarvesterConfig.from_env()

    if not config.supabase_url or not config.openai_api_key:
        print("ERROR: Missing required environment variables:", file=sys.stderr)
        print("  - SUPABASE_URL", file=sys.stderr)
        print("  - SUPABASE_SERVICE_ROLE", file=sys.stderr)
        print("  - OPENAI_API_KEY", file=sys.stderr)
        sys.exit(1)

    harvester = SkillHarvester(config)

    if args.trace_id:
        harvester.harvest_from_trace(args.trace_id, force=args.force)
    elif args.auto_harvest:
        harvester.auto_harvest(hours=args.hours)
    else:
        print("Usage:")
        print("  python skill_harvester.py --trace-id <trace_id>")
        print("  python skill_harvester.py --auto-harvest --hours 24")
        sys.exit(1)

if __name__ == "__main__":
    main()
