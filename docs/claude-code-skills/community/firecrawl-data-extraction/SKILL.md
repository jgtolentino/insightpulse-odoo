# Firecrawl Data Extraction Skill

**Version:** 1.0.0  
**Category:** Workflow Automation  
**Dependencies:** firecrawl-py, supabase, notion-client  
**Cost Savings:** $12,000/year vs. Apify, ScrapingBee, or Bright Data

---

## Overview

Comprehensive web scraping, crawling, and data extraction skill using Firecrawl. Extract structured data from websites, monitor changes, convert to markdown, and integrate with Supabase, Notion, and Superset for analysis.

**Key Capabilities:**
- 🔍 **Smart Crawling**: Navigate entire sites with JavaScript rendering
- 📄 **Format Conversion**: HTML → Markdown, JSON, structured data
- 🔄 **Change Monitoring**: Track website updates (e.g., BIR announcements)
- 🤖 **AI Extraction**: Use LLM to extract specific data patterns
- 📊 **Data Pipeline**: Crawl → Process → Store in Supabase → Visualize in Superset
- 🔗 **Integration**: Works with Notion, Odoo, MCP servers

---

## Use Cases

### 1. BIR Compliance Monitoring (Finance SSC)
**Problem:** Manually checking BIR website for tax updates, new forms, deadlines  
**Solution:** Auto-crawl BIR website daily, extract announcements, notify via Notion

```python
# Monitor BIR website for updates
crawler.crawl(
    url="https://bir.gov.ph/index.php/tax-information.html",
    match="**/tax-information/**",
    extract_schema={
        "announcements": "list of tax announcements with dates",
        "deadline_changes": "any changes to filing deadlines",
        "new_forms": "newly released BIR forms"
    }
)
```

**Savings:** $500/month vs. manual monitoring + compliance consultant

### 2. OCA Module Discovery (Odoo Development)
**Problem:** Tracking new OCA modules, updates, and documentation  
**Solution:** Crawl OCA GitHub repos, extract module metadata, store in Supabase

```python
# Discover OCA modules
crawler.crawl(
    url="https://github.com/OCA",
    match="**/README.md",
    extract_schema={
        "module_name": "name of the module",
        "version": "Odoo version compatibility",
        "features": "list of features",
        "dependencies": "required OCA modules"
    }
)
```

**Savings:** 10 hours/month research time

### 3. Competitive Analysis (Finance Services)
**Problem:** Monitoring competitor pricing, features, and announcements  
**Solution:** Scheduled crawls of competitor websites with change detection

```python
# Track competitors
crawler.crawl(
    url="https://competitor.com/pricing",
    screenshot=True,
    extract_schema={
        "pricing_tiers": "list of plans with prices",
        "features": "features per tier",
        "promotions": "current promotions"
    }
)
```

**Savings:** $2,000/month vs. competitive intelligence services

### 4. Document Aggregation (Knowledge Base)
**Problem:** Consolidating documentation from multiple sources  
**Solution:** Crawl docs sites, convert to markdown, import to Notion

```python
# Aggregate documentation
crawler.crawl(
    url="https://docs.example.com",
    formats=["markdown", "html"],
    onlyMainContent=True
)
```

**Savings:** 20 hours/month manual copying

### 5. Job Posting Analysis (HR/Recruitment)
**Problem:** Finding talent, tracking salary trends  
**Solution:** Scrape job boards for relevant positions and compensation data

```python
# Analyze job market
crawler.crawl(
    url="https://jobs.example.com",
    match="**/jobs/odoo-developer/**",
    extract_schema={
        "position": "job title",
        "salary_range": "salary information",
        "required_skills": "list of required skills",
        "company": "company name"
    }
)
```

---

## Installation

### Method 1: Python Package
```bash
pip install firecrawl-py supabase notion-client --break-system-packages
```

### Method 2: Docker (Recommended for Production)
```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

RUN pip install firecrawl-py supabase notion-client

WORKDIR /app
COPY . .

CMD ["python", "crawler.py"]
```

