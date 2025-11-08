# ChatGPT Custom GPT Configuration

## Step 1: Create Custom GPT

Go to ChatGPT → **Explore GPTs** → **Create a GPT**

### Name
```
InsightPulse FinServ Assistant
```

### Description
```
AI assistant for InsightPulse FinServ operations: month-end close, expense management, policy Q&A, and Odoo ERP queries.
```

### Instructions
```
You are the InsightPulse FinServ Assistant, an AI agent with access to:

1. **Month-End Close Operations**
   - Get close status for all 8 agencies (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
   - View detailed checklists with task status
   - Track exceptions and blockers
   - Analyze close cycle metrics

2. **Policy & Compliance Q&A**
   - Answer questions about company policies, SOPs, and procedures
   - Search policy documents with semantic search
   - Provide citations for all answers
   - Cover accounting, finance, HR, procurement, and BIR compliance

3. **Odoo ERP Operations**
   - Query sale orders, invoices, expenses
   - List and filter expense reports
   - Create project tasks
   - Search customers/vendors

**Response Style**:
- Be concise and structured
- Use bullet points and tables when appropriate
- Always cite policy sources when answering compliance questions
- Include relevant links to Odoo records
- For close operations, highlight exceptions and blockers

**Security**:
- Never expose API keys or credentials
- Respect user permissions (some data may be agency-specific)
- Flag critical compliance issues immediately

When users ask about:
- "Close status" → Use the Close Operations API
- "Policy on..." → Use Policy QA API with citations
- "Expense EXP-001" → Use Odoo Expenses API
- "Create task..." → Use Tasks API

Always provide actionable insights, not just data dumps.
```

---

## Step 2: Configure Actions

Click **Configure** → **Actions** → **Create new action**

### Schema
Import the OpenAPI schema:

**URL**: `https://api.insightpulseai.net/.well-known/openapi.yaml`

or paste the content from `openapi.yaml`

### Authentication

**Type**: API Key

**API Key**:
- Header Name: `X-API-Key`
- Value: `gpt-xxxxxxxxxxxxxxxxxxxxxxxxxx` (from your .env)

---

## Step 3: Privacy Settings

- **Who can access**: Only you (or Anyone with link for team access)
- **Web browsing**: Off
- **DALL-E**: Off
- **Code Interpreter**: On (for data analysis)

---

## Step 4: Test the GPT

### Test Query 1: Close Status
```
What's the month-end close status for all agencies?
```

Expected: Uses `GET /api/close/status` and returns structured status for all 8 agencies

### Test Query 2: Policy QA
```
What's our policy on expense approval thresholds?
```

Expected: Uses `POST /api/policy/qa` and returns answer with citations

### Test Query 3: Expense Lookup
```
Show me pending expenses for agency RIM
```

Expected: Uses `GET /api/expenses?agency_code=RIM&state=reported`

### Test Query 4: Create Task
```
Create a task: "Review Q4 accruals for CKVC" assigned to user ID 5
```

Expected: Uses `POST /api/tasks` and creates task in Odoo

---

## Step 5: Publish

Click **Publish** → **Only me** (or share link with team)

---

## Usage Examples

Once configured, you can ask:

**Close Operations**:
- "What's the close status for RIM this month?"
- "Show me the close checklist for CKVC for 2025-01"
- "Are there any critical close exceptions?"
- "What's our average close cycle time?"

**Policy Q&A**:
- "What's the policy on travel expense reimbursement?"
- "What are the BIR deadlines for Q1 2025?"
- "Who approves POs above ₱100,000?"
- "What's the D+3 accrual cutoff SLA?"

**Odoo Operations**:
- "Show me sale order SO001"
- "List all overdue invoices"
- "Get expense EXP-2025-00042 details"
- "Create a task: 'Review vendor contracts' for Project 12"

**Multi-step Analysis**:
- "Analyze close cycle trends for the last 6 months and suggest improvements"
- "Which agency has the most close exceptions? What are the top 3 issues?"
- "Compare expense approval rates across all 8 agencies"

---

## Troubleshooting

### Actions not appearing
- Check that `api.insightpulseai.net` is accessible
- Verify API key is correct
- Check OpenAPI schema is valid

### Authentication errors
- Verify `X-API-Key` header is set correctly
- Check API key has correct prefix in .env
- Test endpoint directly: `curl -H "X-API-Key: xxx" https://api.insightpulseai.net/health`

### Slow responses
- Some operations (policy QA with RAG) may take 5-15 seconds
- ChatGPT has a 45-second timeout for action calls
- Consider breaking complex queries into smaller parts

---

## Advanced: Team Deployment

To share with your finance team:

1. **Publish GPT** → "Anyone with link"
2. **Share link** via Slack/Mattermost
3. **Set up team API key** (different from personal key)
4. **Monitor usage** via n8n analytics workflow

---

## Security Notes

- API key grants **full access** to all operations
- Consider creating **read-only API keys** for team members
- Rotate API keys quarterly
- Monitor API access logs in Supabase
- Never share your GPT link publicly

---

**Result**: Your Custom GPT now has direct access to your entire FinServ stack!
