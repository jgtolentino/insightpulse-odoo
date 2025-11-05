#!/usr/bin/env python3
"""
YAML-Specific Merge Tool

Intelligently merges YAML structures using semantic understanding.

Strategy:
- Lists: merge unique items
- Dicts: recursive merge
- Scalars: prefer ours if changed, else theirs

Usage:
    python yaml-merge.py <base> <ours> <theirs>

This script is designed to be used as a Git merge driver.
Configure in .gitattributes:
    *.yml merge=yaml
    *.yaml merge=yaml

And in .git/config or ~/.gitconfig:
    [merge "yaml"]
        name = YAML semantic merge
        driver = python .github/scripts/yaml-merge.py %O %A %B
"""

import sys
import yaml
from typing import Dict, Any, List, Union
from pathlib import Path


class YAMLMerger:
    """Smart YAML merge that understands structure."""

    def __init__(self):
        self.conflicts = []

    def smart_merge(
        self,
        base: Any,
        ours: Any,
        theirs: Any,
        path: str = ""
    ) -> Any:
        """
        Intelligently merge YAML structures.

        Args:
            base: Common ancestor value
            ours: Our version
            theirs: Their version
            path: Current path in the YAML tree (for error reporting)

        Returns:
            Merged value
        """

        # Both are dicts - merge recursively
        if isinstance(ours, dict) and isinstance(theirs, dict):
            return self.merge_dicts(base or {}, ours, theirs, path)

        # Both are lists - merge intelligently
        elif isinstance(ours, list) and isinstance(theirs, list):
            return self.merge_lists(base or [], ours, theirs, path)

        # Scalars - check who changed it
        else:
            return self.merge_scalars(base, ours, theirs, path)

    def merge_dicts(
        self,
        base: Dict,
        ours: Dict,
        theirs: Dict,
        path: str
    ) -> Dict:
        """
        Merge dictionary structures.

        Strategy:
        - If key exists in both: recurse
        - If key only in one: include it
        - If both changed same key: recurse or use our value
        """
        result = {}

        all_keys = set(ours.keys()) | set(theirs.keys())

        for key in sorted(all_keys):
            key_path = f"{path}.{key}" if path else key

            our_val = ours.get(key)
            their_val = theirs.get(key)
            base_val = base.get(key) if isinstance(base, dict) else None

            if key in ours and key in theirs:
                # Both have the key - recurse
                result[key] = self.smart_merge(base_val, our_val, their_val, key_path)
            elif key in ours:
                # Only we have it - keep ours
                result[key] = our_val
            else:
                # Only they have it - take theirs
                result[key] = their_val

        return result

    def merge_lists(
        self,
        base: List,
        ours: List,
        theirs: List,
        path: str
    ) -> List:
        """
        Merge list structures.

        Strategy:
        1. If items are dicts with 'name' or 'id' keys: merge by identifier
        2. Otherwise: combine unique items (preserve order)
        """

        # Check if list items are dicts with identifiers
        if self.has_identifiable_items(ours) and self.has_identifiable_items(theirs):
            return self.merge_identified_lists(base, ours, theirs, path)
        else:
            return self.merge_simple_lists(base, ours, theirs, path)

    def has_identifiable_items(self, items: List) -> bool:
        """Check if list items have 'name' or 'id' keys."""
        if not items:
            return False

        for item in items:
            if isinstance(item, dict):
                if 'name' in item or 'id' in item or 'key' in item:
                    return True

        return False

    def get_item_id(self, item: Any) -> str:
        """Get identifier for a list item."""
        if isinstance(item, dict):
            return item.get('name') or item.get('id') or item.get('key') or str(hash(str(item)))
        else:
            return str(item)

    def merge_identified_lists(
        self,
        base: List,
        ours: List,
        theirs: List,
        path: str
    ) -> List:
        """
        Merge lists of identified items (dicts with name/id).

        Strategy: merge items by identifier
        """
        # Build maps by identifier
        base_map = {self.get_item_id(item): item for item in base} if base else {}
        our_map = {self.get_item_id(item): item for item in ours}
        their_map = {self.get_item_id(item): item for item in theirs}

        result = []
        seen = set()

        # Process items maintaining order
        for item_id in list(our_map.keys()) + list(their_map.keys()):
            if item_id in seen:
                continue
            seen.add(item_id)

            our_item = our_map.get(item_id)
            their_item = their_map.get(item_id)
            base_item = base_map.get(item_id)

            if our_item is not None and their_item is not None:
                # Both have it - merge
                merged = self.smart_merge(base_item, our_item, their_item, f"{path}[{item_id}]")
                result.append(merged)
            elif our_item is not None:
                # Only we have it
                result.append(our_item)
            else:
                # Only they have it
                result.append(their_item)

        return result

    def merge_simple_lists(
        self,
        base: List,
        ours: List,
        theirs: List,
        path: str
    ) -> List:
        """
        Merge simple lists (no identifiers).

        Strategy: combine unique items, prefer our order
        """
        # Convert to strings for comparison
        base_set = set(str(item) for item in base) if base else set()
        our_set = set(str(item) for item in ours)
        their_set = set(str(item) for item in theirs)

        # Items added by us
        our_additions = our_set - base_set

        # Items added by them
        their_additions = their_set - base_set

        # Start with our list
        result = list(ours)

        # Add their additions that we don't have
        for item in theirs:
            item_str = str(item)
            if item_str in their_additions and item_str not in our_set:
                result.append(item)

        return result

    def merge_scalars(
        self,
        base: Any,
        ours: Any,
        theirs: Any,
        path: str
    ) -> Any:
        """
        Merge scalar values.

        Strategy:
        - If we changed it: use ours
        - If they changed it and we didn't: use theirs
        - If both changed it differently: conflict (use ours, log conflict)
        """

        we_changed = base != ours
        they_changed = base != theirs

        if we_changed and they_changed:
            if ours != theirs:
                # Real conflict - both changed to different values
                self.conflicts.append({
                    'path': path,
                    'base': base,
                    'ours': ours,
                    'theirs': theirs,
                    'resolution': 'ours'
                })
                print(f"⚠️  Conflict at {path}: using ours ({ours})", file=sys.stderr)
                return ours
            else:
                # Both changed to same value - no conflict
                return ours

        elif we_changed:
            # Only we changed - use ours
            return ours

        elif they_changed:
            # Only they changed - use theirs
            return theirs

        else:
            # Neither changed - use any (they're all the same)
            return ours