### Method 3: Add to Existing DigitalOcean App
```yaml
# deploy/digitalocean.yaml
services:
  - name: firecrawl-worker
    environment_slug: python
    run_command: python workers/firecrawl_worker.py
    envs:
      - key: FIRECRAWL_API_KEY
        scope: RUN_TIME
      - key: SUPABASE_URL
        scope: RUN_TIME
      - key: NOTION_TOKEN
        scope: RUN_TIME
```

---

## Configuration

### Environment Variables
```bash
# Firecrawl API (get from https://firecrawl.dev)
FIRECRAWL_API_KEY=fc-your-api-key

# Storage
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_KEY=your-supabase-key

# Notifications
NOTION_TOKEN=your-notion-integration-token
NOTION_DATABASE_ID=your-database-id

# Scheduling (optional)
CRAWL_SCHEDULE="0 2 * * *"  # Daily at 2 AM
```

### Firecrawl Plans
- **Free Tier**: 500 credits/month (~500 pages)
- **Hobby**: $20/month (2,000 credits)
- **Standard**: $100/month (15,000 credits)
- **Self-Hosted**: Free (requires infrastructure)

**Recommendation:** Start with Free tier, upgrade based on usage

---

## Core Features

### 1. Basic Scraping
```python
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

# Scrape single page
result = app.scrape_url(
    url="https://example.com",
    params={
        "formats": ["markdown", "html"],
        "onlyMainContent": True
    }
)

print(result['markdown'])
```

### 2. Site Crawling
```python
# Crawl entire site
crawl_result = app.crawl_url(
    url="https://example.com",
    params={
        "limit": 100,
        "scrapeOptions": {
            "formats": ["markdown"],
        }
    },
    wait_until_done=True
)

for page in crawl_result['data']:
    print(f"URL: {page['metadata']['sourceURL']}")
    print(f"Title: {page['metadata']['title']}")
    print(f"Content: {page['markdown'][:200]}...")
```

### 3. AI-Powered Extraction
```python
# Extract structured data using LLM
result = app.scrape_url(
    url="https://bir.gov.ph/announcements",
    params={
        "formats": ["extract"],
        "extract": {
            "schema": {
                "type": "object",
                "properties": {
                    "announcements": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "date": {"type": "string"},
                                "category": {"type": "string"},
                                "description": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
    }
)

announcements = result['extract']['announcements']
```

### 4. Screenshot Capture
```python
# Capture visual evidence
result = app.scrape_url(
    url="https://competitor.com/pricing",
    params={
        "formats": ["screenshot"],
        "screenshot": True,
        "fullPageScreenshot": True
    }
)

screenshot_url = result['screenshot']
# Store in DigitalOcean Spaces or Supabase Storage
```

### 5. Change Detection
```python
# Monitor for changes
from hashlib import sha256

def check_for_changes(url, previous_hash):
    result = app.scrape_url(url)
    current_hash = sha256(result['markdown'].encode()).hexdigest()
    
    if current_hash != previous_hash:
        # Content changed - notify
        notify_via_notion(url, result['markdown'])
        return current_hash
    
    return previous_hash
```

---

## Integration Patterns

### Pattern 1: Firecrawl → Supabase → Superset
**Use Case:** BIR announcements dashboard

```python
from firecrawl import FirecrawlApp
from supabase import create_client

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# 1. Crawl BIR website
result = app.scrape_url(
    "https://bir.gov.ph/index.php/tax-information.html",
    params={
        "formats": ["extract"],
        "extract": {
            "schema": {
                "type": "object",
                "properties": {
                    "announcements": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "date": {"type": "string"},
                                "url": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
    }
)

# 2. Store in Supabase
for announcement in result['extract']['announcements']:
    supabase.table("bir_announcements").upsert({
        "title": announcement['title'],
        "date": announcement['date'],
        "url": announcement['url'],
        "scraped_at": "now()"
    }, on_conflict="url").execute()

# 3. Query in Superset
# Create dataset: SELECT * FROM bir_announcements ORDER BY date DESC
```

### Pattern 2: Firecrawl → Notion Database
**Use Case:** Competitive intelligence

