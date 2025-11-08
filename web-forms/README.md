# Feature Request System - Web Forms

Simplified feature request system using Notion (alternative to Odoo community form).

## 📦 Components

### 1. HTML Form
**File**: `feature-request-form.html`

Beautiful, responsive form built with Tailwind CSS.

**Features**:
- ✅ Mobile-friendly responsive design
- ✅ Real-time validation
- ✅ Success/error messages
- ✅ Character limits
- ✅ Clean, professional UI

**Deployment**:
```bash
# Deploy to static hosting (Vercel, Netlify, GitHub Pages, etc.)
cp feature-request-form.html /your-static-site/feature-request.html
```

**Embed in Existing Site**:
```html
<!-- Add to your landing page -->
<iframe
  src="https://your-site.com/feature-request.html"
  width="100%"
  height="800px"
  frameborder="0"
></iframe>
```

---

### 2. Serverless API
**File**: `api/submit-feature-request.ts`

Edge function that receives form submissions and creates Notion pages.

**Tech Stack**:
- TypeScript
- Vercel Edge Runtime (or Netlify/Cloudflare Workers)
- Notion API

**Setup**:

```bash
# Install dependencies
npm install @notionhq/client

# Deploy to Vercel
vercel --prod

# Set environment variables
vercel env add NOTION_API_TOKEN
vercel env add NOTION_FEATURE_DB_ID
```

**Update Form**:

In `feature-request-form.html`, update line ~305:

```javascript
// Change this:
// const response = { ok: true }; // Simulated success

// To this:
const response = await fetch('/api/submit-feature-request', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
});
```

---

## 🚀 Quick Start

### Option 1: Local Testing (Python Script)
```bash
# Set environment variables
export NOTION_API_TOKEN="secret_xxx"
export NOTION_FEATURE_DB_ID="db_xxx"

# Submit via interactive CLI
python ../scripts/submit_feature_request.py interactive
```

### Option 2: Deploy Web Form

**Step 1: Set Up Notion Database**
```bash
cd ../scripts
python setup_feature_request_db.py --parent-page-id <your_page_id>
```

**Step 2: Deploy Serverless Function**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd ../web-forms
vercel --prod

# Configure environment
vercel env add NOTION_API_TOKEN
vercel env add NOTION_FEATURE_DB_ID
```

**Step 3: Update Form URL**
```javascript
// In feature-request-form.html, update API endpoint:
const response = await fetch('https://your-project.vercel.app/api/submit-feature-request', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
});
```

**Step 4: Deploy Form**
```bash
# Deploy HTML form to Vercel
vercel --prod

# Or use any static hosting:
# - Netlify
# - GitHub Pages
# - Cloudflare Pages
# - AWS S3 + CloudFront
```

---

## 📋 Alternative: Tally.so Integration

For a no-code option, use Tally.so (free tier available):

**Step 1: Create Tally Form**
1. Go to https://tally.so
2. Create new form with fields:
   - Title (short text)
   - Category (dropdown)
   - Use Case (long text)
   - Priority (dropdown)
   - Email (email)
   - Solution (long text, optional)
   - Tags (short text, optional)

**Step 2: Connect to Notion**
1. In Tally form settings → Integrations
2. Add Notion integration
3. Map form fields to Notion database properties
4. Test submission

**Step 3: Embed**
```html
<!-- Add to your website -->
<iframe
  src="https://tally.so/r/YOUR_FORM_ID"
  width="100%"
  height="800px"
  frameborder="0"
></iframe>
```

**Pros**:
- ✅ No code required
- ✅ Built-in Notion integration
- ✅ Free tier available
- ✅ Spam protection
- ✅ Mobile-optimized

**Cons**:
- ❌ Less customization
- ❌ Tally branding (free tier)
- ❌ Data goes through third party

---

## 📊 Comparison

| Method | Complexity | Cost | Customization | Recommended For |
|--------|------------|------|---------------|-----------------|
| **Python CLI** | Low | Free | Medium | Internal teams |
| **Web Form + Vercel** | Medium | Free (hobby tier) | High | Public-facing |
| **Tally.so** | Very Low | Free/Paid | Low | Quick setup |

---

## 🔒 Security Considerations

### Environment Variables
**Never commit**:
- NOTION_API_TOKEN
- NOTION_FEATURE_DB_ID

**Use**:
- `.env` files (gitignored)
- Vercel Environment Variables
- Secret managers (AWS Secrets Manager, Vault)

### Rate Limiting
Add rate limiting to prevent abuse:

```typescript
// In submit-feature-request.ts
import rateLimit from '@/lib/rate-limit';

const limiter = rateLimit({
  interval: 60 * 1000, // 1 minute
  uniqueTokenPerInterval: 500
});

export default async function handler(req: Request) {
  try {
    await limiter.check(req, 5, 'FEATURE_REQUEST'); // 5 requests per minute
  } catch {
    return new Response('Rate limit exceeded', { status: 429 });
  }

  // ... rest of handler
}
```

### CORS
Configure allowed origins:

```typescript
const headers = {
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': 'https://insightpulseai.net', // Only your domain
  'Access-Control-Allow-Methods': 'POST',
  'Access-Control-Allow-Headers': 'Content-Type'
};
```

---

## 📖 Documentation

See main documentation:
- [Feature Request System Overview](../docs/NOTION_FEATURE_REQUEST_SYSTEM.md)
- [Python Submission Script](../scripts/submit_feature_request.py)
- [Database Setup](../scripts/setup_feature_request_db.py)

---

## 🤝 Contributing

Have suggestions for the feature request system? Submit a feature request! 😉

---

**Version**: 1.0.0
**Last Updated**: 2025-11-08
