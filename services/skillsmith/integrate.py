#!/usr/bin/env python3
"""
Skillsmith Integration Orchestrator
Ties together: error mining, knowledge agent, RL feedback, training dataset, error catalog
"""
import os
import sys
import json
import logging
import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class SkillsmithIntegration:
    """Orchestrates integration between Skillsmith and existing AI/ML pipeline"""

    def __init__(self):
        self.repo_root = Path(__file__).parent.parent.parent
        self.skills_proposed = self.repo_root / "skills" / "proposed"
        self.skills_approved = self.repo_root / "skills"
        self.trm_dataset = self.repo_root / "datasets" / "trm" / "erp_tasks.jsonl"
        self.error_catalog = self.repo_root / "docs" / "error-codes.yaml"
        self.integration_log = self.repo_root / "logs" / "skillsmith-integration.jsonl"

        # Ensure directories exist
        self.trm_dataset.parent.mkdir(parents=True, exist_ok=True)
        self.integration_log.parent.mkdir(parents=True, exist_ok=True)

    def run_full_pipeline(self):
        """Run complete integration pipeline"""
        logger.info("=" * 60)
        logger.info("Starting Skillsmith Integration Pipeline")
        logger.info("=" * 60)

        results = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "steps": []
        }

        try:
            # Step 1: Enrich proposals with forum knowledge
            logger.info("\n[1/5] Enriching proposals with forum knowledge...")
            forum_result = self.enrich_with_forum_knowledge()
            results["steps"].append({"step": "forum_enrichment", "result": forum_result})

            # Step 2: Update confidence from error rates
            logger.info("\n[2/5] Updating confidence scores from outcomes...")
            confidence_result = self.update_confidence_scores()
            results["steps"].append({"step": "confidence_update", "result": confidence_result})

            # Step 3: Sync approved skills to TRM dataset
            logger.info("\n[3/5] Syncing approved skills to training dataset...")
            trm_result = self.sync_to_trm_dataset()
            results["steps"].append({"step": "trm_sync", "result": trm_result})

            # Step 4: Update error catalog
            logger.info("\n[4/5] Updating error catalog with live data...")
            catalog_result = self.update_error_catalog()
            results["steps"].append({"step": "catalog_update", "result": catalog_result})

            # Step 5: Check if retrain needed
            logger.info("\n[5/5] Checking if retraining needed...")
            retrain_result = self.check_retrain_needed()
            results["steps"].append({"step": "retrain_check", "result": retrain_result})

            results["status"] = "success"
            logger.info("\n✅ Integration pipeline completed successfully")

        except Exception as e:
            logger.error(f"\n❌ Integration pipeline failed: {e}", exc_info=True)
            results["status"] = "failed"
            results["error"] = str(e)

        # Log results
        self._log_integration(results)
        return results

    def enrich_with_forum_knowledge(self) -> Dict:
        """Enrich skill proposals with Odoo forum knowledge"""
        try:
            from services.skillsmith.forum_enrichment import enrich_proposals
            return enrich_proposals(self.skills_proposed)
        except ImportError:
            logger.warning("Forum enrichment module not found, skipping")
            return {"skipped": True, "reason": "module_not_found"}
        except Exception as e:
            logger.error(f"Forum enrichment failed: {e}")
            return {"error": str(e)}

    def update_confidence_scores(self) -> Dict:
        """Update skill confidence from error rate outcomes"""
        try:
            from services.skillsmith.feedback_loop import update_confidence_from_outcomes
            return update_confidence_from_outcomes()
        except ImportError:
            logger.warning("Feedback loop module not found, skipping")
            return {"skipped": True, "reason": "module_not_found"}
        except Exception as e:
            logger.error(f"Confidence update failed: {e}")
            return {"error": str(e)}

    def sync_to_trm_dataset(self) -> Dict:
        """Sync approved skills to TRM training dataset"""
        try:
            from services.skillsmith.trm_sync import sync_approved_skills
            return sync_approved_skills(self.skills_approved, self.trm_dataset)
        except ImportError:
            logger.warning("TRM sync module not found, skipping")
            return {"skipped": True, "reason": "module_not_found"}
        except Exception as e:
            logger.error(f"TRM sync failed: {e}")
            return {"error": str(e)}

    def update_error_catalog(self) -> Dict:
        """Update error catalog with live production data"""
        try:
            from services.skillsmith.sync_catalog import sync_error_catalog
            return sync_error_catalog(self.error_catalog)
        except ImportError:
            logger.warning("Catalog sync module not found, skipping")
            return {"skipped": True, "reason": "module_not_found"}
        except Exception as e:
            logger.error(f"Catalog sync failed: {e}")
            return {"error": str(e)}

    def check_retrain_needed(self) -> Dict:
        """Check if model retraining is needed"""
        # Check if significant changes warrant retraining
        threshold = 10  # Retrain if 10+ new skills approved

        if not self.trm_dataset.exists():
            return {"retrain_needed": False, "reason": "no_dataset"}

        try:
            # Count recent additions
            recent_count = 0
            cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=7)

            with self.trm_dataset.open() as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if "approved_at" in entry:
                            approved_at = datetime.datetime.fromisoformat(
                                entry["approved_at"].replace("Z", "+00:00")
                            )
                            if approved_at > cutoff:
                                recent_count += 1
                    except:
                        continue

            retrain_needed = recent_count >= threshold

            return {
                "retrain_needed": retrain_needed,
                "recent_additions": recent_count,
                "threshold": threshold,
                "recommendation": "Run 'make retrain' to update model" if retrain_needed else "No retrain needed yet"
            }
        except Exception as e:
            logger.error(f"Retrain check failed: {e}")
            return {"error": str(e)}

    def _log_integration(self, results: Dict):
        """Log integration run to JSONL"""
        try:
            with self.integration_log.open('a') as f:
                f.write(json.dumps(results) + '\n')
        except Exception as e:
            logger.error(f"Failed to log integration results: {e}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Skillsmith Integration Pipeline")
    parser.add_argument("--step", choices=["forum", "confidence", "trm", "catalog", "retrain"],
                       help="Run specific step only")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    args = parser.parse_args()

    integration = SkillsmithIntegration()

    if args.step:
        # Run specific step
        step_map = {
            "forum": integration.enrich_with_forum_knowledge,
            "confidence": integration.update_confidence_scores,
            "trm": integration.sync_to_trm_dataset,
            "catalog": integration.update_error_catalog,
            "retrain": integration.check_retrain_needed
        }
        result = step_map[args.step]()
        print(json.dumps(result, indent=2))
    else:
        # Run full pipeline
        result = integration.run_full_pipeline()

        # Print summary
        print("\n" + "=" * 60)
        print("Integration Summary")
        print("=" * 60)
        print(f"Status: {result['status']}")
        print(f"Timestamp: {result['timestamp']}")
        print(f"\nSteps completed: {len(result['steps'])}")

        for step in result['steps']:
            status = "✅" if not step['result'].get('error') else "❌"
            print(f"  {status} {step['step']}")

        if result.get('status') == 'success':
            # Check retrain recommendation
            for step in result['steps']:
                if step['step'] == 'retrain_check':
                    if step['result'].get('retrain_needed'):
                        print(f"\n⚠️  {step['result']['recommendation']}")
                    break

        sys.exit(0 if result['status'] == 'success' else 1)


if __name__ == "__main__":
    main()
