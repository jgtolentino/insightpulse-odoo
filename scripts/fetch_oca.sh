#!/bin/bash
# fetch_oca.sh
# This script reads a list of Git repos and clones them into the addons directory.
# It's run *inside* the Dockerfile during the build.

set -e

REPO_LIST_FILE=$1
DEST_DIR=$2

if [ -z "$REPO_LIST_FILE" ] || [ -z "$DEST_DIR" ]; then
    echo "Usage: $0 <repo_list_file> <destination_dir>"
    exit 1
fi

mkdir -p $DEST_DIR

# Read the file line by line
while IFS= read -r REPO_URL || [ -n "$REPO_URL" ]; do
    if [ -n "$REPO_URL" ]; then
        echo "--- Cloning $REPO_URL ---"
        # We do a shallow clone (depth 1) of the specific branch (e.g., 16.0)
        # This keeps the image size small.
        # Format for oca_requirements.txt should be: https://github.com/OCA/web 16.0
        REPO=$(echo $REPO_URL | cut -d' ' -f1)
        BRANCH=$(echo $REPO_URL | cut -d' ' -f2)
        git clone --depth 1 --branch $BRANCH $REPO $DEST_DIR/$(basename $REPO)
    fi
done < "$REPO_LIST_FILE"

echo "--- OCA modules fetched successfully ---"
