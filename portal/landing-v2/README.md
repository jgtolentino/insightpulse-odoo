# InsightPulse AI Landing Page v2

Modern landing page built with Next.js 14, Ant Design 5, and Framer Motion, inspired by Claude's financial services page design.

## Features

- 🎨 **Ant Design 5** - Modern, customizable component library
- ⚡ **Next.js 14** - React framework with SSR and SSG
- 🎭 **Framer Motion** - Smooth animations and transitions
- 📱 **Responsive** - Mobile-first design
- 🎯 **SEO Optimized** - Meta tags, semantic HTML
- 🚀 **Performance** - Code splitting, lazy loading

## Design Highlights

### Inspired by Claude Financial Services Page

1. **Hero Section** with gradient background and real-time statistics
2. **Cost Savings Calculator** showing SaaS replacement value ($52.7k/year)
3. **Feature Cards** with icons and descriptions
4. **Compliance Section** with BIR-specific features
5. **Use Cases** with expandable accordions
6. **Call-to-Action** sections throughout

### Key Components

- **Navigation**: Sticky header with glassmorphism effect
- **Hero**: Animated text and live dashboard card
- **Statistics**: Real-time metrics (expenses, OCR accuracy, processing time)
- **Features**: 4-column grid with icons and descriptions
- **Compliance**: Gradient background with checklist items
- **Footer**: Multi-column layout with links

## Setup

### Prerequisites

- Node.js 18+ and npm
- Git

### Installation

```bash
# Navigate to the landing page directory
cd portal/landing-v2

# Install dependencies
npm install

# Run development server
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000)

### Build for Production

```bash
# Create optimized production build
npm run build

# Start production server
npm start
```

## Configuration

### Theme Customization

Edit `pages/_app.tsx` to customize Ant Design theme:

```typescript
const theme = {
  token: {
    colorPrimary: '#667eea',      // Primary brand color
    colorSuccess: '#52c41a',      // Success color
    borderRadius: 8,              // Global border radius
    fontFamily: '...',            // Font family
  },
};
```

### Content Updates

#### Hero Section
- Edit title, subtitle, and CTAs in `pages/index.tsx` (lines 61-100)
- Update statistics in the dashboard card (lines 150-180)

#### Cost Savings
- Update SaaS replacement data in the array (lines 210-220)
- Modify savings calculations

#### Features
- Edit feature cards array (lines 250-280)
- Add/remove features as needed

#### Compliance
- Update BIR compliance checklist (lines 320-360)
- Modify agency tags (line 380)

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy to Vercel
vercel --prod
```

### DigitalOcean App Platform

1. Create new app in DigitalOcean dashboard
2. Connect GitHub repository
3. Set build command: `cd portal/landing-v2 && npm run build`
4. Set output directory: `portal/landing-v2/.next`
5. Deploy

### Docker

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

## Design System

### Colors

- **Primary**: `#667eea` (Purple gradient start)
- **Secondary**: `#764ba2` (Purple gradient end)
- **Success**: `#52c41a` (Green for positive metrics)
- **Info**: `#1890ff` (Blue for informational elements)

### Typography

- **Headings**: Bold, tracking-tight
- **Body**: 16px, line-height 1.6
- **Small**: 14px for captions and labels

### Spacing

- Section padding: 80-100px vertical
- Card gaps: 24-32px
- Component spacing: 16-24px

## Performance

- **Lighthouse Score**: 90+ (target)
- **First Contentful Paint**: <1.5s
- **Time to Interactive**: <3s
- **Bundle Size**: <300KB (gzipped)

## Analytics Integration

Add Google Analytics or other tracking:

```typescript
// pages/_app.tsx
import Script from 'next/script';

<Script
  src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"
  strategy="afterInteractive"
/>
```

## Accessibility

- ARIA labels on all interactive elements
- Keyboard navigation support
- Color contrast ratio >4.5:1
- Screen reader compatible

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

LGPL-3.0 (matching main project license)

## Support

- Documentation: https://jgtolentino.github.io/insightpulse-odoo/
- GitHub: https://github.com/jgtolentino/insightpulse-odoo
- Status: https://insightpulseai.net
