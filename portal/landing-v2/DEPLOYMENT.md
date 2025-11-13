# InsightPulse AI Landing Page - Deployment Guide

## Overview

Professional landing page built with Next.js 14 and Ant Design 5, inspired by Claude's financial services page design. Optimized for Finance SSC value proposition, BIR compliance messaging, and multi-agency operations.

## Quick Start

```bash
# Navigate to directory
cd /Users/tbwa/insightpulse-odoo/portal/landing-v2

# Install dependencies
npm install

# Run development server
npm run dev

# Visit http://localhost:3000
```

## Design Features Implemented

### 1. Hero Section ✅
- **Inspired by**: Claude financial services hero
- **Features**:
  - Gradient text effect for "AI-Powered Automation"
  - Animated entrance with Framer Motion
  - Live statistics card showing real-time metrics
  - Dual CTA buttons (primary + secondary)
  - Trust indicators below CTAs

### 2. Cost Savings Calculator ✅
- **$52,700 Annual Savings** displayed prominently
- 5 SaaS replacement cards:
  - SAP Concur → Odoo Expense ($15k)
  - SAP Ariba → Odoo Procurement ($12k)
  - Tableau → Apache Superset ($8.4k)
  - Slack Enterprise → Mattermost ($12.6k)
  - Odoo Enterprise → Odoo CE + OCA ($4.7k)

### 3. Features Grid ✅
- **4-column layout** with icons
- Focus areas:
  - BIR Compliance (Forms 1601-C, 1702-RT, 2550Q)
  - Multi-Tenant (8 agencies: RIM, CKVC, BOM, etc.)
  - Analytics & BI (Superset dashboards)
  - Cloud Native (DigitalOcean, Supabase)

### 4. Compliance Section ✅
- **Gradient background** (purple to violet)
- **Checklist items**:
  - Immutable records
  - Automated tax forms
  - E-invoice ready
- **Live metrics card** showing monthly processing volume

### 5. Use Cases Accordion ✅
- **4 expandable sections**:
  - OCR-Powered Expense Automation
  - Multi-Agency Procurement
  - Analytics & Business Intelligence
  - Month-End Closing Automation

### 6. Multiple CTAs ✅
- Hero section: "Start Free Trial" + "Book Demo"
- Footer section: "Start Free Trial" + "Schedule Demo"
- Compliance section: Links to security and FAQ

## Technical Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Next.js | 14.0.4 |
| UI Library | Ant Design | 5.12.0 |
| Animation | Framer Motion | 10.16.16 |
| Icons | Ant Design Icons | 5.2.6 |
| Language | TypeScript | 5.3.3 |

## Performance Targets

- **Lighthouse Score**: 90+ (all categories)
- **First Contentful Paint**: <1.5s
- **Time to Interactive**: <3s
- **Bundle Size**: <300KB (gzipped)

## Deployment Options

### Option 1: Vercel (Recommended)

**Pros**:
- Zero-config deployment
- Automatic SSL
- Global CDN
- Preview deployments for PRs

**Steps**:
```bash
npm i -g vercel
vercel --prod
```

**Expected URL**: `insightpulse-landing.vercel.app`

### Option 2: DigitalOcean App Platform

**Pros**:
- Integrated with existing infrastructure
- Direct PostgreSQL access
- Private networking

**Configuration**:
```yaml
name: insightpulse-landing
region: sfo
services:
  - name: web
    source_dir: /portal/landing-v2
    build_command: npm run build
    run_command: npm start
    http_port: 3000
    instance_size_slug: basic-xxs
    instance_count: 1
    routes:
      - path: /
```

**Cost**: ~$5/month (basic-xxs)

### Option 3: Docker Container

**Dockerfile**:
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

**Deploy**:
```bash
docker build -t insightpulse-landing .
docker run -p 3000:3000 insightpulse-landing
```

## Environment Variables

Create `.env.local` file:

```env
# Analytics
NEXT_PUBLIC_GA_MEASUREMENT_ID=G-XXXXXXXXXX

# API Endpoints
NEXT_PUBLIC_API_URL=https://insightpulseai.net/api

# Feature Flags
NEXT_PUBLIC_ENABLE_DEMO=true
```

