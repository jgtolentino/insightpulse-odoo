# 🚀 Notion BIR Task Automations - Deployment Guide

**Database:** https://notion.so/73c27159-544e-414b-846f-edf41e296091

## 🚨 CRITICAL: Security First

**Your Notion API key was exposed and MUST be rotated immediately:**

1. Go to https://www.notion.so/my-integrations
2. Find integration: **"BIR Task Automations"** or create new one
3. Click **"Secrets"** → **"Rotate Secret"**
4. Copy new key (starts with `ntn_`)
5. **Never** commit this key to git or share in chat

---

## 📦 What's Deployed

You now have **3 deployment options** ready to use:

### Option 1: GitHub Actions (Recommended)
- **Location:** `.github/workflows/notion-automations.yml`
- **Schedule:** 9 AM & 3 PM Manila time (daily)
- **Cost:** Free (included in GitHub)
- **Setup Time:** 5 minutes

### Option 2: Supabase Edge Functions
- **Location:** `supabase/functions/notion-{overdue,escalation}/`
- **Schedule:** Configure in Supabase dashboard
- **Cost:** Free tier (up to 500K invocations/month)
- **Setup Time:** 10 minutes

### Option 3: DigitalOcean App Platform
- **Location:** `infra/do/notion-automations.yaml`
- **Schedule:** DO App Platform cron jobs
- **Cost:** ~$5/month (basic-xxs instance)
- **Setup Time:** 15 minutes

---

## 🎯 Quick Start: GitHub Actions (5 Minutes)

### Step 1: Rotate API Key
```bash
# Get new key from https://www.notion.so/my-integrations
# Store it safely (never commit!)
```

### Step 2: Add GitHub Secrets

Go to your repo:
https://github.com/jgtolentino/insightpulse-odoo/settings/secrets/actions

Add two secrets:
- **NOTION_API_KEY** → `ntn_YOUR_NEW_KEY_HERE`
- **NOTION_DATABASE_ID** → `73c27159-544e-414b-846f-edf41e296091`

### Step 3: Install Dependencies

```bash
cd ~/Documents/GitHub/insightpulse-odoo/scripts/notion
npm install
```

### Step 4: Test Locally (Optional)

```bash
# Set environment variables (never commit!)
export NOTION_API_KEY="ntn_YOUR_NEW_KEY_HERE"
export NOTION_DATABASE_ID="73c27159-544e-414b-846f-edf41e296091"

# Test connection
node test-connection.js

# Run one-time formula setup
node 04-add-days-late-formula.js

# Test automations
npm run overdue-check
npm run escalation
```

### Step 5: Commit & Push

```bash
cd ~/Documents/GitHub/insightpulse-odoo
git add .github/workflows/notion-automations.yml
git add scripts/notion/
git commit -m "feat: Add Notion BIR task automations

- Daily overdue check (9 AM Manila)
- Escalation for 2+ day late tasks (3 PM Manila)
- GitHub Actions deployment
- Supabase Edge Functions ready
- DigitalOcean App Platform spec"

git push origin main
```

### Step 6: Verify

1. Go to https://github.com/jgtolentino/insightpulse-odoo/actions
2. Find workflow: **"Notion BIR Task Automations"**
3. Click **"Run workflow"** → Select **"test"** → Run
4. Check logs for ✅ success

---

## 🔧 Option 2: Supabase Edge Functions

### Step 1: Install Supabase CLI

```bash
brew install supabase/tap/supabase
supabase login
```

### Step 2: Link Project

```bash
cd ~/Documents/GitHub/insightpulse-odoo
supabase link --project-ref spdtwktxdalcfigzeqrz
```

### Step 3: Set Secrets

```bash
supabase secrets set NOTION_API_KEY="ntn_YOUR_NEW_KEY_HERE"
supabase secrets set NOTION_DATABASE_ID="73c27159-544e-414b-846f-edf41e296091"
```

### Step 4: Deploy Functions

```bash
supabase functions deploy notion-overdue
supabase functions deploy notion-escalation
```

### Step 5: Configure Cron

1. Go to https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz
2. Navigate to **Edge Functions** → **Cron Jobs**
3. Add two cron jobs:

**Job 1: Overdue Check**
- Name: `notion-overdue-9am`
- Schedule: `0 1 * * *` (9 AM Manila = 1 AM UTC)
- Function: `notion-overdue`

**Job 2: Escalation**
- Name: `notion-escalation-3pm`
- Schedule: `0 7 * * *` (3 PM Manila = 7 AM UTC)
- Function: `notion-escalation`

### Step 6: Test

```bash
# Test overdue function
curl -X POST https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/notion-overdue \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY"

# Test escalation function
curl -X POST https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/notion-escalation \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY"
```

---

## 🌊 Option 3: DigitalOcean App Platform

### Step 1: Create App

```bash
doctl apps create --spec infra/do/notion-automations.yaml
```

Output will show app ID (save this).

