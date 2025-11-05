#!/usr/bin/env python3
"""
deduplicate-archives.py
Deduplicate extracted archive contents by finding and removing duplicate files
"""

import os
import hashlib
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Configuration
EXTRACTED_DIR = Path("/Users/tbwa/insightpulse-odoo/.extracted-archives")
LOG_FILE = EXTRACTED_DIR / "deduplication-log.txt"

def compute_md5(file_path):
    """Compute MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"⚠️  Error hashing {file_path}: {e}")
        return None

def find_duplicates():
    """Find duplicate files by hash."""
    print(f"ℹ️  Scanning: {EXTRACTED_DIR}")

    hash_to_files = defaultdict(list)
    file_count = 0

    # Compute hashes for all files
    for root, dirs, files in os.walk(EXTRACTED_DIR):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for filename in files:
            # Skip hidden files and log files
            if filename.startswith('.') or filename == 'deduplication-log.txt':
                continue

            file_path = Path(root) / filename
            file_count += 1

            if file_count % 100 == 0:
                print(f"Processed {file_count} files...")

            file_hash = compute_md5(file_path)
            if file_hash:
                hash_to_files[file_hash].append(file_path)

    # Find duplicates
    duplicates = {hash: files for hash, files in hash_to_files.items() if len(files) > 1}

    print(f"\n✅ Scan complete!")
    print(f"Total files scanned: {file_count}")
    print(f"Unique files: {len(hash_to_files)}")
    print(f"Duplicate sets: {len(duplicates)}")
    print(f"Duplicate files: {sum(len(files) - 1 for files in duplicates.values())}")

    return duplicates

def write_log(duplicates):
    """Write deduplication log."""
    with open(LOG_FILE, 'w') as f:
        f.write(f"=== Archive Deduplication Log ===\n")
        f.write(f"Date: {datetime.now()}\n")
        f.write(f"Directory: {EXTRACTED_DIR}\n\n")

        f.write(f"Duplicate sets: {len(duplicates)}\n")
        f.write(f"Duplicate files: {sum(len(files) - 1 for files in duplicates.values())}\n\n")

        f.write("=== Duplicates ===\n\n")

        for hash_value, files in sorted(duplicates.items()):
            f.write(f"Hash: {hash_value}\n")
            f.write(f"Original: {files[0]}\n")
            f.write(f"Duplicates:\n")
            for dup in files[1:]:
                f.write(f"  - {dup}\n")
            f.write("\n")

    print(f"📝 Log written: {LOG_FILE}")

def delete_duplicates(duplicates, dry_run=True):
    """Delete duplicate files (keep first occurrence)."""
    if dry_run:
        print("\n🔍 DRY RUN - No files will be deleted")

    deleted_count = 0
    space_saved = 0

    for hash_value, files in duplicates.items():
        # Keep first file, delete rest
        original = files[0]
        for dup in files[1:]:
            try:
                file_size = dup.stat().st_size
                if not dry_run:
                    dup.unlink()
                deleted_count += 1
                space_saved += file_size
                print(f"{'Would delete' if dry_run else 'Deleted'}: {dup.relative_to(EXTRACTED_DIR)}")
            except Exception as e:
                print(f"⚠️  Error deleting {dup}: {e}")

    print(f"\n{'Would delete' if dry_run else 'Deleted'}: {deleted_count} files")
    print(f"Space {'would be' if dry_run else ''} saved: {space_saved / 1024 / 1024:.2f} MB")

    return deleted_count, space_saved

def main():
    print("=== Archive Deduplication ===\n")

    if not EXTRACTED_DIR.exists():
        print(f"❌ Directory not found: {EXTRACTED_DIR}")
        return

    # Find duplicates
    duplicates = find_duplicates()

    if not duplicates:
        print("\n✅ No duplicates found!")
        return

    # Write log
    write_log(duplicates)

    # Dry run first
    print("\n" + "="*50)
    delete_duplicates(duplicates, dry_run=True)

    # Prompt for actual deletion
    print("\n" + "="*50)
    response = input("\nDelete duplicate files? (y/N): ").strip().lower()

    if response == 'y':
        print("\nDeleting duplicates...")
        deleted, saved = delete_duplicates(duplicates, dry_run=False)

        # Update log with deletion results
        with open(LOG_FILE, 'a') as f:
            f.write("=== Deletion Summary ===\n")
            f.write(f"Files deleted: {deleted}\n")
            f.write(f"Space saved: {saved / 1024 / 1024:.2f} MB\n")

        print(f"\n✅ Deduplication complete! Log: {LOG_FILE}")
    else:
        print("\n⏸️  Deletion cancelled. Review log for details.")

if __name__ == "__main__":
    main()
