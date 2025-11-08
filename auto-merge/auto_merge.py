#!/usr/bin/env python3
"""
AI-Powered Auto-Merge Conflict Resolution System

Three-tier resolution strategy:
1. Tier 1 (95%): Pattern-based safe auto-merge
2. Tier 2 (4%): LLM-assisted semantic resolution
3. Tier 3 (1%): Human review deferral

Author: InsightPulse AI
License: MIT
"""

import os
import re
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import anthropic


class ResolutionTier(Enum):
    """Resolution tier classification"""
    SAFE_AUTO = "tier1_safe_auto"
    LLM_ASSISTED = "tier2_llm_assisted"
    HUMAN_REVIEW = "tier3_human_review"


class ConflictType(Enum):
    """Types of merge conflicts"""
    NON_OVERLAPPING = "non_overlapping"
    FORMATTING = "formatting_only"
    DOCUMENTATION = "documentation"
    SEMANTIC = "semantic_conflict"
    LOGIC = "logic_conflict"
    UNKNOWN = "unknown"


@dataclass
class ConflictMarkers:
    """Parsed conflict markers"""
    file_path: str
    start_line: int
    separator_line: int
    end_line: int
    head_content: List[str]
    incoming_content: List[str]
    conflict_type: ConflictType


@dataclass
class ResolutionResult:
    """Result of conflict resolution"""
    file_path: str
    tier: ResolutionTier
    conflict_type: ConflictType
    confidence: float
    resolved_content: Optional[str]
    reasoning: str
    timestamp: str
    success: bool
    error: Optional[str] = None

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            **asdict(self),
            'tier': self.tier.value,
            'conflict_type': self.conflict_type.value
        }


class HighRiskFileDetector:
    """Detects high-risk files that require human review"""

    HIGH_RISK_PATTERNS = [
        r'.*\.sql$',                    # SQL files
        r'.*migration.*\.py$',          # Database migrations
        r'.*auth.*\.py$',               # Authentication
        r'.*security.*\.py$',           # Security modules
        r'.*\.env.*',                   # Environment files
        r'.*secret.*',                  # Secrets
        r'.*password.*',                # Password-related
        r'.*config/production.*',       # Production configs
        r'.*\.key$',                    # Key files
        r'.*\.pem$',                    # Certificate files
    ]

    @classmethod
    def is_high_risk(cls, file_path: str) -> bool:
        """Check if file is high-risk"""
        for pattern in cls.HIGH_RISK_PATTERNS:
            if re.match(pattern, file_path, re.IGNORECASE):
                return True
        return False