```python
from notion_client import Client

notion = Client(auth=os.getenv("NOTION_TOKEN"))

# Crawl competitor
result = app.scrape_url(
    "https://competitor.com/features",
    params={"formats": ["extract"], "extract": {"schema": {...}}}
)

# Create Notion page
notion.pages.create(
    parent={"database_id": os.getenv("NOTION_DATABASE_ID")},
    properties={
        "Name": {"title": [{"text": {"content": "Competitor Analysis"}}]},
        "Source": {"url": "https://competitor.com/features"},
        "Date": {"date": {"start": str(date.today())}},
        "Status": {"select": {"name": "Reviewed"}}
    },
    children=[
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"text": {"content": result['markdown']}}]
            }
        }
    ]
)
```

### Pattern 3: Scheduled Crawling with Cron
**Use Case:** Daily BIR monitoring

```python
# workers/bir_monitor.py
import schedule
import time

def monitor_bir():
    print(f"[{datetime.now()}] Checking BIR website...")
    result = app.scrape_url("https://bir.gov.ph/...")
    
    # Check for new announcements
    new_items = check_new_announcements(result)
    
    if new_items:
        # Notify via Notion
        for item in new_items:
            notify_team(item)
            
    print(f"Found {len(new_items)} new announcements")

# Run daily at 2 AM
schedule.every().day.at("02:00").do(monitor_bir)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Pattern 4: MCP Server with Firecrawl Tools
**Use Case:** AI agent that can scrape web pages

```python
# mcp-server with Firecrawl tools
from mcp.server import Server
from mcp.types import Tool

server = Server("firecrawl-mcp")

@server.tool()
async def scrape_website(url: str, format: str = "markdown") -> str:
    """Scrape a website and return content in specified format"""
    result = app.scrape_url(url, params={"formats": [format]})
    return result.get(format, result.get('markdown', ''))

@server.tool()
async def extract_data(url: str, schema: dict) -> dict:
    """Extract structured data from a website using AI"""
    result = app.scrape_url(
        url,
        params={"formats": ["extract"], "extract": {"schema": schema}}
    )
    return result['extract']

@server.tool()
async def monitor_changes(url: str) -> dict:
    """Check if a website has changed since last check"""
    # Implementation with change detection
    pass
```

---

## Example: Complete BIR Monitoring System

```python
#!/usr/bin/env python3
"""
BIR Compliance Monitoring System
Monitors BIR website for updates and notifies via Notion
"""

import os
from datetime import datetime
from firecrawl import FirecrawlApp
from supabase import create_client
from notion_client import Client

# Initialize clients
firecrawl = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)
notion = Client(auth=os.getenv("NOTION_TOKEN"))

# BIR pages to monitor
BIR_PAGES = [
    "https://bir.gov.ph/index.php/tax-information.html",
    "https://bir.gov.ph/index.php/bir-forms.html",
    "https://bir.gov.ph/index.php/revenue-memorandum-circulars.html"
]

def scrape_bir_page(url):
    """Scrape BIR page and extract announcements"""
    result = firecrawl.scrape_url(
        url,
        params={
            "formats": ["extract"],
            "extract": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "announcements": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "date": {"type": "string"},
                                    "category": {"type": "string"},
                                    "description": {"type": "string"},
                                    "link": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        }
    )
    
    return result['extract']['announcements']

def store_in_supabase(announcements):
    """Store announcements in Supabase"""
    for ann in announcements:
        # Upsert to avoid duplicates
        supabase.table("bir_announcements").upsert({
            "title": ann['title'],
            "date": ann['date'],
            "category": ann['category'],
            "description": ann['description'],
            "link": ann['link'],
            "scraped_at": datetime.now().isoformat(),
            "status": "new"
        }, on_conflict="link").execute()

def create_notion_task(announcement):
    """Create Notion task for new announcement"""
    notion.pages.create(
        parent={"database_id": os.getenv("NOTION_BIR_DB_ID")},
        properties={
            "Name": {
                "title": [{"text": {"content": announcement['title']}}]
            },
            "Category": {
                "select": {"name": announcement['category']}
            },
            "Due Date": {
                "date": {"start": announcement['date']}
            },
            "Status": {
                "select": {"name": "To Review"}
            },
            "Source": {
                "url": announcement['link']
            },
            "Agencies": {
                "multi_select": [
                    {"name": "RIM"}, {"name": "CKVC"}, 
                    {"name": "BOM"}, {"name": "JPAL"},
                    {"name": "JLI"}, {"name": "JAP"},
                    {"name": "LAS"}, {"name": "RMQB"}
                ]
            }
        },
        children=[
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "text": {"content": announcement['description']}
                    }]
                }
            }
        ]
    )