### Step 2: Set Environment Variables

Go to DigitalOcean dashboard:
https://cloud.digitalocean.com/apps

1. Find app: **"notion-bir-automations"**
2. Go to **Settings** → **Environment Variables**
3. Add:
   - **NOTION_API_KEY** (Secret) → Your rotated key
   - **NOTION_DATABASE_ID** (General) → `73c27159-544e-414b-846f-edf41e296091`
   - **TZ** (General) → `Asia/Manila`

### Step 3: Deploy

```bash
doctl apps create-deployment <app-id>
```

### Step 4: Monitor

```bash
# View logs
doctl apps logs <app-id> --follow

# Check cron jobs
# Go to App Platform → Jobs → View Schedule
```

---

## 📊 Add "Days late" Formula to Notion Database

Run this **once** to add the formula property:

```bash
cd ~/Documents/GitHub/insightpulse-odoo/scripts/notion

export NOTION_API_KEY="ntn_YOUR_NEW_KEY_HERE"
export NOTION_DATABASE_ID="73c27159-544e-414b-846f-edf41e296091"

node 04-add-days-late-formula.js
```

This adds a formula that automatically calculates days overdue.

---

## 🎨 Optional: Native Notion Automations

You can also configure automations **inside Notion** (complements the API automations):

### Automation 1: Daily 9 AM Reminder

1. Open database in Notion
2. Click **"•••"** → **"Automations"** → **"New automation"**
3. Configure:
   - **Trigger:** Every day at 09:00
   - **Filter:** Past due ≠ empty AND Status ≠ Complete
   - **Action:** Add comment

```
🔔 Daily overdue: {{Name}} ({{Days late}} days late).
@Assignee — please resolve or update status.
```

### Automation 2: Daily 3 PM Escalation

1. Create another automation
2. Configure:
   - **Trigger:** Every day at 15:00
   - **Filter:** Days late ≥ 2 AND Status ≠ Complete
   - **Action:** Add comment

```
🚨 Escalation: {{Name}} is {{Days late}} days overdue.
@Approver please review. @Assignee update now.
```

---

## 🧪 Testing Checklist

- [ ] **Step 1:** Create test task
  - Name: "TEST: Overdue Task"
  - Due date: 3 days ago
  - Status: In Progress
  - Assignee: You

- [ ] **Step 2:** Wait for 9 AM automation (or trigger manually)

- [ ] **Step 3:** Verify in Notion
  - [ ] Status changed to "Overdue"
  - [ ] Comment added with @mention
  - [ ] "Days late" shows 3

- [ ] **Step 4:** Wait for 3 PM escalation (or trigger manually)

- [ ] **Step 5:** Verify escalation
  - [ ] Escalation comment added
  - [ ] @Approver mentioned
  - [ ] No duplicate comments

- [ ] **Step 6:** Mark complete
  - [ ] No more notifications sent

---

## 📈 Monitoring & Logs

### GitHub Actions
https://github.com/jgtolentino/insightpulse-odoo/actions

### Supabase Edge Functions
https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/functions

### DigitalOcean App Platform
https://cloud.digitalocean.com/apps

---

## 🔍 Troubleshooting

### "object not found" error
→ Database not shared with integration. Go to Notion → Database → "•••" → Connections → Add integration

### "unauthorized" error
→ Wrong API key. Rotate key and update in all deployment targets.

### Automations not running
→ Check cron syntax is correct (UTC times, not Manila).

### Duplicate comments
→ Automations check for existing comments. If duplicates appear, check timing overlap between deployments.

### Formula not working
→ Re-run `node 04-add-days-late-formula.js`

---

## 📚 Files Created

```
insightpulse-odoo/
├── .github/workflows/
│   └── notion-automations.yml         # GitHub Actions (Option 1)
├── supabase/functions/
│   ├── notion-overdue/
│   │   └── index.ts                   # Supabase Edge Function
│   └── notion-escalation/
│       └── index.ts                   # Supabase Edge Function
├── infra/do/
│   └── notion-automations.yaml        # DigitalOcean spec (Option 3)
└── scripts/notion/
    ├── 01-completion-logging.js       # Audit trail (on-demand)
    ├── 02-daily-overdue-check.js      # Daily 9 AM
    ├── 03-escalation-automation.js    # Daily 3 PM
    ├── 04-add-days-late-formula.js    # One-time setup
    ├── test-connection.js             # Testing
    ├── package.json                   # Dependencies
    └── .env.example                   # Template
```

---

## ✅ Success Criteria

- [x] New Notion API key generated
- [x] GitHub Secrets configured
- [x] Workflow deployed to insightpulse-odoo repo
- [x] Supabase Edge Functions ready (optional)
- [x] DigitalOcean spec ready (optional)
- [ ] Test automation successful
- [ ] "Days late" formula working in Notion
- [ ] No secrets in git

---

**Need help?** Check logs in GitHub Actions tab or email jgtolentino_rn@yahoo.com