class ConflictParser:
    """Parse Git conflict markers from files"""

    CONFLICT_START = re.compile(r'^<{7} (.+)$')
    CONFLICT_SEP = re.compile(r'^={7}$')
    CONFLICT_END = re.compile(r'^>{7} (.+)$')

    @classmethod
    def find_conflicts(cls, file_path: str) -> List[ConflictMarkers]:
        """Find all conflicts in a file"""
        conflicts = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return conflicts

        i = 0
        while i < len(lines):
            # Look for conflict start marker
            start_match = cls.CONFLICT_START.match(lines[i])
            if not start_match:
                i += 1
                continue

            start_line = i
            head_content = []

            # Collect HEAD content
            i += 1
            while i < len(lines) and not cls.CONFLICT_SEP.match(lines[i]):
                head_content.append(lines[i])
                i += 1

            if i >= len(lines):
                break

            separator_line = i
            incoming_content = []

            # Collect incoming content
            i += 1
            while i < len(lines) and not cls.CONFLICT_END.match(lines[i]):
                incoming_content.append(lines[i])
                i += 1

            if i >= len(lines):
                break

            end_line = i

            # Classify conflict type
            conflict_type = cls._classify_conflict(
                file_path, head_content, incoming_content
            )

            conflicts.append(ConflictMarkers(
                file_path=file_path,
                start_line=start_line,
                separator_line=separator_line,
                end_line=end_line,
                head_content=head_content,
                incoming_content=incoming_content,
                conflict_type=conflict_type
            ))

            i += 1

        return conflicts

    @classmethod
    def _classify_conflict(
        cls,
        file_path: str,
        head_content: List[str],
        incoming_content: List[str]
    ) -> ConflictType:
        """Classify the type of conflict"""

        # Check if documentation
        if any(ext in file_path.lower() for ext in ['.md', '.rst', '.txt', 'readme']):
            return ConflictType.DOCUMENTATION

        # Check if formatting only (whitespace differences)
        head_stripped = [line.strip() for line in head_content]
        incoming_stripped = [line.strip() for line in incoming_content]
        if head_stripped == incoming_stripped:
            return ConflictType.FORMATTING

        # Check if non-overlapping (different sections)
        head_text = ''.join(head_content).strip()
        incoming_text = ''.join(incoming_content).strip()

        # Simple heuristic: if one is empty or they don't share common keywords
        if not head_text or not incoming_text:
            return ConflictType.NON_OVERLAPPING

        # Check for Makefile targets (common non-overlapping pattern)
        if file_path.endswith('Makefile') or 'makefile' in file_path.lower():
            # Check if different targets
            head_targets = set(re.findall(r'^([a-z-]+):', head_text, re.MULTILINE))
            incoming_targets = set(re.findall(r'^([a-z-]+):', incoming_text, re.MULTILINE))
            if head_targets and incoming_targets and not head_targets.intersection(incoming_targets):
                return ConflictType.NON_OVERLAPPING

        return ConflictType.UNKNOWN


class SafeAutoMerger:
    """Tier 1: Safe pattern-based auto-merge"""

    @classmethod
    def can_auto_merge(cls, conflict: ConflictMarkers) -> bool:
        """Check if conflict can be safely auto-merged"""

        # High-risk files require human review
        if HighRiskFileDetector.is_high_risk(conflict.file_path):
            return False

        # Safe auto-merge patterns
        safe_types = [
            ConflictType.NON_OVERLAPPING,
            ConflictType.FORMATTING,
            ConflictType.DOCUMENTATION
        ]

        return conflict.conflict_type in safe_types

    @classmethod
    def resolve(cls, conflict: ConflictMarkers) -> ResolutionResult:
        """Resolve conflict using safe patterns"""

        if not cls.can_auto_merge(conflict):
            return ResolutionResult(
                file_path=conflict.file_path,
                tier=ResolutionTier.SAFE_AUTO,
                conflict_type=conflict.conflict_type,
                confidence=0.0,
                resolved_content=None,
                reasoning="Not safe for auto-merge",
                timestamp=datetime.utcnow().isoformat(),
                success=False
            )

        # Resolution strategy based on conflict type
        if conflict.conflict_type == ConflictType.NON_OVERLAPPING:
            # Keep both sections
            resolved = ''.join(conflict.head_content) + ''.join(conflict.incoming_content)
            confidence = 0.95
            reasoning = "Non-overlapping sections - kept both"

        elif conflict.conflict_type == ConflictType.FORMATTING:
            # Prefer HEAD (already formatted)
            resolved = ''.join(conflict.head_content)
            confidence = 0.98
            reasoning = "Formatting-only conflict - kept HEAD formatting"

        elif conflict.conflict_type == ConflictType.DOCUMENTATION:
            # Keep both, separated by newline
            resolved = ''.join(conflict.head_content) + '\n' + ''.join(conflict.incoming_content)
            confidence = 0.90
            reasoning = "Documentation conflict - merged both versions"

        else:
            resolved = None
            confidence = 0.0
            reasoning = "Unknown conflict type"

        return ResolutionResult(
            file_path=conflict.file_path,
            tier=ResolutionTier.SAFE_AUTO,
            conflict_type=conflict.conflict_type,
            confidence=confidence,
            resolved_content=resolved,
            reasoning=reasoning,
            timestamp=datetime.utcnow().isoformat(),
            success=resolved is not None
        )


