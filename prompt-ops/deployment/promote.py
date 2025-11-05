#!/usr/bin/env python3
"""
Prompt Promotion Tool
---------------------
Promotes prompts from canary -> staging -> prod with validation
"""
import argparse
import yaml
import sys
from pathlib import Path
from typing import Dict, Any


def load_catalog(path: Path) -> Dict[str, Any]:
    """Load prompt registry catalog"""
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def save_catalog(catalog: Dict[str, Any], path: Path):
    """Save updated catalog"""
    with open(path, 'w') as f:
        yaml.dump(catalog, f, default_flow_style=False, sort_keys=False)


def find_prompt(catalog: Dict[str, Any], prompt_id: str) -> Dict[str, Any]:
    """Find prompt by ID"""
    for prompt in catalog['prompts']:
        if prompt['id'] == prompt_id:
            return prompt
    return None


def get_next_ring(current_ring: str) -> str:
    """Get next rollout ring"""
    ring_order = ['ring-1', 'ring-2', 'prod']
    if current_ring in ring_order:
        idx = ring_order.index(current_ring)
        if idx < len(ring_order) - 1:
            return ring_order[idx + 1]
    return None


def promote_prompt(prompt_id: str, target_ring: str, catalog_path: Path) -> bool:
    """Promote prompt to target ring"""
    catalog = load_catalog(catalog_path)

    prompt = find_prompt(catalog, prompt_id)
    if not prompt:
        print(f"❌ Prompt '{prompt_id}' not found in catalog")
        return False

    current_ring = prompt['rollout']
    print(f"Current ring: {current_ring}")
    print(f"Target ring:  {target_ring}")

    # Validate promotion path
    if target_ring == 'prod' and current_ring not in ['ring-2', 'prod']:
        print(f"❌ Cannot promote from {current_ring} directly to prod")
        print("   Must go through ring-2 first")
        return False

    # Update catalog
    prompt['rollout'] = target_ring
    save_catalog(catalog, catalog_path)

    print(f"✅ Promoted '{prompt_id}' to {target_ring}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Promote prompt to next ring")
    parser.add_argument('--id', required=True, help="Prompt ID")
    parser.add_argument('--to', required=True, choices=['ring-1', 'ring-2', 'prod'], help="Target ring")
    parser.add_argument('--catalog', type=Path, default=Path('prompt-ops/registry/catalog.yml'), help="Catalog path")

    args = parser.parse_args()

    success = promote_prompt(args.id, args.to, args.catalog)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
