#!/usr/bin/env python3
"""
Skillsmith Feedback Loop
Auto-updates skill confidence based on error rate outcomes
"""
import os
import json
import yaml
import psycopg
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from psycopg.rows import dict_row

logger = logging.getLogger(__name__)

# Database config
DB_CONFIG = {
    'host': os.getenv('SUPABASE_DB_HOST'),
    'dbname': os.getenv('SUPABASE_DB_NAME'),
    'user': os.getenv('SUPABASE_DB_USER'),
    'password': os.getenv('SUPABASE_DB_PASSWORD'),
    'port': os.getenv('SUPABASE_DB_PORT', '5432'),
}


class ConfidenceUpdater:
    """Updates skill confidence based on real-world outcomes"""

    def __init__(self):
        self.repo_root = Path(__file__).parent.parent.parent
        self.skills_dir = self.repo_root / "skills"
        self.confidence_log = self.repo_root / "logs" / "confidence-updates.jsonl"
        self.confidence_log.parent.mkdir(parents=True, exist_ok=True)

    def update_confidence_from_outcomes(self) -> Dict:
        """Main entry point: update all approved skills"""
        logger.info("Updating skill confidence from error rate outcomes...")

        results = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "updated_skills": [],
            "stats": {
                "boosted": 0,
                "reduced": 0,
                "unchanged": 0,
                "errors": 0
            }
        }

        # Get all approved skills
        approved_skills = self._get_approved_skills()
        logger.info(f"Found {len(approved_skills)} approved skills")

        # Get current error signatures
        try:
            error_data = self._get_error_signatures()
        except Exception as e:
            logger.error(f"Failed to fetch error signatures: {e}")
            return {"error": str(e)}

        # Update each skill
        for skill_file, skill_data in approved_skills.items():
            try:
                update = self._calculate_confidence_update(skill_data, error_data)

                if update["action"] != "unchanged":
                    # Update YAML file
                    self._update_skill_yaml(skill_file, skill_data, update)

                    results["updated_skills"].append({
                        "skill_id": skill_data.get("id"),
                        "file": str(skill_file.name),
                        "action": update["action"],
                        "old_confidence": update["old_confidence"],
                        "new_confidence": update["new_confidence"],
                        "reason": update["reason"]
                    })

                results["stats"][update["action"]] += 1

            except Exception as e:
                logger.error(f"Failed to update {skill_file.name}: {e}")
                results["stats"]["errors"] += 1

        # Log results
        self._log_update(results)

        logger.info(f"✅ Updated {len(results['updated_skills'])} skills")
        logger.info(f"   Boosted: {results['stats']['boosted']}")
        logger.info(f"   Reduced: {results['stats']['reduced']}")
        logger.info(f"   Unchanged: {results['stats']['unchanged']}")

        return results

    def _get_approved_skills(self) -> Dict[Path, Dict]:
        """Get all approved skills from skills/ directory"""
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

    def _get_error_signatures(self) -> Dict:
        """Fetch current error signatures from database"""
        if not all(DB_CONFIG.values()):
            logger.warning("Database config incomplete, returning empty data")
            return {}

        try:
            with psycopg.connect(**DB_CONFIG, row_factory=dict_row) as conn:
                with conn.cursor() as cur:
                    # Refresh materialized view
                    cur.execute("REFRESH MATERIALIZED VIEW public.error_signatures;")
                    conn.commit()

                    # Get all signatures
                    cur.execute("""
                        SELECT fp, component, kind, norm_msg, hits_7d, hits_30d
                        FROM public.error_signatures
                    """)
                    rows = cur.fetchall()

                    # Index by fingerprint
                    return {str(row['fp']): row for row in rows}

        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise

    def _calculate_confidence_update(self, skill: Dict, error_data: Dict) -> Dict:
        """Calculate new confidence based on error rate changes"""
        fingerprint = skill.get("match", {}).get("fingerprint")
        current_confidence = skill.get("metadata", {}).get("confidence", 0.5)

        if not fingerprint or fingerprint not in error_data:
            return {
                "action": "unchanged",
                "old_confidence": current_confidence,
                "new_confidence": current_confidence,
                "reason": "no_data"
            }

        sig = error_data[fingerprint]
        hits_7d = sig['hits_7d']
        hits_30d = sig['hits_30d']

        # Calculate baseline (what we'd expect without intervention)
        # Assume 30d rate should continue into 7d window
        expected_7d = hits_30d * (7 / 30)

        # Calculate impact
        if expected_7d == 0:
            impact_ratio = 1.0
        else:
            impact_ratio = hits_7d / expected_7d

        # Update confidence based on impact
        # - If errors reduced significantly (ratio < 0.5): boost confidence
        # - If errors unchanged or increased (ratio > 0.9): reduce confidence
        # - Otherwise: leave unchanged

        new_confidence = current_confidence

        if impact_ratio < 0.3:
            # Excellent: 70%+ reduction
            new_confidence = min(1.0, current_confidence * 1.3)
            action = "boosted"
            reason = f"error_reduced_by_{int((1-impact_ratio)*100)}%"

        elif impact_ratio < 0.5:
            # Good: 50%+ reduction
            new_confidence = min(1.0, current_confidence * 1.15)
            action = "boosted"
            reason = f"error_reduced_by_{int((1-impact_ratio)*100)}%"

        elif impact_ratio > 1.5:
            # Poor: errors increased
            new_confidence = max(0.1, current_confidence * 0.8)
            action = "reduced"
            reason = f"error_increased_by_{int((impact_ratio-1)*100)}%"

        elif impact_ratio > 0.9:
            # Marginal: little impact
            new_confidence = max(0.1, current_confidence * 0.95)
            action = "reduced"
            reason = "minimal_impact"

        else:
            # Moderate impact: leave unchanged
            action = "unchanged"
            reason = "moderate_impact"

        return {
            "action": action,
            "old_confidence": round(current_confidence, 3),
            "new_confidence": round(new_confidence, 3),
            "reason": reason,
            "hits_7d": hits_7d,
            "hits_30d": hits_30d,
            "expected_7d": round(expected_7d, 1),
            "impact_ratio": round(impact_ratio, 2)
        }

    def _update_skill_yaml(self, skill_file: Path, skill_data: Dict, update: Dict):
        """Update skill YAML file with new confidence"""
        # Ensure metadata section exists
        if "metadata" not in skill_data:
            skill_data["metadata"] = {}

        # Update confidence
        skill_data["metadata"]["confidence"] = update["new_confidence"]

        # Add update history
        if "confidence_history" not in skill_data["metadata"]:
            skill_data["metadata"]["confidence_history"] = []

        skill_data["metadata"]["confidence_history"].append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "old": update["old_confidence"],
            "new": update["new_confidence"],
            "reason": update["reason"],
            "hits_7d": update.get("hits_7d"),
            "impact_ratio": update.get("impact_ratio")
        })

        # Keep only last 10 history entries
        skill_data["metadata"]["confidence_history"] = \
            skill_data["metadata"]["confidence_history"][-10:]

        # Update last_updated
        skill_data["metadata"]["last_updated"] = datetime.utcnow().isoformat() + "Z"

        # Write back to file
        with skill_file.open('w') as f:
            yaml.safe_dump(skill_data, f, default_flow_style=False, sort_keys=False)

    def _log_update(self, results: Dict):
        """Log confidence updates"""
        try:
            with self.confidence_log.open('a') as f:
                f.write(json.dumps(results) + '\n')
        except Exception as e:
            logger.error(f"Failed to log confidence update: {e}")


def update_confidence_from_outcomes() -> Dict:
    """Main entry point for integration"""
    updater = ConfidenceUpdater()
    return updater.update_confidence_from_outcomes()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    result = update_confidence_from_outcomes()
    print(json.dumps(result, indent=2))