class LLMAssistedMerger:
    """Tier 2: LLM-assisted semantic resolution"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with Anthropic API key"""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def resolve(self, conflict: ConflictMarkers) -> ResolutionResult:
        """Resolve conflict using Claude Sonnet 4"""

        # High-risk files require human review
        if HighRiskFileDetector.is_high_risk(conflict.file_path):
            return ResolutionResult(
                file_path=conflict.file_path,
                tier=ResolutionTier.LLM_ASSISTED,
                conflict_type=conflict.conflict_type,
                confidence=0.0,
                resolved_content=None,
                reasoning="High-risk file - requires human review",
                timestamp=datetime.utcnow().isoformat(),
                success=False
            )

        # Build prompt for Claude
        prompt = self._build_resolution_prompt(conflict)

        try:
            # Call Claude API
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse response
            result = self._parse_claude_response(response.content[0].text)

            return ResolutionResult(
                file_path=conflict.file_path,
                tier=ResolutionTier.LLM_ASSISTED,
                conflict_type=conflict.conflict_type,
                confidence=result['confidence'],
                resolved_content=result['resolved_content'],
                reasoning=result['reasoning'],
                timestamp=datetime.utcnow().isoformat(),
                success=True
            )

        except Exception as e:
            return ResolutionResult(
                file_path=conflict.file_path,
                tier=ResolutionTier.LLM_ASSISTED,
                conflict_type=conflict.conflict_type,
                confidence=0.0,
                resolved_content=None,
                reasoning=f"LLM error: {str(e)}",
                timestamp=datetime.utcnow().isoformat(),
                success=False,
                error=str(e)
            )

    def _build_resolution_prompt(self, conflict: ConflictMarkers) -> str:
        """Build prompt for Claude"""
        head_content = ''.join(conflict.head_content)
        incoming_content = ''.join(conflict.incoming_content)

        return f"""You are an expert Git merge conflict resolver. Analyze this conflict and provide a resolution.

File: {conflict.file_path}
Conflict Type: {conflict.conflict_type.value}

HEAD version:
```
{head_content}```

Incoming version:
```
{incoming_content}```

Please provide:
1. Resolved content (the merged result)
2. Confidence score (0.0-1.0)
3. Reasoning (brief explanation)

Respond in this JSON format:
{{
  "resolved_content": "...",
  "confidence": 0.85,
  "reasoning": "..."
}}

Guidelines:
- For non-overlapping sections, keep both
- For semantic conflicts, choose the version that preserves both intents
- For logic conflicts, score confidence < 0.70 to defer to human
- Never remove functionality unless clearly superseded
"""

    def _parse_claude_response(self, response_text: str) -> Dict:
        """Parse Claude's JSON response"""
        try:
            # Extract JSON from markdown code blocks if present
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                # Try to find JSON directly
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                json_text = json_match.group(0) if json_match else response_text

            result = json.loads(json_text)

            # Validate required fields
            if 'resolved_content' not in result:
                raise ValueError("Missing resolved_content")
            if 'confidence' not in result:
                result['confidence'] = 0.70
            if 'reasoning' not in result:
                result['reasoning'] = "LLM resolution"

            return result

        except Exception as e:
            print(f"Error parsing Claude response: {e}")
            print(f"Response text: {response_text}")
            raise


