# Odoo Knowledge Agent

Automated forum scraper that extracts solved issues from Odoo forum to build error prevention guardrails and auto-fix patches.

## Features

- **Automated Scraping**: Cron job runs weekly to scrape solved forum issues
- **Manual Trigger**: Run scraper on-demand from Odoo UI
- **Logging**: Track all scraping sessions with detailed logs
- **Integration**: Uses existing scraper script from `agents/odoo-knowledge/`

## Installation

1. Add module to Odoo addons path
2. Install Python dependencies:
   ```bash
   pip install playwright
   python3 -m playwright install chromium
   ```
3. Update Odoo apps list
4. Install "Odoo Knowledge Agent" module

## Usage

### Automatic Scraping (Cron Job)

The cron job runs **weekly** by default:
- Model: `odoo.knowledge.agent`
- Method: `cron_scrape_forum()`
- Interval: 1 week
- Active: Yes

To modify schedule:
1. Go to: Settings → Technical → Automation → Scheduled Actions
2. Find: "Odoo Forum Scraper"
3. Edit interval (daily, weekly, monthly)

### Manual Scraping

1. Navigate to: **Knowledge Agent → Forum Scrapes**
2. Click: **Create**
3. Click: **Run Scraper** button
4. Monitor progress in the form view

### View Results

- **Output File**: `agents/odoo-knowledge/knowledge/solved_issues_raw.json`
- **Statistics**: Pages scraped, issues found
- **Logs**: Detailed execution logs in the "Logs" tab

## Configuration

### Scraper Settings

Edit `agents/odoo-knowledge/scraper/scrape_solved_threads.py`:
- `MAX_PAGES`: Number of pages to scrape (default: 100)
- `BASE_URL`: Odoo forum URL
- `QUERY`: Forum search query

### Cron Job Settings

Edit `data/cron_forum_scraper.xml`:
- `interval_number`: How often (1, 2, 3, etc.)
- `interval_type`: Unit (days, weeks, months)
- `active`: Enable/disable cron

## Technical Details

### Models

**`odoo.knowledge.agent`**
- Tracks scraping sessions
- States: draft, running, done, failed
- Fields: pages_scraped, issues_found, output_file

**`odoo.knowledge.agent.log`**
- Logs scraper execution
- Levels: info, warning, error

### Scraper Integration

The module calls the existing Python scraper:
```python
scraper_path = 'agents/odoo-knowledge/scraper/scrape_solved_threads.py'
subprocess.run(['python3', str(scraper_path)])
```

### Output

Scraper generates:
- `solved_issues_raw.json` - Raw scraped data (~1,100 issues)
- Used by downstream guardrails and auto-patches

## Troubleshooting

### Playwright Not Installed
```bash
pip install playwright
python3 -m playwright install chromium
```

### Scraper Timeout
- Default: 1 hour timeout
- Edit: `timeout=3600` in `knowledge_agent.py`

### Permission Errors
- Check file permissions on `agents/odoo-knowledge/`
- Ensure Odoo user can write to output directory

## Related

- **Guardrails**: `agents/odoo-knowledge/guardrails/`
- **Auto-patches**: `agents/odoo-knowledge/autopatches/`
- **Documentation**: `agents/odoo-knowledge/README.md`

---

**Version**: 1.0.0
**Author**: InsightPulse AI
**License**: LGPL-3