## Content Management

### Update Hero Section

File: `pages/index.tsx` (lines 61-100)

```typescript
<Title level={1}>
  Transform Finance SSC with{' '}
  <span style={{ /* gradient */ }}>
    YOUR_NEW_HEADLINE
  </span>
</Title>
```

### Update Cost Savings

File: `pages/index.tsx` (lines 210-220)

```typescript
const saasReplacements = [
  { name: 'OLD_TOOL', replacement: 'NEW_TOOL', savings: '$X,XXX' },
  // Add more...
];
```

### Update Statistics

File: `pages/index.tsx` (lines 150-180)

```typescript
<Statistic
  title="Your Metric"
  value={1234}
  suffix="unit"
/>
```

## SEO Configuration

### Meta Tags

Already included in `pages/index.tsx`:

```typescript
<Head>
  <title>InsightPulse AI | Transform Finance SSC</title>
  <meta name="description" content="Multi-tenant, BIR-compliant..." />
</Head>
```

### Open Graph Tags (Add)

```typescript
<meta property="og:title" content="InsightPulse AI" />
<meta property="og:description" content="Save $52.7k/year..." />
<meta property="og:image" content="/og-image.png" />
<meta property="og:url" content="https://insightpulseai.net" />
```

## Analytics Setup

### Google Analytics

1. Create GA4 property
2. Add tracking code to `pages/_app.tsx`:

```typescript
import Script from 'next/script';

// In _app.tsx
<Script
  src={`https://www.googletagmanager.com/gtag/js?id=${GA_ID}`}
  strategy="afterInteractive"
/>
```

### Event Tracking

```typescript
// Track CTA clicks
const handleCTAClick = () => {
  gtag('event', 'cta_click', {
    cta_location: 'hero',
    cta_text: 'Start Free Trial',
  });
};
```

## Testing Checklist

### Visual Testing
- [ ] Hero section displays correctly on mobile, tablet, desktop
- [ ] Cost savings cards are responsive
- [ ] Feature grid adapts to screen sizes
- [ ] Compliance section gradient renders properly
- [ ] Accordion animations work smoothly

### Functional Testing
- [ ] All CTAs link to correct destinations
- [ ] Navigation menu works on mobile
- [ ] Accordion panels expand/collapse
- [ ] Footer links are functional
- [ ] Forms (if any) submit correctly

### Performance Testing
- [ ] Run Lighthouse audit (target: 90+)
- [ ] Check bundle size (<300KB)
- [ ] Test on 3G network
- [ ] Verify lazy loading works
- [ ] Check Core Web Vitals

### Cross-Browser Testing
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile browsers (iOS Safari, Chrome Android)

## Monitoring

### Add to monitoring dashboard

```yaml
endpoint: https://insightpulseai.net/
health_check: /api/health
alert_threshold: 99.9% uptime
response_time_p95: <3s
```

## Troubleshooting

### Issue: Build fails with "Module not found"

**Solution**:
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Issue: Ant Design styles not loading

**Solution**: Ensure `_app.tsx` imports reset CSS:
```typescript
import 'antd/dist/reset.css';
```

### Issue: Framer Motion animations not working

**Solution**: Check that `framer-motion` is installed:
```bash
npm install framer-motion@latest
```

## Next Steps

1. **Deploy to staging**: Test on actual domain
2. **A/B testing**: Test different CTAs and headlines
3. **Add analytics**: Track conversions and user behavior
4. **SEO optimization**: Submit sitemap, add structured data
5. **Performance tuning**: Optimize images, enable caching

## Support

- **Documentation**: `/portal/landing-v2/README.md`
- **GitHub**: https://github.com/jgtolentino/insightpulse-odoo
- **Status Page**: https://insightpulseai.net

## Version History

- **v1.0.0** (2025-11-12): Initial release
  - Next.js 14 + Ant Design 5
  - Claude-inspired design
  - Finance SSC focus
  - BIR compliance messaging