def main():
    """Main monitoring loop"""
    print(f"[{datetime.now()}] Starting BIR monitoring...")
    
    all_announcements = []
    
    # Crawl all BIR pages
    for url in BIR_PAGES:
        print(f"Scraping: {url}")
        try:
            announcements = scrape_bir_page(url)
            all_announcements.extend(announcements)
            print(f"  Found {len(announcements)} announcements")
        except Exception as e:
            print(f"  Error: {e}")
    
    # Store in Supabase
    print(f"Storing {len(all_announcements)} announcements...")
    store_in_supabase(all_announcements)
    
    # Get new announcements (not yet reviewed)
    new_announcements = supabase.table("bir_announcements")\
        .select("*")\
        .eq("status", "new")\
        .execute()
    
    # Create Notion tasks for new items
    print(f"Creating {len(new_announcements.data)} Notion tasks...")
    for ann in new_announcements.data:
        try:
            create_notion_task(ann)
            # Mark as processed
            supabase.table("bir_announcements")\
                .update({"status": "notified"})\
                .eq("id", ann['id'])\
                .execute()
        except Exception as e:
            print(f"  Error creating task: {e}")
    
    print(f"[{datetime.now()}] Monitoring complete!")

if __name__ == "__main__":
    main()
```

**Deploy to DigitalOcean:**
```yaml
# .github/workflows/deploy-bir-monitor.yml
name: Deploy BIR Monitor

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install firecrawl-py supabase notion-client
      - run: python workers/bir_monitor.py
        env:
          FIRECRAWL_API_KEY: ${{ secrets.FIRECRAWL_API_KEY }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
          NOTION_TOKEN: ${{ secrets.NOTION_TOKEN }}
          NOTION_BIR_DB_ID: ${{ secrets.NOTION_BIR_DB_ID }}
```

---

## Advanced Features

### 1. Rate Limiting and Retries
```python
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def scrape_with_retry(url):
    return app.scrape_url(url)
```

### 2. Proxy Rotation
```python
# For sites that block scrapers
result = app.scrape_url(
    url,
    params={
        "formats": ["markdown"],
        "headers": {
            "User-Agent": "Mozilla/5.0 ...",
        },
        "waitFor": 2000,  # Wait for JS to load
    }
)
```

### 3. Batch Processing
```python
# Crawl multiple URLs efficiently
urls = [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3"
]

results = []
for url in urls:
    result = app.scrape_url(url)
    results.append(result)
    time.sleep(1)  # Be nice to servers
```

### 4. Data Enrichment
```python
# Combine Firecrawl with AI for enrichment
from anthropic import Anthropic

anthropic = Anthropic()

# Scrape content
content = app.scrape_url("https://example.com")['markdown']

# Enrich with AI
enriched = anthropic.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1000,
    messages=[{
        "role": "user",
        "content": f"Summarize this BIR announcement:\n\n{content}"
    }]
)
```

---

## Cost Optimization

### Self-Hosted Option (Free)
```bash
# Clone Firecrawl
git clone https://github.com/mendableai/firecrawl
cd firecrawl

# Deploy with Docker
docker-compose up -d

# Use local endpoint
FIRECRAWL_API_URL=http://localhost:3002
```

**Benefits:**
- No API costs
- Unlimited scraping
- Full control

**Drawbacks:**
- Infrastructure management
- Maintenance overhead
- ~$20/month DigitalOcean droplet

### Hybrid Approach
- **Development:** Self-hosted
- **Production:** Firecrawl API (for reliability)

---

## Monitoring & Alerts

### Track Scraping Success
```sql
-- Supabase: Track scraping runs
CREATE TABLE scrape_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url TEXT NOT NULL,
    status TEXT NOT NULL,
    pages_scraped INT,
    errors INT,
    duration_ms INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Query failed scrapes
