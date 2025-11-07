#!/usr/bin/env python3
"""
TRM Dataset Sync
Syncs approved Skillsmith skills to the training dataset for small LLM
"""
import json
import yaml
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class TRMDatasetSync:
    """Syncs approved skills to TRM (Task Retrieval & Mastery) training dataset"""

    def __init__(self, skills_dir: Path, trm_dataset: Path):
        self.skills_dir = skills_dir
        self.trm_dataset = trm_dataset
        self.trm_dataset.parent.mkdir(parents=True, exist_ok=True)

        # Track what's already in dataset to avoid duplicates
        self.existing_fingerprints = self._load_existing_fingerprints()

    def sync_approved_skills(self) -> Dict:
        """Sync all approved skills to TRM dataset"""
        logger.info("Syncing approved skills to TRM dataset...")

        results = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "added": [],
            "skipped": [],
            "errors": []
        }

        # Get all approved skills
        approved_skills = self._get_approved_skills()
        logger.info(f"Found {len(approved_skills)} approved skills")

        # Convert each to training example
        for skill_file, skill_data in approved_skills.items():
            try:
                fingerprint = skill_data.get("match", {}).get("fingerprint")

                # Skip if already in dataset
                if fingerprint in self.existing_fingerprints:
                    results["skipped"].append({
                        "skill_id": skill_data.get("id"),
                        "reason": "already_in_dataset"
                    })
                    continue

                # Convert to training example
                training_example = self._skill_to_training_example(skill_data)

                # Append to dataset
                self._append_to_dataset(training_example)

                # Track as added
                self.existing_fingerprints.add(fingerprint)
                results["added"].append({
                    "skill_id": skill_data.get("id"),
                    "fingerprint": fingerprint
                })

            except Exception as e:
                logger.error(f"Failed to sync {skill_file.name}: {e}")
                results["errors"].append({
                    "skill_id": skill_data.get("id"),
                    "error": str(e)
                })

        logger.info(f"✅ Added {len(results['added'])} new training examples")
        logger.info(f"   Skipped {len(results['skipped'])} (already in dataset)")
        logger.info(f"   Errors: {len(results['errors'])}")

        return results

    def _get_approved_skills(self) -> Dict[Path, Dict]:
        """Get all approved skills"""
        skills = {}

        for yaml_file in self.skills_dir.glob("*.yaml"):
            try:
                with yaml_file.open() as f:
                    data = yaml.safe_load(f)

                if data and data.get("status") == "approved":
                    skills[yaml_file] = data
            except Exception as e:
                logger.warning(f"Failed to load {yaml_file.name}: {e}")

        return skills

    def _load_existing_fingerprints(self) -> Set[str]:
        """Load fingerprints of skills already in dataset"""
        fingerprints = set()

        if not self.trm_dataset.exists():
            return fingerprints

        try:
            with self.trm_dataset.open() as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if "fingerprint" in entry:
                            fingerprints.add(entry["fingerprint"])
                    except:
                        continue
        except Exception as e:
            logger.warning(f"Failed to load existing fingerprints: {e}")

        return fingerprints

    def _skill_to_training_example(self, skill: Dict) -> Dict:
        """Convert skill to training dataset format"""
        kind = skill.get("kind", "unknown")
        skill_id = skill.get("id", "unknown")
        name = skill.get("name", "Unknown Error")

        # Base example
        example = {
            "id": skill_id,
            "source": "skillsmith-production",
            "kind": kind,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # Extract metadata
        metadata = skill.get("metadata", {})
        match = skill.get("match", {})
        action = skill.get("action", {})

        if kind == "guardrail":
            # Guardrail: teach model to prevent this error
            example.update({
                "task": f"prevent_{name.lower().replace(' ', '_')}",
                "input": {
                    "error_pattern": match.get("message_regex"),
                    "component": match.get("component"),
                    "context": "pre_execution_check"
                },
                "output": {
                    "action": "block",
                    "message": action.get("message"),
                    "suggest_fix": action.get("suggest_fix", True)
                },
                "description": f"Prevent {name} by validating input before execution",
            })

        elif kind == "fixer":
            # Fixer: teach model to auto-fix this error
            example.update({
                "task": f"fix_{name.lower().replace(' ', '_')}",
                "input": {
                    "error_pattern": match.get("message_regex"),
                    "component": match.get("component"),
                    "context": "post_error_recovery"
                },
                "output": {
                    "action": "autopatch",
                    "script": action.get("script"),
                    "dry_run": action.get("dry_run", True)
                },
                "description": f"Automatically fix {name} using patch script",
            })

        # Add metrics for quality assessment
        example["metrics"] = {
            "hits_7d": metadata.get("hits_7d", 0),
            "hits_30d": metadata.get("hits_30d", 0),
            "impact_score": metadata.get("impact_score", 0),
            "confidence": metadata.get("confidence", 0.5),
        }

        # Add fingerprint for deduplication
        example["fingerprint"] = match.get("fingerprint")

        # Add tags for retrieval
        example["tags"] = self._generate_tags(skill)

        return example

    def _generate_tags(self, skill: Dict) -> List[str]:
        """Generate searchable tags for the training example"""
        tags = []

        # Kind
        tags.append(skill.get("kind", "unknown"))

        # Component parts
        component = skill.get("match", {}).get("component", "")
        if component:
            # Split odoo.addons.sale.models.order → [odoo, addons, sale, models, order]
            tags.extend([p for p in component.split(".") if p])

        # Error type
        name = skill.get("name", "")
        if "KeyError" in name:
            tags.append("keyerror")
        elif "ValueError" in name:
            tags.append("valueerror")
        elif "ImportError" in name:
            tags.append("importerror")

        # Priority
        priority = skill.get("priority", "medium")
        tags.append(f"priority_{priority}")

        # Impact level
        impact_score = skill.get("metadata", {}).get("impact_score", 0)
        if impact_score > 20:
            tags.append("high_impact")
        elif impact_score > 10:
            tags.append("medium_impact")
        else:
            tags.append("low_impact")

        return list(set(tags))  # Deduplicate

    def _append_to_dataset(self, example: Dict):
        """Append training example to JSONL dataset"""
        with self.trm_dataset.open('a') as f:
            f.write(json.dumps(example) + '\n')


def sync_approved_skills(skills_dir: Path, trm_dataset: Path) -> Dict:
    """Main entry point for integration"""
    syncer = TRMDatasetSync(skills_dir, trm_dataset)
    return syncer.sync_approved_skills()


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Defaults
    repo_root = Path(__file__).parent.parent.parent
    skills_dir = repo_root / "skills"
    trm_dataset = repo_root / "datasets" / "trm" / "erp_tasks.jsonl"

    result = sync_approved_skills(skills_dir, trm_dataset)
    print(json.dumps(result, indent=2))
