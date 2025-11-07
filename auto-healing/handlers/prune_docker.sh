#!/usr/bin/env bash
set -euo pipefail

# Auto-heal handler: Prune Docker resources
# Error: DOCKER-DISK-PRESSURE

LOG_PREFIX="[heal:prune_docker]"

echo "$LOG_PREFIX Starting heal for disk pressure"

# Get disk usage before
BEFORE=$(df -h / | tail -1 | awk '{print $5}')
echo "$LOG_PREFIX Disk usage before: $BEFORE"

# Prune unused containers, images, volumes
echo "$LOG_PREFIX Pruning unused containers..."
docker container prune -f

echo "$LOG_PREFIX Pruning unused images..."
docker image prune -af

echo "$LOG_PREFIX Pruning unused volumes..."
docker volume prune -f

echo "$LOG_PREFIX Pruning build cache..."
docker builder prune -af

# Get disk usage after
AFTER=$(df -h / | tail -1 | awk '{print $5}')
echo "$LOG_PREFIX Disk usage after: $AFTER"

echo "$LOG_PREFIX Heal completed successfully"