SELECT * FROM scrape_logs 
WHERE status = 'failed' 
AND created_at > NOW() - INTERVAL '24 hours';
```

### Superset Dashboard
```sql
-- Create Superset dataset
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_scrapes,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
    AVG(duration_ms) as avg_duration_ms
FROM scrape_logs
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

---

## Security Best Practices

### 1. API Key Management
```bash
# Never commit keys to git
echo "FIRECRAWL_API_KEY=*" >> .gitignore

# Use environment variables
export FIRECRAWL_API_KEY=fc-xxx

# Or use secrets manager
doctl secrets create FIRECRAWL_API_KEY --value="fc-xxx"
```

### 2. Rate Limiting
```python
# Respect robots.txt
from urllib.robotparser import RobotFileParser

rp = RobotFileParser()
rp.set_url("https://example.com/robots.txt")
rp.read()

if rp.can_fetch("*", url):
    result = app.scrape_url(url)
```

### 3. Error Handling
```python
try:
    result = app.scrape_url(url)
except Exception as e:
    # Log error
    supabase.table("scrape_logs").insert({
        "url": url,
        "status": "failed",
        "error": str(e)
    }).execute()
```

---

## Skill Combinations

### With Other Skills

**odoo-finance-automation + firecrawl-data-extraction:**
- Scrape BIR forms → Auto-fill in Odoo
- Monitor tax rates → Update Odoo accounting

**superset-dashboard-automation + firecrawl-data-extraction:**
- Scrape data → Store in Supabase → Visualize in Superset
- Competitive pricing tracking dashboard

**notion-workflow-sync + firecrawl-data-extraction:**
- Scrape news → Create Notion pages → Assign tasks
- Document aggregation workflow

**paddle-ocr-validation + firecrawl-data-extraction:**
- Scrape PDFs → OCR extract → Validate against BIR rules
- Receipt verification pipeline

---

## ROI Calculation

### Savings vs. Alternatives

| Service | Monthly Cost | Annual Cost |
|---------|-------------|-------------|
| Apify | $49-499 | $588-5,988 |
| ScrapingBee | $49-449 | $588-5,388 |
| Bright Data | $500+ | $6,000+ |
| **Firecrawl** | **$0-100** | **$0-1,200** |

**Savings: $5,000-12,000/year**

### Time Savings
- **Manual monitoring:** 2 hours/day × $50/hour = $100/day
- **Automated:** $0.10/day in API costs
- **Annual savings:** $36,000 in labor

### Total ROI
- **Investment:** $1,200/year (Firecrawl Standard plan)
- **Savings:** $41,000/year (labor + tools)
- **Net benefit:** $39,800/year
- **ROI:** 3,317%

---

## Troubleshooting

### Common Issues

**1. Rate Limiting**
```python
# Add delays between requests
time.sleep(2)

# Or use built-in rate limiting
result = app.scrape_url(url, params={"wait": 2000})
```

**2. JavaScript Not Loading**
```python
# Increase wait time
result = app.scrape_url(
    url,
    params={"waitFor": 5000}  # Wait 5 seconds
)
```

**3. Blocked by Anti-Bot**
```python
# Use stealth mode
result = app.scrape_url(
    url,
    params={
        "headers": {
            "User-Agent": "Mozilla/5.0 ...",
            "Referer": "https://google.com"
        }
    }
)
```

---

## Next Steps

1. **Get Firecrawl API Key:** https://firecrawl.dev
2. **Set up Supabase tables** for scraped data
3. **Create Notion database** for task tracking
4. **Deploy BIR monitor** to DigitalOcean
5. **Build Superset dashboard** for insights

---

## Resources

- **Firecrawl Docs:** https://docs.firecrawl.dev
- **API Reference:** https://docs.firecrawl.dev/api-reference
- **GitHub:** https://github.com/mendableai/firecrawl
- **Community:** Discord, GitHub Discussions

---

**Created by:** Jake Tolentino  
**Organization:** Finance Shared Service Center  
**License:** MIT
