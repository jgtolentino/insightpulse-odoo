#!/bin/bash
# fetch_oca.sh
# This script reads a list of Git repos and clones them into the addons directory.
# It's run *inside* the Dockerfile during the build.

set -e

REPO_LIST_FILE="$1"
DEST_DIR="$2"

if [ -z "$REPO_LIST_FILE" ] || [ -z "$DEST_DIR" ]; then
    echo "Usage: $0 <repo_list_file> <destination_dir>"
    exit 1
fi

if [ ! -f "$REPO_LIST_FILE" ]; then
    echo "Error: Repository list file not found: $REPO_LIST_FILE"
    exit 1
fi

mkdir -p "$DEST_DIR"

echo "=== Fetching OCA modules into $DEST_DIR ==="
echo ""

# Read the file line by line
while IFS= read -r REPO_URL || [ -n "$REPO_URL" ]; do
    # Skip empty lines and comments
    if [ -z "$REPO_URL" ] || [[ "$REPO_URL" =~ ^[[:space:]]*# ]]; then
        continue
    fi

    echo "--- Cloning $REPO_URL ---"
    # We do a shallow clone (depth 1) of the specific branch (e.g., 19.0, 18.0)
    # This keeps the image size small.
    # Format for oca_requirements.txt should be: https://github.com/OCA/web 19.0
    REPO=$(echo "$REPO_URL" | cut -d' ' -f1)
    BRANCH=$(echo "$REPO_URL" | cut -d' ' -f2)
    REPO_NAME=$(basename "$REPO" .git)

    if [ -z "$REPO" ] || [ -z "$BRANCH" ]; then
        echo "Warning: Skipping malformed line: $REPO_URL"
        continue
    fi

    if git clone --depth 1 --branch "$BRANCH" "$REPO" "$DEST_DIR/$REPO_NAME"; then
        echo "✓ Successfully cloned $REPO_NAME (branch: $BRANCH)"
    else
        echo "✗ Failed to clone $REPO_NAME (branch: $BRANCH)"
        exit 1
    fi
    echo ""
done < "$REPO_LIST_FILE"

echo "=== OCA modules fetched successfully ==="