def merge_yaml_files(base_file: str, our_file: str, their_file: str) -> bool:
    """
    Merge three YAML files.

    Args:
        base_file: Common ancestor
        our_file: Our version (will be overwritten with merge result)
        their_file: Their version

    Returns:
        True if merge successful, False if conflicts remain
    """

    # Load YAML files
    try:
        with open(base_file, 'r', encoding='utf-8') as f:
            base_data = yaml.safe_load(f) or {}
    except FileNotFoundError:
        base_data = {}
    except Exception as e:
        print(f"❌ Error loading base file: {e}", file=sys.stderr)
        return False

    try:
        with open(our_file, 'r', encoding='utf-8') as f:
            our_data = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"❌ Error loading our file: {e}", file=sys.stderr)
        return False

    try:
        with open(their_file, 'r', encoding='utf-8') as f:
            their_data = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"❌ Error loading their file: {e}", file=sys.stderr)
        return False

    # Perform smart merge
    merger = YAMLMerger()
    merged = merger.smart_merge(base_data, our_data, their_data)

    # Write result back to our file
    try:
        with open(our_file, 'w', encoding='utf-8') as f:
            yaml.dump(
                merged,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
                width=120
            )
    except Exception as e:
        print(f"❌ Error writing merged file: {e}", file=sys.stderr)
        return False

    # Report conflicts
    if merger.conflicts:
        print(f"\n⚠️  {len(merger.conflicts)} conflict(s) resolved automatically", file=sys.stderr)
        for conflict in merger.conflicts:
            print(f"  - {conflict['path']}: used ours ({conflict['ours']})", file=sys.stderr)

    print(f"✅ YAML merge successful: {our_file}", file=sys.stderr)
    return True


def main():
    """Main entry point for Git merge driver."""
    if len(sys.argv) != 4:
        print("Usage: yaml-merge.py <base> <ours> <theirs>", file=sys.stderr)
        print("\nThis script is designed to be used as a Git merge driver.", file=sys.stderr)
        print("Configure in .gitattributes:", file=sys.stderr)
        print("  *.yml merge=yaml", file=sys.stderr)
        print("  *.yaml merge=yaml", file=sys.stderr)
        sys.exit(1)

    base_file = sys.argv[1]
    our_file = sys.argv[2]
    their_file = sys.argv[3]

    # Validate files exist
    if not Path(our_file).exists():
        print(f"❌ Error: Our file does not exist: {our_file}", file=sys.stderr)
        sys.exit(1)

    if not Path(their_file).exists():
        print(f"❌ Error: Their file does not exist: {their_file}", file=sys.stderr)
        sys.exit(1)

    # Perform merge
    success = merge_yaml_files(base_file, our_file, their_file)

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
