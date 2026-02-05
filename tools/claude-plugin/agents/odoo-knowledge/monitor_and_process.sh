#!/bin/bash
# Background monitoring and processing pipeline for Odoo knowledge scraper

LOG_FILE="agents/odoo-knowledge/scraper/scrape.log"
STATUS_FILE="agents/odoo-knowledge/scraper/status.json"
KNOWLEDGE_DIR="agents/odoo-knowledge/knowledge"

mkdir -p "$KNOWLEDGE_DIR"

echo "🔄 Starting continuous scraping and indexing pipeline..."

# Function to check if scraping is complete
check_scraping_complete() {
    grep -q "✅ Scraping complete!" "$LOG_FILE" 2>/dev/null
}

# Function to check if processing is complete
check_processing_complete() {
    [ -f "$KNOWLEDGE_DIR/solutions_processed.json" ]
}

# Monitor scraping progress
while ! check_scraping_complete; do
    if [ -f "$LOG_FILE" ]; then
        # Get last 3 lines to show progress
        tail -3 "$LOG_FILE" | grep -E "(📄|✅|⚠️)" || true
    fi
    sleep 10
done

echo ""
echo "✅ Scraping complete! Starting solution processing..."

# Process solutions
cd agents/odoo-knowledge/scraper
python3 process_solutions.py 2>&1 | tee process.log

echo ""
echo "📊 Creating knowledge index..."

# Create index file
cd ../..
python3 -c "
import json
from pathlib import Path

knowledge_dir = Path('agents/odoo-knowledge/knowledge')
raw_file = knowledge_dir / 'solved_issues_raw.json'
processed_file = knowledge_dir / 'solutions_processed.json'
index_file = knowledge_dir / 'index.json'

# Load data
raw_data = json.loads(raw_file.read_text()) if raw_file.exists() else []
processed_data = json.loads(processed_file.read_text()) if processed_file.exists() else []

# Build index
index = {
    'total_issues': len(raw_data),
    'processed_issues': len(processed_data),
    'categories': {},
    'modules': {},
    'error_types': {},
    'by_tag': {}
}

# Count by category
for issue in processed_data:
    module = issue.get('module', 'unknown')
    error_type = issue.get('error_type', 'unknown')

    index['modules'][module] = index['modules'].get(module, 0) + 1
    index['error_types'][error_type] = index['error_types'].get(error_type, 0) + 1

    for tag in issue.get('tags', []):
        index['by_tag'][tag] = index['by_tag'].get(tag, 0) + 1

# Save index
index_file.write_text(json.dumps(index, indent=2))

print('✅ Index created!')
print(f'📊 Total issues: {index[\"total_issues\"]}')
print(f'📊 Processed: {index[\"processed_issues\"]}')
print(f'📊 Modules: {list(index[\"modules\"].keys())}')
"

echo ""
echo "🎉 COMPLETE! Knowledge base ready."
echo ""
echo "📁 Files created:"
ls -lh agents/odoo-knowledge/knowledge/*.json 2>/dev/null || echo "   (checking...)"

# Update status
cat > "$STATUS_FILE" <<EOF
{
  "status": "complete",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "files": {
    "raw": "knowledge/solved_issues_raw.json",
    "processed": "knowledge/solutions_processed.json",
    "index": "knowledge/index.json"
  }
}
EOF

echo ""
echo "✅ All done! Check agents/odoo-knowledge/knowledge/ for results."
