#!/bin/bash
# Health check script for post-healing verification

set -e

echo "Running post-healing health checks..."

# 1. Check Git repository health
echo "Checking Git repository..."
git status > /dev/null 2>&1 || {
  echo "ERROR: Git repository is corrupted"
  exit 1
}

# 2. Check disk space
echo "Checking disk space..."
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
  echo "WARNING: Disk usage is at ${DISK_USAGE}%"
fi

# 3. Check memory
echo "Checking memory..."
MEMORY_USAGE=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
if [ "$MEMORY_USAGE" -gt 90 ]; then
  echo "WARNING: Memory usage is at ${MEMORY_USAGE}%"
fi

# 4. Check critical files
echo "Checking critical files..."
CRITICAL_FILES=(
  "README.md"
  "requirements.txt"
  ".github/workflows"
)

for file in "${CRITICAL_FILES[@]}"; do
  if [ ! -e "$file" ]; then
    echo "ERROR: Critical file/directory missing: $file"
    exit 1
  fi
done

# 5. Check Python environment
if command -v python &> /dev/null; then
  echo "Checking Python environment..."
  python --version
fi

# 6. Check Docker if available
if command -v docker &> /dev/null; then
  echo "Checking Docker..."
  docker ps > /dev/null 2>&1 || echo "WARNING: Docker not responding"
fi

echo "✅ All health checks passed"
exit 0
