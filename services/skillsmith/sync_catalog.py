#!/usr/bin/env python3
"""
Error Catalog Auto-Sync
Updates error catalog with live production data from error_signatures
"""
import os
import yaml
import psycopg
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List
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


class ErrorCatalogSync:
    """Syncs error catalog with live production patterns"""

    def __init__(self, catalog_path: Path):
        self.catalog_path = catalog_path
        self.catalog_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize catalog if doesn't exist
        if not self.catalog_path.exists():
            self._init_catalog()

    def sync_error_catalog(self) -> Dict:
        """Main sync operation"""
        logger.info("Syncing error catalog with production data...")

        results = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "updated": [],
            "added": [],
            "stats": {}
        }

        try:
            # Load current catalog
            catalog = self._load_catalog()

            # Get live error data
            error_data = self._get_live_error_data()

            if not error_data:
                logger.warning("No live error data available")
                return {"warning": "no_data"}

            # Get active skills
            skills_map = self._get_active_skills()

            # Update catalog entries
            for sig in error_data:
                code = self._get_or_create_error_code(catalog, sig)

                update_info = self._update_catalog_entry(
                    catalog, code, sig, skills_map
                )

                if update_info["created"]:
                    results["added"].append(code)
                else:
                    results["updated"].append(code)

            # Calculate stats
            results["stats"] = self._calculate_stats(catalog, error_data)

            # Save updated catalog
            self._save_catalog(catalog)

            logger.info(f"✅ Updated {len(results['updated'])} entries")
            logger.info(f"   Added {len(results['added'])} new entries")

        except Exception as e:
            logger.error(f"Catalog sync failed: {e}", exc_info=True)
            return {"error": str(e)}

        return results

    def _init_catalog(self):
        """Initialize empty catalog"""
        initial_catalog = {
            "metadata": {
                "title": "Odoo Error Catalog - Production",
                "description": "Auto-synced from Skillsmith error signatures",
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "version": "1.0.0"
            },
            "categories": {
                "database": "Database errors (SQL, ORM, constraints)",
                "validation": "Data validation errors",
                "permission": "Access control and permissions",
                "integration": "External integrations and APIs",
                "business_logic": "Business rule violations",
                "system": "System-level errors"
            },
            "errors": {}
        }

        self._save_catalog(initial_catalog)

    def _load_catalog(self) -> Dict:
        """Load error catalog YAML"""
        with self.catalog_path.open() as f:
            return yaml.safe_load(f)

    def _save_catalog(self, catalog: Dict):
        """Save error catalog YAML"""
        # Update metadata timestamp
        catalog["metadata"]["last_updated"] = datetime.utcnow().isoformat() + "Z"

        with self.catalog_path.open('w') as f:
            yaml.safe_dump(catalog, f, default_flow_style=False, sort_keys=False)

    def _get_live_error_data(self) -> List[Dict]:
        """Fetch live error signatures from database"""
        if not all(DB_CONFIG.values()):
            logger.warning("Database config incomplete")
            return []

        try:
            with psycopg.connect(**DB_CONFIG, row_factory=dict_row) as conn:
                with conn.cursor() as cur:
                    # Refresh materialized view
                    cur.execute("REFRESH MATERIALIZED VIEW public.error_signatures;")
                    conn.commit()

                    # Get top signatures
                    cur.execute("""
                        SELECT fp, component, kind, norm_msg, hits_7d, hits_30d, tags
                        FROM public.error_signatures
                        WHERE hits_7d > 0
                        ORDER BY (hits_7d * 0.7 + hits_30d * 0.3) DESC
                        LIMIT 100
                    """)

                    return cur.fetchall()

        except Exception as e:
            logger.error(f"Failed to fetch live data: {e}")
            raise

    def _get_active_skills(self) -> Dict[str, Dict]:
        """Get mapping of fingerprint → skill"""
        skills_map = {}

        repo_root = Path(__file__).parent.parent.parent
        skills_dir = repo_root / "skills"

        for yaml_file in skills_dir.glob("*.yaml"):
            try:
                with yaml_file.open() as f:
                    skill = yaml.safe_load(f)

                if skill and skill.get("status") == "approved":
                    fp = skill.get("match", {}).get("fingerprint")
                    if fp:
                        skills_map[fp] = {
                            "id": skill.get("id"),
                            "name": skill.get("name"),
                            "kind": skill.get("kind"),
                            "confidence": skill.get("metadata", {}).get("confidence", 0.5)
                        }
            except Exception as e:
                logger.warning(f"Failed to load skill {yaml_file.name}: {e}")

        return skills_map

    def _get_or_create_error_code(self, catalog: Dict, sig: Dict) -> str:
        """Get existing error code or generate new one"""
        # Try to find existing by fingerprint
        for code, entry in catalog.get("errors", {}).items():
            if entry.get("fingerprint") == str(sig['fp']):
                return code

        # Generate new code
        kind = sig['kind']
        category = self._classify_error(kind, sig['component'])

        # Count existing codes in this category
        prefix_map = {
            "database": "DB",
            "validation": "VAL",
            "permission": "PERM",
            "integration": "INT",
            "business_logic": "BIZ",
            "system": "SYS"
        }

        prefix = prefix_map.get(category, "ERR")

        # Find next number
        existing_nums = [
            int(code.split('-')[1])
            for code in catalog.get("errors", {}).keys()
            if code.startswith(prefix + '-') and code.split('-')[1].isdigit()
        ]

        next_num = max(existing_nums, default=0) + 1

        return f"{prefix}-{next_num:03d}"

    def _classify_error(self, kind: str, component: str) -> str:
        """Classify error into category"""
        kind_lower = kind.lower()
        component_lower = component.lower()

        if "sql" in kind_lower or "integrity" in kind_lower or "orm" in component_lower:
            return "database"
        elif "permission" in kind_lower or "access" in kind_lower or "forbidden" in kind_lower:
            return "permission"
        elif "validation" in kind_lower or "value" in kind_lower:
            return "validation"
        elif "api" in component_lower or "request" in kind_lower:
            return "integration"
        elif "import" in kind_lower or "module" in kind_lower:
            return "system"
        else:
            return "business_logic"

    def _update_catalog_entry(self, catalog: Dict, code: str,
                              sig: Dict, skills_map: Dict) -> Dict:
        """Update or create catalog entry"""
        if "errors" not in catalog:
            catalog["errors"] = {}

        created = code not in catalog["errors"]

        if created:
            # Create new entry
            catalog["errors"][code] = {
                "title": f"{sig['kind']} in {sig['component']}",
                "description": sig['norm_msg'][:200],
                "category": self._classify_error(sig['kind'], sig['component']),
                "severity": self._calculate_severity(sig),
                "first_seen": datetime.utcnow().isoformat() + "Z"
            }

        entry = catalog["errors"][code]

        # Update live stats
        entry["live_stats"] = {
            "hits_7d": sig['hits_7d'],
            "hits_30d": sig['hits_30d'],
            "last_seen": datetime.utcnow().isoformat() + "Z",
            "trend": "increasing" if sig['hits_7d'] > sig['hits_30d'] / 4 else "stable"
        }

        # Link to skills
        fp_str = str(sig['fp'])
        if fp_str in skills_map:
            skill = skills_map[fp_str]
            entry["active_guardrails"] = [{
                "skill_id": skill["id"],
                "name": skill["name"],
                "kind": skill["kind"],
                "confidence": skill["confidence"]
            }]
        else:
            entry["active_guardrails"] = []

        # Update fingerprint
        entry["fingerprint"] = str(sig['fp'])

        # Add example
        entry["example"] = sig['norm_msg']

        # Add tags
        entry["tags"] = sig.get('tags', [])

        return {"created": created, "code": code}

    def _calculate_severity(self, sig: Dict) -> str:
        """Calculate error severity"""
        hits_7d = sig['hits_7d']

        if hits_7d >= 20:
            return "critical"
        elif hits_7d >= 10:
            return "high"
        elif hits_7d >= 5:
            return "medium"
        else:
            return "low"

    def _calculate_stats(self, catalog: Dict, error_data: List[Dict]) -> Dict:
        """Calculate catalog statistics"""
        return {
            "total_errors": len(catalog.get("errors", {})),
            "active_patterns": len(error_data),
            "by_severity": self._count_by_severity(catalog),
            "by_category": self._count_by_category(catalog),
            "coverage": self._calculate_coverage(catalog)
        }

    def _count_by_severity(self, catalog: Dict) -> Dict:
        """Count errors by severity"""
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for entry in catalog.get("errors", {}).values():
            severity = entry.get("severity", "low")
            counts[severity] = counts.get(severity, 0) + 1
        return counts

    def _count_by_category(self, catalog: Dict) -> Dict:
        """Count errors by category"""
        counts = {}
        for entry in catalog.get("errors", {}).values():
            category = entry.get("category", "unknown")
            counts[category] = counts.get(category, 0) + 1
        return counts

    def _calculate_coverage(self, catalog: Dict) -> Dict:
        """Calculate guardrail coverage"""
        total = len(catalog.get("errors", {}))
        covered = sum(
            1 for entry in catalog.get("errors", {}).values()
            if entry.get("active_guardrails")
        )

        return {
            "total_errors": total,
            "covered_by_skills": covered,
            "coverage_pct": round((covered / total * 100) if total > 0 else 0, 1)
        }


def sync_error_catalog(catalog_path: Path) -> Dict:
    """Main entry point for integration"""
    syncer = ErrorCatalogSync(catalog_path)
    return syncer.sync_error_catalog()


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    repo_root = Path(__file__).parent.parent.parent
    catalog_path = repo_root / "docs" / "error-codes.yaml"

    result = sync_error_catalog(catalog_path)
    print(yaml.dump(result, default_flow_style=False))
