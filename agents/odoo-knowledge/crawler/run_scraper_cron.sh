#!/bin/bash
# Odoo Knowledge Base Scraper - Production Cron Job
# Runs scraper, processes results, commits to repo

set -e  # Exit on error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="$PROJECT_ROOT/logs/scraper"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/scraper_$TIMESTAMP.log"

# Create log directory
mkdir -p "$LOG_DIR"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "ERROR: $1"
    # Optional: Send notification (email, Slack, etc.)
    # curl -X POST "$SLACK_WEBHOOK" -d "{\"text\":\"Odoo scraper failed: $1\"}"
    exit 1
}

# Trap errors
trap 'error_exit "Script failed at line $LINENO"' ERR

log "=========================================="
log "Starting Odoo Knowledge Base Scraper"
log "=========================================="

# Check if in git repo
cd "$PROJECT_ROOT" || error_exit "Cannot cd to project root: $PROJECT_ROOT"

if [ ! -d ".git" ]; then
    error_exit "Not a git repository: $PROJECT_ROOT"
fi

log "Project root: $PROJECT_ROOT"
log "Log file: $LOG_FILE"

# Pull latest changes
log "Pulling latest changes from git..."
git fetch origin || error_exit "Git fetch failed"
git pull origin "$(git branch --show-current)" || log "WARNING: Git pull failed (may be OK if ahead)"

# Check Python and dependencies
log "Checking Python environment..."
if ! command -v python3 &> /dev/null; then
    error_exit "Python3 not found"
fi

PYTHON_VERSION=$(python3 --version)
log "Python version: $PYTHON_VERSION"

# Install/update dependencies
log "Installing dependencies..."
cd "$SCRIPT_DIR"
pip3 install -q -r ../requirements.txt || error_exit "Failed to install dependencies"

# Run scraper
log "Running scraper (this may take 30-60 minutes)..."
SCRAPER_OUTPUT="$LOG_DIR/scraper_output_$TIMESTAMP.json"

python3 scrape_solved_threads.py 2>&1 | tee -a "$LOG_FILE"

if [ ! -f "../knowledge/solved_threads_raw.json" ]; then
    error_exit "Scraper failed - output file not found"
fi

# Check output size
OUTPUT_SIZE=$(wc -l < "../knowledge/solved_threads_raw.json")
log "Scraped $OUTPUT_SIZE lines"

if [ "$OUTPUT_SIZE" -lt 10 ]; then
    error_exit "Scraper output too small ($OUTPUT_SIZE lines) - possible failure"
fi

# Process results (if processor exists)
if [ -f "../scraper/process_solutions_simple.py" ]; then
    log "Processing solutions..."
    cd "$PROJECT_ROOT/agents/odoo-knowledge/scraper"
    python3 process_solutions_simple.py 2>&1 | tee -a "$LOG_FILE" || log "WARNING: Solution processing failed"
fi

# Commit changes
cd "$PROJECT_ROOT"
log "Committing changes..."

# Check if there are changes
if git diff --quiet agents/odoo-knowledge/knowledge/; then
    log "No changes detected - skipping commit"
else
    ISSUE_COUNT=$(grep -o '"id":' agents/odoo-knowledge/knowledge/solved_threads_raw.json | wc -l || echo "unknown")

    git add agents/odoo-knowledge/knowledge/
    git commit -m "chore: update Odoo knowledge base (scraped $ISSUE_COUNT issues)

Automated scraper run at $TIMESTAMP
Log: logs/scraper/scraper_$TIMESTAMP.log" || error_exit "Git commit failed"

    # Push to remote
    log "Pushing to remote..."
    git push origin "$(git branch --show-current)" || error_exit "Git push failed"

    log "Changes committed and pushed successfully"
fi

# Cleanup old logs (keep last 30 days)
log "Cleaning up old logs..."
find "$LOG_DIR" -name "scraper_*.log" -mtime +30 -delete 2>/dev/null || true

# Summary
log "=========================================="
log "Scraper completed successfully!"
log "Total issues in knowledge base: $ISSUE_COUNT"
log "Log file: $LOG_FILE"
log "=========================================="

exit 0