class ConflictResolver:
    """Main conflict resolution orchestrator"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize resolver"""
        self.api_key = api_key
        self.llm_merger = None
        self.audit_trail = []

    def resolve_file(self, file_path: str) -> List[ResolutionResult]:
        """Resolve all conflicts in a file"""
        results = []

        # Find conflicts
        conflicts = ConflictParser.find_conflicts(file_path)

        if not conflicts:
            print(f"No conflicts found in {file_path}")
            return results

        print(f"Found {len(conflicts)} conflict(s) in {file_path}")

        # Resolve each conflict
        for i, conflict in enumerate(conflicts):
            print(f"\nResolving conflict {i+1}/{len(conflicts)}...")
            result = self._resolve_single_conflict(conflict)
            results.append(result)
            self.audit_trail.append(result.to_dict())

            print(f"  Tier: {result.tier.value}")
            print(f"  Confidence: {result.confidence:.2f}")
            print(f"  Success: {result.success}")

        return results

    def _resolve_single_conflict(self, conflict: ConflictMarkers) -> ResolutionResult:
        """Resolve a single conflict using the three-tier strategy"""

        # Try Tier 1: Safe auto-merge
        result = SafeAutoMerger.resolve(conflict)
        if result.success and result.confidence >= 0.70:
            return result

        # Try Tier 2: LLM-assisted
        if self.api_key:
            if not self.llm_merger:
                self.llm_merger = LLMAssistedMerger(self.api_key)

            result = self.llm_merger.resolve(conflict)
            if result.success and result.confidence >= 0.70:
                return result

        # Tier 3: Defer to human
        return ResolutionResult(
            file_path=conflict.file_path,
            tier=ResolutionTier.HUMAN_REVIEW,
            conflict_type=conflict.conflict_type,
            confidence=0.0,
            resolved_content=None,
            reasoning="Requires human review - confidence too low or high-risk file",
            timestamp=datetime.utcnow().isoformat(),
            success=False
        )

    def apply_resolutions(
        self,
        file_path: str,
        results: List[ResolutionResult]
    ) -> bool:
        """Apply resolved conflicts to file"""

        # Check if all resolutions successful
        if not all(r.success for r in results):
            print("Not all conflicts resolved - skipping apply")
            return False

        # Read original file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading file: {e}")
            return False

        # Create backup
        backup_path = f"{file_path}.backup"
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False

        # Find and replace conflicts
        conflicts = ConflictParser.find_conflicts(file_path)

        # Apply resolutions in reverse order (to preserve line numbers)
        for conflict, result in reversed(list(zip(conflicts, results))):
            # Replace conflict markers with resolved content
            lines[conflict.start_line:conflict.end_line + 1] = [result.resolved_content]

        # Write resolved file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"Applied resolutions to {file_path}")
            print(f"Backup saved to {backup_path}")
            return True
        except Exception as e:
            print(f"Error writing resolved file: {e}")
            # Restore from backup
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_lines = f.readlines()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(backup_lines)
            return False

    def save_audit_trail(self, output_path: str = "auto-merge-audit.json"):
        """Save audit trail to JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.audit_trail, f, indent=2)
            print(f"\nAudit trail saved to {output_path}")
        except Exception as e:
            print(f"Error saving audit trail: {e}")


def find_conflicted_files() -> List[str]:
    """Find all files with merge conflicts"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', '--diff-filter=U'],
            capture_output=True,
            text=True,
            check=True
        )
        files = result.stdout.strip().split('\n')
        return [f for f in files if f]
    except subprocess.CalledProcessError as e:
        print(f"Error finding conflicted files: {e}")
        return []


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='AI-Powered Auto-Merge Conflict Resolution'
    )
    parser.add_argument(
        '--file',
        help='Specific file to resolve (default: all conflicted files)'
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Apply resolutions to files'
    )
    parser.add_argument(
        '--api-key',
        help='Anthropic API key (default: ANTHROPIC_API_KEY env var)'
    )
    parser.add_argument(
        '--audit',
        default='auto-merge-audit.json',
        help='Audit trail output path'
    )

    args = parser.parse_args()

    # Find files to resolve
    if args.file:
        files = [args.file]
    else:
        files = find_conflicted_files()

    if not files:
        print("No conflicted files found")
        return 0

    print(f"Found {len(files)} conflicted file(s)")

    # Initialize resolver
    resolver = ConflictResolver(api_key=args.api_key)

    # Resolve each file
    all_success = True
    for file_path in files:
        print(f"\n{'='*60}")
        print(f"Resolving: {file_path}")
        print('='*60)

        results = resolver.resolve_file(file_path)

        if args.apply:
            success = resolver.apply_resolutions(file_path, results)
            if not success:
                all_success = False

    # Save audit trail
    resolver.save_audit_trail(args.audit)

    return 0 if all_success else 1


if __name__ == '__main__':
    sys.exit(main())
